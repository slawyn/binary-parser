from utils import *
import sys
import traceback
import utils
from packer import Packer
from parsers.pe.fileheader import FILEHEADER

  
class OPTIONALHEADER:
    _subsystemtypes = {
        0: "IMAGE_SUBSYSTEM_UNKNOWN",
        1: "IMAGE_SUBSYSTEM_NATIVE",
        2: "IMAGE_SUBSYSTEM_WINDOWS_GUI",
        3: "IMAGE_SUBSYSTEM_WINDOWS_CUI",
        7: "IMAGE_SUBSYSTEM_POSIX_CUI",
        9: "IMAGE_SUBSYSTEM_WINDOWS_CE_GUI",
        10: "IMAGE_SUBSYSTEM_EFI_APPLICATION",
        11: "IMAGE_SUBSYSTEM_EFI_BOOT_ SERVICE_DRIVER",
        12: "IMAGE_SUBSYSTEM_EFI_RUNTIME_ DRIVER",
        13: "IMAGE_SUBSYSTEM_EFI_ROM",
        14: "IMAGE_SUBSYSTEM_XBOX"


    }
    _dllcharacteristictypes = {
        0x0020: "IMAGE_DLLCHARACTERISTICS_HIGH_ENTROPY_VA",
        0x0040: "IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE",
        0x0080: "IMAGE_DLLCHARACTERISTICS_FORCE_INTEGRITY",
        0x0100: "IMAGE_DLLCHARACTERISTICS_NX_COMPAT",
        0x0200: "IMAGE_DLLCHARACTERISTICS_NO_ISOLATION",
        0x0400: "IMAGE_DLLCHARACTERISTICS_NO_SEH",
        0x0800: "IMAGE_DLLCHARACTERISTICS_NO_BIND",
        0x1000: "IMAGE_DLLCHARACTERISTICS_APPCONTAINER",
        0x2000: "IMAGE_DLLCHARACTERISTICS_WDM_DRIVER",
        0x4000: "IMAGE_DLLCHARACTERISTICS_GUARD_CF",
        0x8000: "IMAGE_DLLCHARACTERISTICS_TERMINAL_SERVER_AWARE"
    }

    def __init__(self, data):
        self.DataDirectory = {}
        self.Signature = unpack(data[0:2])
        if self.Signature == 0x20b:
            self.is64Bit = True
        else:
            self.is64Bit = False

        self.MajorLinkerVersion = unpack(data[2:3])
        self.MinorLinkerVersion = unpack(data[3:4])
        self.SizeOfCode = unpack(data[4:8])
        self.SizeOfInitializedData = unpack(data[8:12])
        self.SizeOfUninitializedData = unpack(data[12:16])
        self.AddressOfEntryPoint = unpack(data[16:20])
        self.BaseOfCode = unpack(data[20:24])

        if self.is64Bit:
            Packer.set_packer_config(is_64bit=True, is_little_endian=True)

            # 64bit doesn't have BaseOfData
            self.ImageBase = unpack(data[24:32])
        else:
            Packer.set_packer_config(is_64bit=False, is_little_endian=True)
            self.BaseOfData = unpack(data[24:28])
            self.ImageBase = unpack(data[28:32])

        self.SectionAlignment = unpack(data[32:36])
        self.FileAlignment = unpack(data[36:40])
        self.MajorOperatingSystemVersion = unpack(data[40:42])
        self.MinorOperatingSystemVersion = unpack(data[42:44])
        self.MajorImageVersion = unpack(data[44:46])
        self.MinorImageVersion = unpack(data[46:48])
        self.MajorSubsystemVersion = unpack(data[48:50])
        self.MinorSubsystemVersion = unpack(data[50:52])
        self.Win32VersionValue = unpack(data[52:56])
        self.SizeOfImage = unpack(data[56:60])
        self.SizeOfHeaders = unpack(data[60:64])
        self.CheckSum = unpack(data[64:68])
        self.Subsystem = unpack(data[68:70])
        self.DllCharacteristics = unpack(data[70:72])
        offset = 0

        if self.is64Bit:
            # in case of 64bit we have a shift in offset
            self.SizeOfStackReserve = unpack(data[72:80])
            self.SizeOfStackCommit = unpack(data[80:88])
            self.SizeOfHeapReserve = unpack(data[88:96])
            self.SizeOfHeapCommit = unpack(data[96:104])
            self.LoaderFlags = unpack(data[104:108])
            self.NumberOfRvaAndSizes = unpack(data[108:112])
            offset = 112
        else:
            self.SizeOfStackReserve = unpack(data[72:76])
            self.SizeOfStackCommit = unpack(data[76:80])
            self.SizeOfHeapReserve = unpack(data[80:84])
            self.SizeOfHeapCommit = unpack(data[84:88])
            self.LoaderFlags = unpack(data[88:92])
            self.NumberOfRvaAndSizes = unpack(data[92:96])
            offset = 96

        # fille the Dictionary with useful information
        exportrva = unpack(data[offset:offset+4])
        exportsz = unpack(data[offset+4:offset+8])
        if exportrva > 0:
            self.DataDirectory["EXPORT"] = [exportrva, exportsz, None]

        importrva = unpack(data[offset+8:offset+12])
        importsz = unpack(data[offset+12:offset+16])
        if importrva > 0:
            self.DataDirectory["IMPORT"] = [importrva, importsz, None]

        resourcerva = unpack(data[offset+16:offset+20])
        resourcesz = unpack(data[offset+20:offset+24])
        if resourcerva > 0:
            self.DataDirectory["RESOURCE"] = [resourcerva, resourcesz, None]

        exceptionrva = unpack(data[offset+24:offset+28])
        exceptionsz = unpack(data[offset+28:offset+32])
        if exceptionrva > 0:
            self.DataDirectory["EXCEPTION"] = [exceptionrva, exceptionsz, None]

        certificaterva = unpack(data[offset+32:offset+36])
        certificatesz = unpack(data[offset+36:offset+40])
        if certificaterva > 0:
            self.DataDirectory["CERTIFICATE"] = [
                certificaterva, certificatesz, None]

        relocrva = unpack(data[offset+40:offset+44])
        relocsz = unpack(data[offset+44:offset+48])
        if relocrva > 0:
            self.DataDirectory["RELOCATION"] = [relocrva, relocsz, None]

        debugrva = unpack(data[offset+48:offset+52])
        debugsz = unpack(data[offset+52:offset+56])

        if debugrva > 0:
            self.DataDirectory["DEBUG"] = [debugrva, debugsz, None]

        architecturerva = unpack(data[offset+56:offset+60])
        architecturesz = unpack(data[offset+60:offset+64])
        if architecturerva > 0:
            self.DataDirectory["ARCHITECTURE"] = [
                architecturerva, architecturesz, None]

        globalptrrva = unpack(data[offset+64:offset+68])
        globalptrsz = unpack(data[offset+68:offset+72])
        if globalptrrva > 0:
            self.DataDirectory["GLOBALPTR"] = [globalptrrva, globalptrsz, None]

        tlsrva = unpack(data[offset+72:offset+76])
        tlssz = unpack(data[offset+76:offset+80])
        if tlsrva > 0:
            self.DataDirectory["TLS"] = [tlsrva, tlssz, None]

        configrva = unpack(data[offset+80:offset+84])
        configsz = unpack(data[offset+84:offset+88])
        if configrva > 0:
            self.DataDirectory["CONFIG"] = [configrva, configsz, None]

        boundimportrva = unpack(data[offset+88:offset+92])
        boundimportsz = unpack(data[offset+92:offset+96])
        if boundimportrva > 0:
            self.DataDirectory["BOUNDIMPORT"] = [
                boundimportrva, boundimportsz, None]

        iatrva = unpack(data[offset+96:offset+100])
        iatsz = unpack(data[offset+100:offset+104])
        if iatrva > 0:
            self.DataDirectory["IAT"] = [iatrva, iatsz, None]

        delayimportrva = unpack(data[offset+104:offset+108])
        delayimportsz = unpack(data[offset+108:offset+112])
        if delayimportrva > 0:
            self.DataDirectory["DELAYIMPORT"] = [
                delayimportrva, delayimportsz, None]

        clrrva = unpack(data[offset+112:offset+116])
        clrsz = unpack(data[offset+116:offset+120])
        if clrrva > 0:
            self.DataDirectory["META"] = [clrrva, clrsz, None]

        reservedrva = unpack(data[offset+120:offset+124])
        reservedsz = unpack(data[offset+124:offset+128])
        if reservedrva > 0:
            self.DataDirectory["RESERVED"] = [reservedrva, reservedsz, None]

    def __str__(self):
        out = "\n[OPTIONALHEADER]\n"
        out += f"{'ImageBase:':30}{self.ImageBase:x}\n"
        out += f"{'BaseOfCode:':30}{self.BaseOfCode:x}\n"
        out += f"{'EntryPoint:':30}{self.AddressOfEntryPoint:x}\n"
        out += f"{'Subsystem:':30}{self.Subsystem:x} {self._subsystemtypes[self.Subsystem]}\n"
        out += "DllCharacteristics:"
        characteristics = self.DllCharacteristics
        shifter = 0x8000
        while (shifter != 0):

            if shifter & characteristics in self._dllcharacteristictypes.keys():
                cha = self._dllcharacteristictypes[shifter & characteristics]
                out = out+"\n\t"+cha
            shifter = shifter >> 1

        out += "\n[Data Directories]\n"
        for i in self.DataDirectory.keys():
            section = self.DataDirectory[i][2]
            name = "<Not found>"
            if section != None:
                name = section.Name
            out += f"{i:10}\n"
            out += f"  {'rva:':10} {self.DataDirectory[i][0]:x}\n"
            out += f"  {'size:':10} {self.DataDirectory[i][1]:x}\n"
            out += f"  {'sect:':10} {name:}\n"
        return out

        return out


class NTHEADER:
    def __init__(self, data):
        Packer.set_packer_config(is_64bit=False, is_little_endian=True)
        self.Signature = unpack(data[0:4])
        self.FILEHEADER_ = FILEHEADER()
        self.FILEHEADER_.unpack(data[4:])
        self.OPTIONALHEADER_ = OPTIONALHEADER(data[24:])


class DOSHEADER:
    def __init__(self, data):
        self.signature = data[0:2]
        self.cblp = unpack(data[2:4])
        self.cp = unpack(data[4:6])
        self.crlc = unpack(data[6:8])
        self.cparhdr = unpack(data[8:10])
        self.minalloc = unpack(data[10:12])
        self.maxalloc = unpack(data[12:14])
        self.ss = unpack(data[14:16])
        self.sp = unpack(data[16:18])
        self.checksum = unpack(data[18:20])
        self.ip = unpack(data[20:22])
        self.cs = unpack(data[22:24])
        self.lfarlc = unpack(data[24:26])
        self.noverlay = unpack(data[26:28])
        self.reserved1 = data[28:36]
        self.oemid = unpack(data[36:38])
        self.oeminfo = unpack(data[38:40])
        self.reserved2 = data[40:60]
        self.lfanew = unpack(data[60:64])


class SECTIONHEADER:
    _characteristictypes = {
        0x00000008:	"IMAGE_SCN_TYPE_NO_PAD",
        0x00000020:	"IMAGE_SCN_CNT_CODE",
        0x00000040:	"IMAGE_SCN_CNT_INITIALIZED_DATA",
        0x00000080:	"IMAGE_SCN_CNT_UNINITIALIZED_ DATA",
        0x00000100:	"IMAGE_SCN_LNK_OTHER",
        0x00000200:	"IMAGE_SCN_LNK_INFO",
        0x00000800:	"IMAGE_SCN_LNK_REMOVE",
        0x00001000:	"IMAGE_SCN_LNK_COMDAT",
        0x00008000:	"IMAGE_SCN_GPREL",
        0x00020000:	"IMAGE_SCN_MEM_PURGEABLE",
        0x00020000:	"IMAGE_SCN_MEM_16BIT",
        0x00040000:	"IMAGE_SCN_MEM_LOCKED",
        0x00080000:	"IMAGE_SCN_MEM_PRELOAD",
        0x00100000:	"IMAGE_SCN_ALIGN_1BYTES",
        0x00200000:	"IMAGE_SCN_ALIGN_2BYTES",
        0x00300000:	"IMAGE_SCN_ALIGN_4BYTES",
        0x00400000:	"IMAGE_SCN_ALIGN_8BYTES",
        0x00500000:	"IMAGE_SCN_ALIGN_16BYTES",
        0x00600000:	"IMAGE_SCN_ALIGN_32BYTES",
        0x00700000:	"IMAGE_SCN_ALIGN_64BYTES",
        0x00800000:	"IMAGE_SCN_ALIGN_128BYTES",
        0x00900000:	"IMAGE_SCN_ALIGN_256BYTES",
        0x00A00000:	"IMAGE_SCN_ALIGN_512BYTES",
        0x00B00000:	"IMAGE_SCN_ALIGN_1024BYTES",
        0x00C00000:	"IMAGE_SCN_ALIGN_2048BYTES",
        0x00D00000:	"IMAGE_SCN_ALIGN_4096BYTES",
        0x00E00000:	"IMAGE_SCN_ALIGN_8192BYTES",
        # if this is set the count is stored in VA of the first Entry in Relocs not NumberOfRelocations
        0x01000000:	"IMAGE_SCN_LNK_NRELOC_OVFL",
        0x02000000:	"IMAGE_SCN_MEM_DISCARDABLE",
        0x04000000:	"IMAGE_SCN_MEM_NOT_CACHED",
        0x08000000:	"IMAGE_SCN_MEM_NOT_PAGED",
        0x10000000:	"IMAGE_SCN_MEM_SHARED",
        0x20000000:	"IMAGE_SCN_MEM_EXECUTE",
        0x40000000:	"IMAGE_SCN_MEM_READ",
        0x80000000:	"IMAGE_SCN_MEM_WRITE"
    }

    def __init__(self, data):
        self.Name = readstring(data, 0)
        self.VirtualSize = unpack(data[8:12])
        self.VirtualAddress = unpack(data[12:16])
        self.SizeOfRawData = unpack(data[16:20])
        self.PointerToRawData = unpack(data[20:24])
        self.PointerToRelocations = unpack(data[24:28])
        self.PointerToLinenumbers = unpack(data[28:32])
        self.NumberOfRelocations = unpack(data[32:34])
        self.NumberOfLinenumbers = unpack(data[34:36])
        self.Characteristics = unpack(data[36:40])

    def GetCharacteristics(self):
        out = "Characteristics :"
        characteristics = self.Characteristics
        shifter = 0x80000000
        while (shifter != 0):

            if shifter & characteristics in self._characteristictypes.keys():
                cha = self._characteristictypes[shifter & characteristics]
                out = out+"\n\t\t"+cha
            shifter = shifter >> 1
        out = out+"\n"
        return out


class EXPORTTABLE:
    def __init__(self, data, tables_fileoffset, sections):
        self.exportTable = []
        self.ExportFlags = unpack(
            data[tables_fileoffset+0:tables_fileoffset+4])
        self.TimeStamp = unpack(
            data[tables_fileoffset+4:tables_fileoffset+8])
        self.MajorVersion = unpack(
            data[tables_fileoffset+8:tables_fileoffset+10])
        self.MinorVersion = unpack(
            data[tables_fileoffset+10:tables_fileoffset+12])
        self.NameRVA = unpack(
            data[tables_fileoffset+12:tables_fileoffset+16])
        self.OrdinalBase = unpack(
            data[tables_fileoffset+16:tables_fileoffset+20])
        self.NumberOfFunctions = unpack(
            data[tables_fileoffset+20:tables_fileoffset+24])
        self.NumberOfNames = unpack(
            data[tables_fileoffset+24:tables_fileoffset+28])
        self.FunctionsRVA = unpack(
            data[tables_fileoffset+28:tables_fileoffset+32])
        self.NamesRVA = unpack(
            data[tables_fileoffset+32:tables_fileoffset+36])
        self.OrdinalsRVA = unpack(
            data[tables_fileoffset+36:tables_fileoffset+40])

        # read offsets
        FunctionsFileOffset = convertRVAToOffset(self.FunctionsRVA, sections)
        NamesFileOffset = convertRVAToOffset(self.NamesRVA, sections)
        OrdinalsFileOffset = convertRVAToOffset(self.OrdinalsRVA, sections)
        NamesAndOrdinals = {}

        # read names and corresponding indexes
        numberofnames = self.NumberOfNames
        for i in range(self.NumberOfNames):
            NamesAndOrdinals[unpack(data[OrdinalsFileOffset+i*2:OrdinalsFileOffset+i*2+2])
                             ] = unpack(data[NamesFileOffset+i*4:NamesFileOffset+i*4+4])

        # create export table
        for i in range(self.NumberOfFunctions):
            FunctionAddress = unpack(
                data[FunctionsFileOffset+i*4:FunctionsFileOffset+i*4+4])
            if FunctionAddress == 0:  # there are sometimes zero reserved entries for future use, which are currently not in use
                continue
            # if exported by name
            if i in NamesAndOrdinals.keys():
                namesoffset = convertRVAToOffset(NamesAndOrdinals[i], sections)
                symbol = readstring(data, namesoffset)
                # Ordinal,address,hintg,string address, string
                self.exportTable.append(ExportObject(
                    i+self.OrdinalBase, FunctionAddress, i, NamesAndOrdinals[i], symbol))

            # if exported only by ordinal or is forwarded to imported function from another dll
            else:

                namesoffset = convertRVAToOffset(FunctionAddress, sections)
                symbol = ""
                # forwarded to another .dll
                if namesoffset > tables_fileoffset:
                    symbol = readstring(data, namesoffset)
                # Zeroes because either exported by Ordinal or has forwarder RVA
                self.exportTable.append(ExportObject(
                    i+self.OrdinalBase, FunctionAddress, 0, 0, symbol))


# not part of the documentation: for internal use only
class ExportObject:
    def __init__(self, ordinal, functionrva, hint, namerva, name):
        self.Ordinal = ordinal
        self.Hint = hint
        self.FunctionRVA = functionrva
        self.NameRVA = namerva
        self.Name = name


class IMPORTDIRECTORYTABLE:
    def __init__(self, data, offset):
        self.importObjects = None
        self.nameOfDLL = ""
        self.numberOfImportObjects = 0

        self.ILTRVA = unpack(data[0+offset:4+offset])

        # -1 if bound import
        self.TimeStamp = unpack(data[4+offset:8+offset])

        # -1 if bound import : not important
        self.ForwarderChain = unpack(data[8+offset:12+offset])
        self.NameRVA = unpack(data[12+offset:16+offset])
        self.IATRVA = unpack(data[16+offset:20+offset])

        if (self.ILTRVA | self.TimeStamp | self.ForwarderChain | self.NameRVA | self.IATRVA) == 0:
            self.isEmpty = True
        else:
            self.isEmpty = False
# not part of the documentation: for internal use only


class ImportObject:
    def __init__(self, iatrva, ordinal, nametablerva, hint, name, forwarder, value):
        self.IATAddressRVA = iatrva
        self.Ordinal = ordinal
        self.Hint = hint
        self.NameTableRVA = nametablerva
        self.Name = name
        self.Forwarder = forwarder
        self.value = value
        self.ForwarderString = ""


class IMPORTTABLE:
    IMPORT_BY_ORDINAL_64BIT = 0x8000000000000000
    IMPORT_BY_ORDINAL_32BIT = 0x80000000

    def __init__(self, data, tables_fileoffset, sections, mode64):
        self.ImportDirectoryTables = []
        self.NumberOfDLLs = 0
        i = 0
        importdirectorytables = self.ImportDirectoryTables
        while True:
            importdirectorytable = IMPORTDIRECTORYTABLE(data, tables_fileoffset+20*i)
            if importdirectorytable.isEmpty:
                break

            nameoffset = convertRVAToOffset(importdirectorytable.NameRVA, sections)
            importdirectorytable.nameOfDLL = readstring(data, nameoffset)
            importdirectorytables.append(importdirectorytable)

            # Sometimes ILT is empty, but the content of ILT and IAT is the same
            # and changes only after loading
            if importdirectorytable.ILTRVA > 0:
                offsetILT = convertRVAToOffset(importdirectorytable.ILTRVA, sections)
            else:
                offsetILT = convertRVAToOffset(importdirectorytable.IATRVA, sections)

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
                    iltentry = unpack(data[offsetILT+j*8:offsetILT+j*8+8])
                    importbyordinal = iltentry & IMPORTTABLE.IMPORT_BY_ORDINAL_64BIT
                    iatrva = importdirectorytable.IATRVA+j*8
                    valueoffset = convertRVAToOffset(iatrva, sections)
                    value = unpack(data[valueoffset:valueoffset+8])

                else:
                    iltentry = unpack(data[offsetILT+j*4:offsetILT+j*4+4])
                    importbyordinal = iltentry & IMPORTTABLE.IMPORT_BY_ORDINAL_32BIT
                    iatrva = importdirectorytable.IATRVA+j*4
                    valueoffset = convertRVAToOffset(iatrva, sections)
                    value = unpack(data[valueoffset:valueoffset+4])

                if iltentry == 0:  # last entry for this .dll
                    break

                # we have a forwarder:this is undocumented
                if importdirectorytable.ForwarderChain != 0 and importdirectorytable.ForwarderChain != -1:
                    forwarderstringoffset = convertRVAToOffset(iltentry, sections)
                    forwarderstring = readstring(data, forwarderstringoffset)

                    # since we have a  forwarder set it to forwarderchain
                    importObjects.append(ImportObject(iatrva, 0, 0, forwarderstring, importdirectorytable.ForwarderChain, value))

                # import by ordinal
                elif importbyordinal:
                    importObjects.append(ImportObject(iatrva, iltentry & 0xFFFF, 0, 0, "", 0, value))

                # import by name
                else:
                    nametableoffset = convertRVAToOffset((iltentry & 0x7FFFFFFF), sections)
                    hint = unpack(data[nametableoffset:nametableoffset+2])
                    name = readstring(data, nametableoffset+2)
                    importObjects.append(ImportObject(iatrva, 0, (iltentry & 0x7FFFFFFF), hint, name, 0, value))

                j += 1
                importdirectorytable.importObjects = importObjects
                importdirectorytable.numberOfImportObjects = j
            i += 1
        self.NumberOfDLLs = i


class DELAYIMPORTDESCRIPTOR:
    def __init__(self, data, offset):
        self.numberOfImportObjects = 0
        self.importObjects = []
        self.Attributes = unpack(data[0+offset:4+offset])
        self.NameRVA = unpack(data[4+offset:8+offset])
        self.ModuleHandle = unpack(data[8+offset:12+offset])
        self.DelayIAT = unpack(data[12+offset:16+offset])
        self.DelayINT = unpack(data[16+offset:20+offset])
        self.BoundDelayImportTable = unpack(data[20+offset:24+offset])
        self.UnloadDelayImportTable = unpack(data[24+offset:28+offset])
        self.TimeStamp = unpack(data[28+offset:32+offset])
        if (self.Attributes | self.NameRVA | self.ModuleHandle | self.DelayINT | self.DelayIAT | self.BoundDelayImportTable | self.UnloadDelayImportTable | self.TimeStamp) == 0:
            self.isEmpty = True
        else:
            self.isEmpty = False


class DELAYIMPORTTABLE:
    def __init__(self, data, tables_fileoffset, sections, mode64):
        self.DelayImportDescriptors = []
        self.NumberOfDLLs = 0

        i = 0
        # delayimportdescriptrs = self.DelayImportDescriptors
        delayimportdescriptors = self.DelayImportDescriptors
        while True:
            delaytable = DELAYIMPORTDESCRIPTOR(data, tables_fileoffset+32*i)
            if delaytable.isEmpty:
                break

            nameoffset = convertRVAToOffset(delaytable.NameRVA, sections)
            delaytable.nameOfDLL = readstring(data, nameoffset)

            delayimportdescriptors.append(delaytable)

            j = 0
            namesoffset = convertRVAToOffset(delaytable.DelayINT, sections)
            importObjects = []
            importObjectsappend = importObjects.append

            delayIAT = delaytable.DelayIAT
            delayimportdescriptor = delayimportdescriptors[i]

            while True:
                function = 0
                intentry = 0
                iatrva = 0
                importbyordinal = 0
                value = 0
                if mode64:
                    intentry = unpack(
                        data[namesoffset+8*j:namesoffset+8*j+8])
                    # is the import by ordinal bit set?
                    importbyordinal = intentry & 0x8000000000000000
                    iatrva = delayIAT+j*8
                    valueoffset = convertRVAToOffset(iatrva, sections)
                    value = unpack(data[valueoffset:valueoffset+8])
                else:
                    intentry = unpack(
                        data[namesoffset+4*j:namesoffset+4*j+4])
                    importbyordinal = intentry & 0x80000000  # same as above. but for 32 bit PE
                    iatrva = delayIAT+j*4
                    valueoffset = convertRVAToOffset(iatrva, sections)
                    value = unpack(data[valueoffset:valueoffset+4])

                if intentry == 0:
                    break

                # import by ordinal
                if importbyordinal:
                    importObjectsappend(ImportObject(
                        iatrva, intentry & 0xFFFF, 0, 0, "", 0, value))  # no hint no name

                # import by name
                else:
                    nametableoffset = convertRVAToOffset(
                        (intentry & 0x7FFFFFFF), sections)
                    hint = unpack(
                        data[nametableoffset:nametableoffset+2])  # read hint
                    name = readstring(data, nametableoffset+2)
                    importObjectsappend(ImportObject(
                        iatrva, 0, (intentry & 0x7FFFFFFF), hint, name, 0, value))
                j = j+1

            delayimportdescriptor.importObjects = importObjects
            delayimportdescriptor.numberOfImportObjects = j
            i = i+1
        self.NumberOfDLLs = i


class TLSObject:
    def __init__(self, data, offset,  mode):
        idx = 16
        if mode:
            self.RawDataStartVA = unpack(data[0+offset:8+offset])
            self.RawDataEndVA = unpack(data[8+offset:16+offset])
            self.AddressOfIndex = unpack(data[16+offset:24+offset])
            self.AddressOfCallbacks = unpack(data[24+offset:32+offset])
            idx = 32

        else:

            self.RawDataStartVA = unpack(data[offset:offset+4])
            self.RawDataEndVA = unpack(data[4+offset:8+offset])
            self.AddressOfIndex = unpack(data[8+offset:12+offset])
            self.AddressOfCallbacks = unpack(data[12+offset:16+offset])

        self.SizeOfZeroFill = unpack(data[offset+idx:offset+idx+4])
        self.Characteristics = unpack(data[offset+idx+4:offset+idx+8])
        if (self.RawDataStartVA | self.RawDataEndVA | self.AddressOfIndex | self.AddressOfCallbacks | self.SizeOfZeroFill | self.Characteristics) == 0:
            self.isEmpty = True
        else:
            self.isEmpty = False


class TLS:
    def __init__(self, data, tables_fileoffset, mode):
        self.TLSObjects = []
        i = 0

        offset = 24
        if mode:
            offset = 40

        #
        while True:
            object = TLSObject(data, tables_fileoffset+offset*i, mode)

            i = i+1
            if object.isEmpty:
                break
            self.TLSObjects.append(object)


class ScopeTable:
    def __init__(self, startrva, endrva, handlerrva, jumptarget):
        self.StartRVA = startrva
        self.EndRVA = endrva
        self.HandlerRVA = handlerrva
        self.JumpTarget = jumptarget


class ExceptionHandler:
    def __init__(self, handlerrva, count,  scopetables):
        self.HandlerRVA = handlerrva
        self.ScopeTableCount = count
        self.ScopeTables = scopetables


class UnwindInfoObject:
    _flagtypes = {
        0: "UNW_FLAG_NO_HANDLER",
        1: "UNW_FLAG_EHANDLER",
        2: "UNW_FLAG_UHANDLER",
        3: "UNW_FLAG_FHANDLER",
        4: "UNW_FLAG_CHAININFO"
    }
    _registers = ["rax", "rcx", "rdx", "rbx", "rsp", "rbp", "rsi",
                  "rdi", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]
    _codes = {0: "UWOP_PUSH_NONVOL",
              1: "UWOP_ALLOC_LARGE",
              2: "UWOP_ALLOC_SMALL",
              3: "UWOP_SET_FPREG",
              4: "UWOP_SAVE_NONVOL",
              5: "UWOP_SAVE_NONVOL_FAR",
              8: "UWOP_SAVE_XMM128",
              9: "UWOP_SAVE_XMM128_FAR",
              10: "UWOP_PUSH_MACHFRAME"
              }

    def __init__(self, version, flags, sizeofprolog, countofcodes, frameregister, frameregisteroff, codes, handler):
        self.Version = version
        self.Flags = flags
        self.SizeofProlog = sizeofprolog
        self.CountofCodes = countofcodes
        self.FrameRegister = frameregister
        self.FrameOffset = frameregisteroff
        self.Codes = []
        for i in range(len(codes)):

            offset = (codes[i] & 0xFF)
            opcode = (codes[i] & 0xF000) >> 12
            opinfo = (codes[i] & 0xF00) >> 8
            out = self.decode(offset, opcode, opinfo)
            self.Codes.append(out)

        self.ExceptionHandler = handler

    def decode(self, offset, opcode, opinfo):
        out = "0x%x:" % (offset)
        out = out + " opcode: 0x%x" % (opcode)
        out = out + " opinfo: 0x%x" % (opinfo)

        return out

    def getFlags(self):
        return self._flagtypes[self.Flags]

    def getFrameRegister(self):
        return self._registers[self.FrameRegister]


class ExceptionObject:
    def __init__(self, data, offset):
        self.StartRVA = unpack(data[0+offset:4+offset])
        self.EndRVA = unpack(data[4+offset:8+offset])
        self.UnwindInfoPtr = unpack(data[8+offset:12+offset])
        self.UnwindInfo = None
        self.isEmpty = False
        if self.StartRVA | self.EndRVA | self.UnwindInfoPtr == 0:
            self.isEmpty = True


class EXCEPTIONTABLE:
    def __init__(self, data, tables_fileoffset, sections):
        self.ExceptionObjects = []
        offset = 24
        idx = 0
        exceptionbjectsappend = self.ExceptionObjects.append
        while True:
            object = ExceptionObject(data, tables_fileoffset+idx*offset)
            if object.isEmpty:
                break

            unwindinfooff = convertRVAToOffset(object.UnwindInfoPtr, sections)

            t = unpack(data[unwindinfooff:unwindinfooff+1])

            version = t & 0b00000111
            flags = (t & 0b11111000) >> 3

            szprolog = unpack(data[unwindinfooff+1:unwindinfooff+2])
            countofcodes = unpack(data[unwindinfooff+2:unwindinfooff+3])
            t = unpack(data[unwindinfooff+3:unwindinfooff+4])

            frameregister = t & 0b00001111
            frameregisteroff = (t & 0b11110000) >> 4

            # codes and exception handler
            codes = []
            codesoffset = unwindinfooff+4
            for j in range(countofcodes):
                codes.append(unpack(
                    data[codesoffset+j*2:codesoffset+2+j*2]))

            handler = None

            if flags & 0x3:  # 1 - 3 we have a handler
                # the rva of the handler must be aligned after the code
                handlerreloffset = (countofcodes % 2+countofcodes)*2
                handlerinfooffset = codesoffset+handlerreloffset
                exceptharva = unpack(
                    data[handlerinfooffset:handlerinfooffset+4])

                count = unpack(
                    data[handlerinfooffset+4:handlerinfooffset+8])
                scoptableoffset = handlerinfooffset+8
                scopetables = []

                if count < 5:

                    scopes = 0

                    for i in range(count):
                        scopes = i*16

                        startrva = unpack(
                            data[scoptableoffset+scopes:scoptableoffset+scopes+4])
                        endrva = unpack(
                            data[scoptableoffset+4+scopes:scoptableoffset+8+scopes])
                        handlerrva = unpack(
                            data[scoptableoffset+8+scopes:scoptableoffset+12+scopes])
                        jumptarget = unpack(
                            data[scoptableoffset+12+scopes:scoptableoffset+16+scopes])
                        scopetables.append(ScopeTable(
                            startrva, endrva, handlerrva, jumptarget))

                handler = ExceptionHandler(exceptharva, count, scopetables)

            object.UnwindInfo = UnwindInfoObject(
                version, flags, szprolog, countofcodes, frameregister, frameregisteroff, codes, handler)

            idx = idx+1
            exceptionbjectsappend(object)


class PeParser:
    export_dic = {}
    import_dic = {}
    delayimport_dic = {}
    delayimport_stubs_dic = {}
    tls_dic = {}
    exception_dic = {}
    section_files_to_disassemble = []

    def __init__(self, buffer):
        try:

            self.buffer = buffer
            self.DOSHEADER_ = DOSHEADER(self.buffer)
            # next header at offset field
            self.NTHEADER_ = NTHEADER(self.buffer[self.DOSHEADER_.lfanew:])
            self.SECTIONHEADERS_ = []
            self.EXPORTTABLE_ = None
            self.IMPORTTABLE_ = None
            self.DELAYIMPORTTABLE_ = None
            self.EXCEPTIONTABLE_ = None
            self.TLS_ = None

            # FL offset + FL_SIZE+ PESignature_SIZE+PEHeader_SIZE
            offset = self.DOSHEADER_.lfanew+20+4+224
            if self.NTHEADER_.OPTIONALHEADER_.is64Bit:
                offset = self.DOSHEADER_.lfanew+20+4+240  # peheader is bigger in pe32+

            numberofentries = self.NTHEADER_.FILEHEADER_.get_number_of_sections()

            # collect all section information
            for i in range(numberofentries):
                self.SECTIONHEADERS_.append(
                    SECTIONHEADER(self.buffer[offset+40*i:]))

            # x-reference  sections with data directories
            for i in self.NTHEADER_.OPTIONALHEADER_.DataDirectory:
                dd_rva = self.NTHEADER_.OPTIONALHEADER_.DataDirectory[i][0]
                for j in range(numberofentries):
                    section_rva = self.SECTIONHEADERS_[j].VirtualAddress
                    section_size = self.SECTIONHEADERS_[j].VirtualSize

                    if dd_rva >= section_rva and dd_rva <= section_rva+section_size:
                        self.NTHEADER_.OPTIONALHEADER_.DataDirectory[i][2] = self.SECTIONHEADERS_[
                            j]
                        break

            # Decode directories
            for key in self.NTHEADER_.OPTIONALHEADER_.DataDirectory:
                # get rva of the data directory
                tablesrva = self.NTHEADER_.OPTIONALHEADER_.DataDirectory[key][0]
                # get corresponding section in which the information resides
                section = self.NTHEADER_.OPTIONALHEADER_.DataDirectory[key][2]
                if section == None:
                    log(f"ERROR: {key} has no section")
                    continue

                # offset to directory table: internal use
                tables_fileoffset = tablesrva-section.VirtualAddress + section.PointerToRawData

                # parse directories
                if key == "EXPORT":
                    log("Parsing EXPORT")
                    self.EXPORTTABLE_ = EXPORTTABLE(
                        self.buffer, tables_fileoffset, self.SECTIONHEADERS_)

                elif key == "IMPORT":
                    log("Parsing IMPORT")
                    self.IMPORTTABLE_ = IMPORTTABLE(
                        self.buffer, tables_fileoffset, self.SECTIONHEADERS_, self.NTHEADER_.OPTIONALHEADER_.is64Bit)

                elif key == "DELAYIMPORT":
                    log("Parsing DELAYIMPORT")
                    self.DELAYIMPORTTABLE_ = DELAYIMPORTTABLE(
                        self.buffer, tables_fileoffset, self.SECTIONHEADERS_, self.NTHEADER_.OPTIONALHEADER_.is64Bit)

                elif key == "TLS":
                    log("Parsing TLS")
                    self.TLS_ = TLS(self.buffer, tables_fileoffset,
                                    self.NTHEADER_.OPTIONALHEADER_.is64Bit)

                elif key == "EXCEPTION":  # x64 only, on x86 the exception information is saved on the stack
                    log("Parsing EXCEPTION")
                    self.EXCEPTIONTABLE_ = EXCEPTIONTABLE(
                        self.buffer,  tables_fileoffset, self.SECTIONHEADERS_)

                else:
                    pass

        except Exception as e:
            traceback.print_exc()

    def get_buffer(self):
        return self.buffer

    def __str__(self):
        out = str(self.NTHEADER_.FILEHEADER_)
        out += str(self.NTHEADER_.OPTIONALHEADER_)
        out += self.GetSections()

        # write out information about dictionaries
        if self.DELAYIMPORTTABLE_:
            out += self.GetDelayImports()

        if self.IMPORTTABLE_:
            out += self.GetImports()

        if self.EXPORTTABLE_:
            out += self.GetExports()

        if self.TLS_:
            out += self.GetTLSCallbacks()

        if self.EXCEPTIONTABLE_:
            out += self.GetExceptions()

        return out

    def write_all(self, folder):
        log("Success!Writing to files..")

        # write out information about all headers
        with open(folder+"\\peanalysis.txt", "w") as fd:
            log("\t"+folder+"\\peanalysis.txt")
            fd.write(self.NTHEADER_.FILEHEADER_.GetMachine())
            fd.write(self.NTHEADER_.FILEHEADER_.GetCharacteristics())
            fd.write("ImageBase:\n\t%s\n" %
                     hex(self.NTHEADER_.OPTIONALHEADER_.ImageBase))
            fd.write("BaseOfCode:\n\t%s\n" %
                     hex(self.NTHEADER_.OPTIONALHEADER_.BaseOfCode))
            fd.write("EntryPoint:\n\t%s\n" %
                     hex(self.NTHEADER_.OPTIONALHEADER_.AddressOfEntryPoint))
            fd.write(self.NTHEADER_.OPTIONALHEADER_.GetSubsystem())
            fd.write(self.NTHEADER_.OPTIONALHEADER_.GetDllCharacteristics())
            fd.write(self.NTHEADER_.OPTIONALHEADER_.GetDataDirectories())
            fd.write(self.GetSections())
        fd.close()

        # write out information about dictionaries
        if self.DELAYIMPORTTABLE_:
            with open(folder+"\\delayimports.txt", "w") as fd:
                log("\t"+folder+"\\delayimports.txt")
                out = self.GetDelayImports()
                fd.write(out)
            fd.close()

        if self.IMPORTTABLE_:
            with open(folder+"\\imports.txt", "w") as fd:
                log("\t"+folder+"\\imports.txt")
                out = self.GetImports()
                fd.write(out)
            fd.close()

        if self.EXPORTTABLE_:
            with open(folder+"\\exports.txt", "w") as fd:
                log("\t"+folder+"\\exports.txt")
                out = self.GetExports()
                fd.write(out)
            fd.close()

        if self.TLS_:
            with open(folder+"\\tlscallbacks.txt", "w") as fd:
                log("\t"+folder+"\\tlscallbacks.txt")
                out = self.GetTLSCallbacks()
                fd.write(out)
            fd.close()

        if self.EXCEPTIONTABLE_:
            with open(folder+"\\exceptions.txt", "w") as fd:
                log("\t"+folder+"\\exceptions.txt")
                out = self.GetExceptions()
                fd.write(out)

            fd.close()

        # write out sections that need to be disassembled as .bin
        codesections = self.GetCodeSections()
        section_files_to_disassemble = self.section_files_to_disassemble
        for i in range(len(codesections)):

            section_files_to_disassemble.append("code"+str(i))
            log("\t"+folder+"\\"+section_files_to_disassemble[i]+".bin")

            # need to investigate which limits are good
            with open(folder+"\\"+section_files_to_disassemble[i]+".bin", "wb") as fd:
                lowerlimit = codesections[i].PointerToRawData
                upperlimit = codesections[i].PointerToRawData + \
                    codesections[i].VirtualSize

                if upperlimit > codesections[i].PointerToRawData+codesections[i].SizeOfRawData:
                    fd.write(self.buffer[lowerlimit:upperlimit])
                    padding = upperlimit - \
                        codesections[i].PointerToRawData + \
                        codesections[i].SizeOfRawData
                    for i in range(padding):
                        fd.write("\x00")
                else:
                    fd.write(self.buffer[lowerlimit:upperlimit])
            fd.close()

    def getSectionFilesToDisassemble(self):
        return self.section_files_to_disassemble

    def GetSections(self):
        NumberOfEntries = self.NTHEADER_.FILEHEADER_.get_number_of_sections()
        out = "\n[Sections]\n"
        out += " NumberOfSections: %d\n" % (NumberOfEntries)

        for i in range(NumberOfEntries):
            out += f" {'Name':20} {self.SECTIONHEADERS_[i].Name}\n"
            out += f" {'VirtualAddress':20} {self.SECTIONHEADERS_[i].VirtualAddress:x}\n"
            out += f" {'VirtualSize':20} {self.SECTIONHEADERS_[i].VirtualSize:x}\n"
            out += f" {'PointerToRawData':20} {self.SECTIONHEADERS_[i].PointerToRawData:x}\n"
            out += f" {'SizeOfRawData':20} {self.SECTIONHEADERS_[i].SizeOfRawData:x}\n"
            out += f" {self.SECTIONHEADERS_[i].GetCharacteristics()}\n"
        return out

    def GetExports(self):
        NumberOfExports = len(self.EXPORTTABLE_.exportTable)
        table = self.EXPORTTABLE_.exportTable
        base = self.NTHEADER_.OPTIONALHEADER_.ImageBase
        out = ""
        exports = {}
        for i in range(NumberOfExports):
            address = "0x%x" % (table[i].FunctionRVA+base)
            name = ""
            if table[i].Name != "":
                name = table[i].Name
            else:
                name = "__exportedByOrdinal_%x" % (table[i].Ordinal)
            exports[table[i].FunctionRVA+base] = name
            out = out+address+"\t"+name+"\n"
        return out

    def GetTLSCallbacks(self):
        NumberOfCallbacks = len(self.TLS_.TLSObjects)
        table = self.TLS_.TLSObjects
        out = ""
        tls_dic = self.tls_dic
        for i in range(NumberOfCallbacks):
            address = "0x%x" % (table[i].AddressOfCallbacks)
            name = "__TLS_Callback_%x" % (table[i].AddressOfCallbacks)
            tls_dic[table[i].AddressOfCallbacks] = name
            out = out+address+"\t"+name+"\n"
        return out

    def GetDelayImports(self):
        NumberOfDLLs = self.DELAYIMPORTTABLE_.NumberOfDLLs
        base = self.NTHEADER_.OPTIONALHEADER_.ImageBase
        out = ""
        delayimport_dic = self.delayimport_dic
        delayimport_stubs_dic = self.delayimport_stubs_dic
        for i in range(NumberOfDLLs):
            table = self.DELAYIMPORTTABLE_.DelayImportDescriptors[i]
            dlladdress = "0x%x" % (table.NameRVA+base)
            dllname = "#"+table.nameOfDLL
            out1 = dlladdress+"\t"+dllname+"\n"
            out = out+out1
            numberofobjects = table.numberOfImportObjects

            for j in range(numberofobjects):
                out2 = ""
                address = "0x%x" % (table.importObjects[j].IATAddressRVA+base)
                value = "0x%x" % (table.importObjects[j].value)
                name = ""
                if table.importObjects[j].Ordinal:
                    name = "__importedByOrdinal_%x" % (
                        table.importObjects[j].Ordinal)
                else:
                    name = "%s" % (table.importObjects[j].Name)

                delayimport_dic[table.importObjects[j].IATAddressRVA +
                                base] = table.nameOfDLL+"!"+name
                delayimport_stubs_dic[table.importObjects[j]
                                      .value] = table.nameOfDLL+"!"+name+"__stub"
                out = out+address+"\t"+value+"\t"+name+"\n"

        return out

    def GetNameToAddressDics(self):
        return self.export_dic, self.import_dic, self.delayimport_dic, self.delayimport_stubs_dic, self.tls_dic, self.exception_dic

    def GetCodeSections(self):
        sections = []
        for sh in self.SECTIONHEADERS_:
            if (sh.Characteristics & 0x20000020) > 0:
                if sh.PointerToRawData != 0:
                    sections.append(sh)
        return sections

    def GetImports(self):
        NumberOfDLLs = self.IMPORTTABLE_.NumberOfDLLs
        base = self.NTHEADER_.OPTIONALHEADER_.ImageBase
        out = "\n[Imports]\n"
        import_dic = self.import_dic
        for i in range(NumberOfDLLs):
            table = self.IMPORTTABLE_.ImportDirectoryTables[i]
            dlladdress = f"{table.NameRVA+base:x}"
            dllname = table.nameOfDLL
            out1 = dlladdress+"\t"+dllname+"\n"
            out = out+out1
            numberofobjects = table.numberOfImportObjects

            for j in range(numberofobjects):
                out2 = ""
                address = f"  {table.importObjects[j].IATAddressRVA + base:x}"
                name = ""
                if table.importObjects[j].Forwarder:
                    name = "__forwarded__%s" % (table.importObjects[j].Name)
                elif table.importObjects[j].Ordinal:
                    name = "__importedByOrdinal_%x" % (
                        table.importObjects[j].Ordinal)
                else:
                    name = "%s" % (table.importObjects[j].Name)
                import_dic[table.importObjects[j].IATAddressRVA +
                           base] = table.nameOfDLL+"!"+name
                out = out+address+"\t"+name+"\n"

        return out

    def GetExceptions(self):
        NumberOfExceptions = len(self.EXCEPTIONTABLE_.ExceptionObjects)
        base = self.NTHEADER_.OPTIONALHEADER_.ImageBase
        out = ""
        exception_dic = self.exception_dic
        exceptionobjects = self.EXCEPTIONTABLE_.ExceptionObjects

        for i in range(NumberOfExceptions):
            out2 = ""
            out3 = ""
            out4 = ""

            entry = exceptionobjects[i]

            startva = "0x%x" % (entry.StartRVA+base)
            endva = "0x%x" % (entry.EndRVA+base)

            exception_dic[entry.StartRVA+base] = entry.EndRVA+base
            unwindinfo = entry.UnwindInfo

            '''
			# information about stackunwinding
			out2="\tVersion:%x \tFlags:%s \tCountOfCodes:%d \tFrameRegister:%s \tFrameOffset:0x%x"%(
			    unwindinfo.Version, unwindinfo.getFlags(),unwindinfo.CountofCodes, unwindinfo.getFrameRegister(), unwindinfo.FrameOffset)


			countofcodes=unwindinfo.CountofCodes


			for i in range(countofcodes):
				out3=out3+"\t"+unwindinfo.Codes[i]+"\n"


			flags = entry.UnwindInfo.Flags


			if flags == 0x4:	#chained
				pass

			elif flags & 0x3:	#e-/uhandler
				rva = "Handler Address:0x%x"%(
				    entry.UnwindInfo.ExceptionHandler.HandlerRVA+base)
				nmofscopetables = entry.UnwindInfo.ExceptionHandler.ScopeTableCount
				if nmofscopetables <5: #dunno how to recognize if it's data or scopetables
					count= "Count: 0x%x"%(nmofscopetables)
					out4="\t\t"+rva+"\t"+count+"\n"
					for i in range(nmofscopetables):
						table = entry.UnwindInfo.ExceptionHandler.ScopeTables[i]
						out4=out4+"\t\tScope Table:\n\t\t\tStart:0x%x\n\t\t\tEnd:0x%x\n\t\t\tHandler Address:0x%x\n\t\t\tJump Target:0x%x"%(
						    table.StartRVA+base,table.EndRVA+base,table.HandlerRVA+base, table.JumpTarget+base)
				else:
					data= "Data: 0x%x"%(nmofscopetables)
					out4="\t\t"+rva+"\t"+data+"\n"
			'''
            out = out+"".join([startva, "\t", endva, "\n"])

        return out
