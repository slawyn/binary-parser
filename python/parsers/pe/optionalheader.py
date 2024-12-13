import utils
from packer import Packer


class OptionalHeader:
    SIGNATURE_PE32PLUS = 0x20B
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
        self.Signature = utils.unpack(data[0:2])
        if self.Signature == OptionalHeader.SIGNATURE_PE32PLUS:
            self.is64Bit = True
        else:
            self.is64Bit = False

        self.MajorLinkerVersion = utils.unpack(data[2:3])
        self.MinorLinkerVersion = utils.unpack(data[3:4])
        self.SizeOfCode = utils.unpack(data[4:8])
        self.SizeOfInitializedData = utils.unpack(data[8:12])
        self.SizeOfUninitializedData = utils.unpack(data[12:16])
        self.AddressOfEntryPoint = utils.unpack(data[16:20])
        self.BaseOfCode = utils.unpack(data[20:24])

        if self.is64Bit:
            Packer.set_packer_config(is_64bit=True, is_little_endian=True)
            # 64bit doesn't have BaseOfData
            self.ImageBase = utils.unpack(data[24:32])
        else:
            Packer.set_packer_config(is_64bit=False, is_little_endian=True)
            self.BaseOfData = utils.unpack(data[24:28])
            self.ImageBase = utils.unpack(data[28:32])

        self.SectionAlignment = utils.unpack(data[32:36])
        self.FileAlignment = utils.unpack(data[36:40])
        self.MajorOperatingSystemVersion = utils.unpack(data[40:42])
        self.MinorOperatingSystemVersion = utils.unpack(data[42:44])
        self.MajorImageVersion = utils.unpack(data[44:46])
        self.MinorImageVersion = utils.unpack(data[46:48])
        self.MajorSubsystemVersion = utils.unpack(data[48:50])
        self.MinorSubsystemVersion = utils.unpack(data[50:52])
        self.Win32VersionValue = utils.unpack(data[52:56])
        self.SizeOfImage = utils.unpack(data[56:60])
        self.SizeOfHeaders = utils.unpack(data[60:64])
        self.CheckSum = utils.unpack(data[64:68])
        self.Subsystem = utils.unpack(data[68:70])
        self.DllCharacteristics = utils.unpack(data[70:72])
        offset = 0

        if self.is64Bit:
            # in case of 64bit we have a shift in offset
            self.SizeOfStackReserve = utils.unpack(data[72:80])
            self.SizeOfStackCommit = utils.unpack(data[80:88])
            self.SizeOfHeapReserve = utils.unpack(data[88:96])
            self.SizeOfHeapCommit = utils.unpack(data[96:104])
            self.LoaderFlags = utils.unpack(data[104:108])
            self.NumberOfRvaAndSizes = utils.unpack(data[108:112])
            offset = 112
        else:
            self.SizeOfStackReserve = utils.unpack(data[72:76])
            self.SizeOfStackCommit = utils.unpack(data[76:80])
            self.SizeOfHeapReserve = utils.unpack(data[80:84])
            self.SizeOfHeapCommit = utils.unpack(data[84:88])
            self.LoaderFlags = utils.unpack(data[88:92])
            self.NumberOfRvaAndSizes = utils.unpack(data[92:96])
            offset = 96

        # fille the Dictionary with useful information
        exportrva = utils.unpack(data[offset:offset+4])
        exportsz = utils.unpack(data[offset+4:offset+8])
        if exportrva > 0:
            self.DataDirectory["EXPORT"] = [exportrva, exportsz, None]

        importrva = utils.unpack(data[offset+8:offset+12])
        importsz = utils.unpack(data[offset+12:offset+16])
        if importrva > 0:
            self.DataDirectory["IMPORT"] = [importrva, importsz, None]

        resourcerva = utils.unpack(data[offset+16:offset+20])
        resourcesz = utils.unpack(data[offset+20:offset+24])
        if resourcerva > 0:
            self.DataDirectory["RESOURCE"] = [resourcerva, resourcesz, None]

        exceptionrva = utils.unpack(data[offset+24:offset+28])
        exceptionsz = utils.unpack(data[offset+28:offset+32])
        if exceptionrva > 0:
            self.DataDirectory["EXCEPTION"] = [exceptionrva, exceptionsz, None]

        certificaterva = utils.unpack(data[offset+32:offset+36])
        certificatesz = utils.unpack(data[offset+36:offset+40])
        if certificaterva > 0:
            self.DataDirectory["CERTIFICATE"] = [
                certificaterva, certificatesz, None]

        relocrva = utils.unpack(data[offset+40:offset+44])
        relocsz = utils.unpack(data[offset+44:offset+48])
        if relocrva > 0:
            self.DataDirectory["RELOCATION"] = [relocrva, relocsz, None]

        debugrva = utils.unpack(data[offset+48:offset+52])
        debugsz = utils.unpack(data[offset+52:offset+56])

        if debugrva > 0:
            self.DataDirectory["DEBUG"] = [debugrva, debugsz, None]

        architecturerva = utils.unpack(data[offset+56:offset+60])
        architecturesz = utils.unpack(data[offset+60:offset+64])
        if architecturerva > 0:
            self.DataDirectory["ARCHITECTURE"] = [
                architecturerva, architecturesz, None]

        globalptrrva = utils.unpack(data[offset+64:offset+68])
        globalptrsz = utils.unpack(data[offset+68:offset+72])
        if globalptrrva > 0:
            self.DataDirectory["GLOBALPTR"] = [globalptrrva, globalptrsz, None]

        tlsrva = utils.unpack(data[offset+72:offset+76])
        tlssz = utils.unpack(data[offset+76:offset+80])
        if tlsrva > 0:
            self.DataDirectory["TLS"] = [tlsrva, tlssz, None]

        configrva = utils.unpack(data[offset+80:offset+84])
        configsz = utils.unpack(data[offset+84:offset+88])
        if configrva > 0:
            self.DataDirectory["CONFIG"] = [configrva, configsz, None]

        boundimportrva = utils.unpack(data[offset+88:offset+92])
        boundimportsz = utils.unpack(data[offset+92:offset+96])
        if boundimportrva > 0:
            self.DataDirectory["BOUNDIMPORT"] = [
                boundimportrva, boundimportsz, None]

        iatrva = utils.unpack(data[offset+96:offset+100])
        iatsz = utils.unpack(data[offset+100:offset+104])
        if iatrva > 0:
            self.DataDirectory["IAT"] = [iatrva, iatsz, None]

        delayimportrva = utils.unpack(data[offset+104:offset+108])
        delayimportsz = utils.unpack(data[offset+108:offset+112])
        if delayimportrva > 0:
            self.DataDirectory["DELAYIMPORT"] = [
                delayimportrva, delayimportsz, None]

        clrrva = utils.unpack(data[offset+112:offset+116])
        clrsz = utils.unpack(data[offset+116:offset+120])
        if clrrva > 0:
            self.DataDirectory["META"] = [clrrva, clrsz, None]

        reservedrva = utils.unpack(data[offset+120:offset+124])
        reservedsz = utils.unpack(data[offset+124:offset+128])
        if reservedrva > 0:
            self.DataDirectory["RESERVED"] = [reservedrva, reservedsz, None]

    def __str__(self):
        out = "\n[OptionalHeader]\n"
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
                name = section.get_formatted_name()
            out += f"{i:10}\n"
            out += f"  {'rva:':10} {self.DataDirectory[i][0]:x}\n"
            out += f"  {'size:':10} {self.DataDirectory[i][1]:x}\n"
            out += f"  {'sect:':10} {name:}\n"
        return out
