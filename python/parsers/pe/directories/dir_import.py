from packer import Packer
import utils
from parsers.pe.directories.shared import ImportObject
from parsers.pe.directories.shared import Table


class ImportDirectoryTable(Packer):

    def __init__(self):
        super().__init__(
            {
                "idt_ilt_rva": 4,
                "idt_timestamp": 4,
                "idt_forwarder_chain": 4,
                "idt_name_rva": 4,
                "idt_iat_rva": 4
            },
            always_32bit=True
        )
        self.importObjects = []
        self.dll_name = ""

    def set_dll_name(self, name):
        self.dll_name = name

    def get_dll_name(self):
        return self.dll_name

    def is_empty(self):
        return (
            self.get_value("idt_ilt_rva")
            | self.get_value("idt_timestamp")
            | self.get_value("idt_forwarder_chain")
            | self.get_value("idt_name_rva")
            | self.get_value("idt_iat_rva")
        ) == 0

    def get_ilt_rva(self):
        return self.get_value("idt_ilt_rva")

    def get_iat_rva(self):
        return self.get_value("idt_iat_rva")

    def get_name_rva(self):
        return self.get_value("idt_name_rva")

    def get_forwarder_chain(self):
        return self.get_value("idt_forwarder_chain")

    def set_import_objects(self, io):
        self.importObjects = io

    def get_import_objects(self):
        return self.importObjects

    @staticmethod
    def get_column_titles():
        out = ""
        out += utils.formatter2("%-20s", "[ILTRVA]")
        out += utils.formatter2("%-20s", "[TimeStamp]")
        out += utils.formatter2("%-20s", "[ForwarderChain]")
        out += utils.formatter2("%-20s", "[NameRVA]")
        out += utils.formatter2("%-20s", "[IATRVA]")
        out += utils.formatter2("%-20s", "[DLL]")
        return out

    def __str__(self):
        out = ""
        out += utils.formatter2("%-20x",  self.get_value("idt_ilt_rva"))
        out += utils.formatter2("%-20x",  self.get_value("idt_timestamp"))
        out += utils.formatter2("%-20x",  self.get_value("idt_forwarder_chain"))
        out += utils.formatter2("%-20x",  self.get_value("idt_name_rva"))
        out += utils.formatter2("%-20x",  self.get_value("idt_iat_rva"))
        out += utils.formatter2("%-20s",  self.dll_name)
        return out


class ImportTable(Table):
    IMPORT_BY_ORDINAL_64BIT = 0x8000000000000000
    IMPORT_BY_ORDINAL_32BIT = 0x80000000

    def __init__(self):
        super().__init__({})
        self.import_directory_tables = []

    def unpack(self, buffer):
        offset = self.offset
        sections = self.sections
        is_64bit = Packer.is_64bit
        i = 0
        while True:
            idt = ImportDirectoryTable()
            idt.unpack(buffer[offset+20*i:])

            if idt.is_empty():
                break

            nameoffset = utils.convert_rva_to_offset(idt.get_name_rva(), sections)
            idt.set_dll_name(utils.readstring(buffer, nameoffset))
            self.import_directory_tables.append(idt)

            # Sometimes ILT is empty, but the content of ILT and IAT is the same
            # and changes only after loading
            iltrva = idt.get_ilt_rva()
            if iltrva > 0:
                offsetILT = utils.convert_rva_to_offset(iltrva, sections)
            else:
                offsetILT = utils.convert_rva_to_offset(idt.get_iat_rva(), sections)

            # parse imported itemslist
            j = 0
            importObjects = []
            while True:
                iltentry = 0
                importbyordinal = 0
                nametableoffset = 0
                iatrva = 0
                value = 0
                if is_64bit:
                    iltentry = utils.unpack(buffer[offsetILT+j*8:offsetILT+j*8+8])
                    importbyordinal = iltentry & ImportTable.IMPORT_BY_ORDINAL_64BIT
                    iatrva = idt.get_iat_rva()+j*8
                    valueoffset = utils.convert_rva_to_offset(iatrva, sections)
                    value = utils.unpack(buffer[valueoffset:valueoffset+8])

                else:
                    iltentry = utils.unpack(buffer[offsetILT+j*4:offsetILT+j*4+4])
                    importbyordinal = iltentry & ImportTable.IMPORT_BY_ORDINAL_32BIT
                    iatrva = idt.get_iat_rva()+j*4
                    valueoffset = utils.convert_rva_to_offset(iatrva, sections)
                    value = utils.unpack(buffer[valueoffset:valueoffset+4])

                if iltentry == 0:  # last entry for this .dll
                    break

                # we have a forwarder:this is undocumented
                forwarder_chain = idt.get_forwarder_chain()
                if forwarder_chain != 0 and forwarder_chain != -1:
                    forwarderstringoffset = utils.convert_rva_to_offset(iltentry, sections)
                    forwarderstring = utils.readstring(buffer, forwarderstringoffset)

                    # since we have a  forwarder set it to forwarderchain
                    importObjects.append(ImportObject(iatrva, 0, 0, forwarderstring, forwarder_chain, value))

                # import by ordinal
                elif importbyordinal:
                    importObjects.append(ImportObject(iatrva, iltentry & 0xFFFF, 0, 0, "", 0, value))

                # import by name
                else:
                    nametableoffset = utils.convert_rva_to_offset((iltentry & 0x7FFFFFFF), sections)
                    hint = utils.unpack(buffer[nametableoffset:nametableoffset+2])
                    name = utils.readstring(buffer, nametableoffset+2)
                    importObjects.append(ImportObject(iatrva, 0, (iltentry & 0x7FFFFFFF), hint, name, 0, value))

                j += 1
                idt.set_import_objects(importObjects)
            i += 1

    def get_import_directory_tables(self):
        return self.import_directory_tables

    def __str__(self):
        out = f"\n[Imports]({len(self.import_directory_tables)})\n"
        out += f"{ImportDirectoryTable.get_column_titles()}\n"
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
