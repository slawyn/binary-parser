from packer import Packer
import utils
from parsers.pe.directories.shared import ImportObject


class DelayImportDescriptor:
    def __init__(self, data, offset):
        self.numberOfImportObjects = 0
        self.importObjects = []
        self.Attributes = utils.unpack(data[0+offset:4+offset])
        self.NameRVA = utils.unpack(data[4+offset:8+offset])
        self.ModuleHandle = utils.unpack(data[8+offset:12+offset])
        self.DelayIAT = utils.unpack(data[12+offset:16+offset])
        self.DelayINT = utils.unpack(data[16+offset:20+offset])
        self.BoundDelayImportTable = utils.unpack(data[20+offset:24+offset])
        self.UnloadDelayImportTable = utils.unpack(data[24+offset:28+offset])
        self.TimeStamp = utils.unpack(data[28+offset:32+offset])
        if (self.Attributes | self.NameRVA | self.ModuleHandle | self.DelayINT | self.DelayIAT | self.BoundDelayImportTable | self.UnloadDelayImportTable | self.TimeStamp) == 0:
            self.isEmpty = True
        else:
            self.isEmpty = False


class DelayImportTable:
    def __init__(self, data, tables_fileoffset, sections, mode64):
        self.import_directory_tables = []

        i = 0
        while True:
            delaytable = DelayImportDescriptor(data, tables_fileoffset+32*i)
            if delaytable.isEmpty:
                break

            nameoffset = utils.convert_rva_to_offset(delaytable.NameRVA, sections)
            delaytable.nameOfDLL = utils.readstring(data, nameoffset)

            self.import_directory_tables.append(delaytable)

            j = 0
            namesoffset = utils.convert_rva_to_offset(delaytable.DelayINT, sections)
            importObjects = []
            importObjectsappend = importObjects.append

            delayIAT = delaytable.DelayIAT
            delayimportdescriptor = self.import_directory_tables[i]

            while True:
                function = 0
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
