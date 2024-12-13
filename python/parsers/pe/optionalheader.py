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
        Packer.set_packer_config(is_64bit=False, is_little_endian=True)
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

        return out+"\n"
