from packer import Packer
import utils
from parsers.pe.directories.shared import ImportObject
from parsers.pe.directories.shared import Table


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
        self.importobjects = []
        self.dll_name = ""

    def set_dll_name(self, name):
        self.dll_name = name

    def get_dll_name(self):
        return self.dll_name

    def set_import_objects(self, did_import_objects):
        self.importobjects = did_import_objects

    def get_import_objects(self):
        return self.importobjects

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

    @staticmethod
    def get_column_titles():
        out = ""
        out += utils.formatter2("%-20s", "[Attributes]")
        out += utils.formatter2("%-20s", "[NameRVA]")
        out += utils.formatter2("%-20s", "[ModuleHandle]")
        out += utils.formatter2("%-20s", "[ModuleHandle]")
        out += utils.formatter2("%-20s", "[DelayIAT]")
        out += utils.formatter2("%-20s", "[DelayINT]")
        out += utils.formatter2("%-20s", "[BoundDelayImportTable]")
        out += utils.formatter2("%-20s", "[UnloadDelayImportTable]")
        out += utils.formatter2("%-20s", "[TimeStamp]")
        out += utils.formatter2("%-20s", "[DLL]")
        return out

    def __str__(self):
        out = ""
        out += utils.formatter2("%-20x",  self.members["did_attributes"])
        out += utils.formatter2("%-20x",  self.members["did_name_rva"])
        out += utils.formatter2("%-20x",  self.members["did_module_handle"])
        out += utils.formatter2("%-20x",  self.members["did_delay_iat"])
        out += utils.formatter2("%-20x",  self.members["did_delay_int"])
        out += utils.formatter2("%-20x",  self.members["did_bound_delay_import_table"])
        out += utils.formatter2("%-20x",  self.members["did_unload_delay_import_table"])
        out += utils.formatter2("%-20x",  self.members["did_timestamp"])
        out += utils.formatter2("%-20s",  self.dll_name)
        return out


class DelayImportTable(Table):
    def __init__(self):
        self.import_directory_tables = []

    def unpack(self, buffer):
        offset = self.offset
        sections = self.sections
        is_64bit = Packer.is_64bit
        i = 0
        while True:
            did = DelayImportDescriptor()
            did.unpack(buffer[offset+32*i:])
            if did.is_empty():
                break

            nameoffset = utils.convert_rva_to_offset(did.get_name_rva(), sections)
            did.set_dll_name(utils.readstring(buffer, nameoffset))

            self.import_directory_tables.append(did)

            j = 0
            namesoffset = utils.convert_rva_to_offset(did.get_delay_int(), sections)
            importObjects = []
            importObjectsappend = importObjects.append

            delayIAT = did.get_delay_iat()
            delayimportdescriptor = self.import_directory_tables[i]

            while True:
                intentry = 0
                iatrva = 0
                importbyordinal = 0
                value = 0
                if is_64bit:
                    intentry = utils.unpack(buffer[namesoffset+8*j:namesoffset+8*j+8])
                    # is the import by ordinal bit set?
                    importbyordinal = intentry & 0x8000000000000000
                    iatrva = delayIAT+j*8
                    valueoffset = utils.convert_rva_to_offset(iatrva, sections)
                    value = utils.unpack(buffer[valueoffset:valueoffset+8])
                else:
                    intentry = utils.unpack(buffer[namesoffset+4*j:namesoffset+4*j+4])
                    importbyordinal = intentry & 0x80000000  # same as above. but for 32 bit PE
                    iatrva = delayIAT+j*4
                    valueoffset = utils.convert_rva_to_offset(iatrva, sections)
                    value = utils.unpack(buffer[valueoffset:valueoffset+4])

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
                    hint = utils.unpack(buffer[nametableoffset:nametableoffset+2])  # read hint
                    name = utils.readstring(buffer, nametableoffset+2)
                    importObjectsappend(ImportObject(
                        iatrva, 0, (intentry & 0x7FFFFFFF), hint, name, 0, value))
                j = j+1

            delayimportdescriptor.set_import_objects(importObjects)
            delayimportdescriptor.numberOfImportObjects = j
            i = i+1

    def get_import_directory_tables(self):
        return self.import_directory_tables

    def __str__(self):
        out = f"\n[DelayImports]({len(self.import_directory_tables)})\n"
        out += f"{DelayImportDescriptor.get_column_titles()}\n"
        for table in self.import_directory_tables:
            out += str(table)
            out += "\n"

        for table in self.import_directory_tables:
            out += f"\n[{table.get_dll_name()}]({len(table.get_import_objects())})\n"
            out += f"{ImportObject.get_column_titles()}\n"
            for object in table.get_import_objects():
                out += str(object)
                out += "\n"

        return out
