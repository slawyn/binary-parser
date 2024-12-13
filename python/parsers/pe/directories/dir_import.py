from packer import Packer
import utils
from parsers.pe.directories.shared import ImportObject


class ImportDirectoryTable(Packer):
    IDT_ILT_RVA_SZ = 4
    IDT_TIMESTAMP_SZ = 4
    IDT_FORWARDER_CHAIN_SZ = 4
    IDT_NAME_RVA_SZ = 4
    IDT_IAT_RVA_SZ = 4

    def __init__(self, ILTRVA=0, timestamp=0, forwarder_chain=0, name_rva=0, IATRVA=0):
        super().__init__(
            {
                "idt_ilt_rva": ILTRVA,
                "idt_timestamp": timestamp,
                "idt_forwarder_chain": forwarder_chain,
                "idt_name_rva": name_rva,
                "idt_iat_rva": IATRVA
            },
            always_32bit=True
        )
        self.importObjects = []
        self.nameOfDLL = ""

    def set_dll_name(self, name):
        self.nameOfDLL = name

    def get_dll_name(self):
        return self.nameOfDLL

    def is_empty(self):
        return self.members["idt_ilt_rva"] | self.members["idt_timestamp"] | self.members["idt_forwarder_chain"] | self.members["idt_name_rva"] | self.members["idt_iat_rva"] == 0

    def get_ilt_rva(self):
        return self.members["idt_ilt_rva"]

    def get_iat_rva(self):
        return self.members["idt_iat_rva"]

    def get_name_rva(self):
        return self.members["idt_name_rva"]

    def get_forwarder_chain(self):
        return self.members["idt_forwarder_chain"]

    def set_import_objects(self, io):
        self.importObjects = io

    def get_import_objects(self):
        return self.importObjects

    def __str__(self):
        out = ""
        out += utils.formatter("DLL:", self.nameOfDLL)
        out += utils.formatter("ILTRVA:", self.members["idt_ilt_rva"])
        out += utils.formatter("TimeStamp:", self.members["idt_timestamp"])
        out += utils.formatter("ForwarderChain:", self.members["idt_forwarder_chain"], hex=True)
        out += utils.formatter("NameRVA:", self.members["idt_name_rva"])
        out += utils.formatter("IATRVA:", self.members["idt_iat_rva"])
        return out


class ImportTable:
    IMPORT_BY_ORDINAL_64BIT = 0x8000000000000000
    IMPORT_BY_ORDINAL_32BIT = 0x80000000

    def __init__(self, data, tables_fileoffset, sections, mode64):
        self.import_directory_tables = []
        i = 0
        while True:
            import_directory_table = ImportDirectoryTable()
            import_directory_table.unpack(data[tables_fileoffset+20*i:])

            if import_directory_table.is_empty():
                break

            nameoffset = utils.convert_rva_to_offset(import_directory_table.get_name_rva(), sections)
            import_directory_table.set_dll_name(utils.readstring(data, nameoffset))
            self.import_directory_tables.append(import_directory_table)

            # Sometimes ILT is empty, but the content of ILT and IAT is the same
            # and changes only after loading
            iltrva = import_directory_table.get_ilt_rva()
            if iltrva > 0:
                offsetILT = utils.convert_rva_to_offset(iltrva, sections)
            else:
                offsetILT = utils.convert_rva_to_offset(import_directory_table.get_iat_rva(), sections)

            # parse imported itemslist
            j = 0
            importObjects = []
            while True:
                iltentry = 0
                importbyordinal = 0
                nametableoffset = 0
                iatrva = 0
                value = 0
                if mode64:
                    iltentry = utils.unpack(data[offsetILT+j*8:offsetILT+j*8+8])
                    importbyordinal = iltentry & ImportTable.IMPORT_BY_ORDINAL_64BIT
                    iatrva = import_directory_table.get_iat_rva()+j*8
                    valueoffset = utils.convert_rva_to_offset(iatrva, sections)
                    value = utils.unpack(data[valueoffset:valueoffset+8])

                else:
                    iltentry = utils.unpack(data[offsetILT+j*4:offsetILT+j*4+4])
                    importbyordinal = iltentry & ImportTable.IMPORT_BY_ORDINAL_32BIT
                    iatrva = import_directory_table.get_iat_rva()+j*4
                    valueoffset = utils.convert_rva_to_offset(iatrva, sections)
                    value = utils.unpack(data[valueoffset:valueoffset+4])

                if iltentry == 0:  # last entry for this .dll
                    break

                # we have a forwarder:this is undocumented
                forwarder_chain = import_directory_table.get_forwarder_chain()
                if forwarder_chain != 0 and forwarder_chain != -1:
                    forwarderstringoffset = utils.convert_rva_to_offset(iltentry, sections)
                    forwarderstring = utils.readstring(data, forwarderstringoffset)

                    # since we have a  forwarder set it to forwarderchain
                    importObjects.append(ImportObject(iatrva, 0, 0, forwarderstring, forwarder_chain, value))

                # import by ordinal
                elif importbyordinal:
                    importObjects.append(ImportObject(iatrva, iltentry & 0xFFFF, 0, 0, "", 0, value))

                # import by name
                else:
                    nametableoffset = utils.convert_rva_to_offset((iltentry & 0x7FFFFFFF), sections)
                    hint = utils.unpack(data[nametableoffset:nametableoffset+2])
                    name = utils.readstring(data, nametableoffset+2)
                    importObjects.append(ImportObject(iatrva, 0, (iltentry & 0x7FFFFFFF), hint, name, 0, value))

                j += 1
                import_directory_table.set_import_objects(importObjects)
            i += 1

    def get_import_directory_tables(self):
        return self.import_directory_tables

    def get_number_of_dlls(self):
        return len(self.import_directory_tables)
