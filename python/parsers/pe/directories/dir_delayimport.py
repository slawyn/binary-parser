from packer import Packer
import utils
from parsers.pe.directories.shared import ImportObject


class DelayImportDescriptor(Packer):
    DID_ATTRIBUTES_SZ = 4
    DID_NAME_RVA_SZ = 4
    DID_MODULE_HANDLE_SZ = 4
    DID_DELAY_IAT_SZ = 4
    DID_DELAY_INT_SZ = 4
    DID_BOUND_DELAY_IMPORT_TABLE_SZ = 4
    DID_UNLOAD_DELAY_IMPORT_TABLE_SZ = 4
    DID_TIMESTAMP_SZ = 4

    def __init__(
        self, did_attributes=0,
        did_name_rva=0,
        did_module_handle=0,
        did_delay_iat=0,
        did_delay_int=0,
        did_bound_delay_import_table=0,
        did_unload_delay_import_table=0,
        did_timestamp=0
    ):
        super().__init__(
            {
                "did_attributes": did_attributes,
                "did_name_rva": did_name_rva,
                "did_module_handle": did_module_handle,
                "did_delay_iat": did_delay_iat,
                "did_delay_int": did_delay_int,
                "did_bound_delay_import_table": did_bound_delay_import_table,
                "did_unload_delay_import_table": did_unload_delay_import_table,
                "did_timestamp": did_timestamp
            },
            always_32bit=True
        )
        self.did_importObjects = []
        self.dll_name = ""

    def set_dll_name(self, name):
        self.dll_name = name

    def get_dll_name(self):
        return self.dll_name

    def set_import_objects(self, did_import_objects):
        self.did_importObjects = did_import_objects

    def get_import_objects(self):
        return self.did_importObjects

    def is_empty(self):
        return all(value == 0 for value in self.members.values())

    def get_attributes(self):
        return self.members["did_attributes"]

    def get_name_rva(self):
        return self.members["did_name_rva"]

    def get_module_handle(self):
        return self.members["did_module_handle"]

    def get_delay_iat(self):
        return self.members["did_delay_iat"]

    def get_delay_int(self):
        return self.members["did_delay_int"]

    def get_bound_delay_import_table(self):
        return self.members["did_bound_delay_import_table"]

    def get_unload_delay_import_table(self):
        return self.members["did_unload_delay_import_table"]

    def get_timestamp(self):
        return self.members["did_timestamp"]

    def is_empty(self):
        return self.members["did_attributes"] | self.members["did_name_rva"] | self.members["did_module_handle"] | self.members["did_delay_iat"] | self.members["did_delay_int"] | self.members["did_bound_delay_import_table"] | self.members["did_unload_delay_import_table"] | self.members["did_timestamp"] == 0

    def __str__(self):
        out = ""
        out += utils.formatter("DLL:", self.dll_name)
        out += utils.formatter("Attributes:", self.members["did_attributes"])
        out += utils.formatter("NameRVA:", self.members["did_name_rva"])
        out += utils.formatter("ModuleHandle:", self.members["did_module_handle"])
        out += utils.formatter("DelayIAT:", self.members["did_delay_iat"])
        out += utils.formatter("DelayINT:", self.members["did_delay_int"])
        out += utils.formatter("BoundDelayImportTable:", self.members["did_bound_delay_import_table"])
        out += utils.formatter("UnloadDelayImportTable:", self.members["did_unload_delay_import_table"])
        out += utils.formatter("TimeStamp:", self.members["did_timestamp"])
        return out


class DelayImportTable:
    def __init__(self, data, tables_fileoffset, sections, mode64):
        self.import_directory_tables = []

        i = 0
        while True:
            delaytable = DelayImportDescriptor()
            delaytable.unpack(data[tables_fileoffset+32*i:])
            if delaytable.is_empty():
                break

            nameoffset = utils.convert_rva_to_offset(delaytable.get_name_rva(), sections)
            delaytable.set_dll_name(utils.readstring(data, nameoffset))

            self.import_directory_tables.append(delaytable)

            j = 0
            namesoffset = utils.convert_rva_to_offset(delaytable.get_delay_int(), sections)
            importObjects = []
            importObjectsappend = importObjects.append

            delayIAT = delaytable.get_delay_iat()
            delayimportdescriptor = self.import_directory_tables[i]

            while True:
                intentry = 0
                iatrva = 0
                importbyordinal = 0
                value = 0
                if mode64:
                    intentry = utils.unpack(data[namesoffset+8*j:namesoffset+8*j+8])
                    # is the import by ordinal bit set?
                    importbyordinal = intentry & 0x8000000000000000
                    iatrva = delayIAT+j*8
                    valueoffset = utils.convert_rva_to_offset(iatrva, sections)
                    value = utils.unpack(data[valueoffset:valueoffset+8])
                else:
                    intentry = utils.unpack(data[namesoffset+4*j:namesoffset+4*j+4])
                    importbyordinal = intentry & 0x80000000  # same as above. but for 32 bit PE
                    iatrva = delayIAT+j*4
                    valueoffset = utils.convert_rva_to_offset(iatrva, sections)
                    value = utils.unpack(data[valueoffset:valueoffset+4])

                if intentry == 0:
                    break

                # import by ordinal
                if importbyordinal:
                    importObjectsappend(ImportObject(
                        iatrva, intentry & 0xFFFF, 0, 0, "", 0, value))  # no hint no name

                # import by name
                else:
                    nametableoffset = utils.convert_rva_to_offset(
                        (intentry & 0x7FFFFFFF), sections)
                    hint = utils.unpack(data[nametableoffset:nametableoffset+2])  # read hint
                    name = utils.readstring(data, nametableoffset+2)
                    importObjectsappend(ImportObject(
                        iatrva, 0, (intentry & 0x7FFFFFFF), hint, name, 0, value))
                j = j+1

            delayimportdescriptor.importObjects = importObjects
            delayimportdescriptor.numberOfImportObjects = j
            i = i+1


def get_import_directory_tables(self):
    return self.import_directory_tables


def get_number_of_dlls(self):
    return len(self.import_directory_tables)
