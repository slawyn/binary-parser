import utils
from packer import Packer


class FileHeader(Packer):

    FH_MACHINE_T = {
        0x0: "IMAGE_FILE_MACHINE_UNKNOWN",
        0x1D3: "IMAGE_FILE_MACHINE_AM33",
        0x8664: "IMAGE_FILE_MACHINE_AMD64",
        0x1C0: "IMAGE_FILE_MACHINE_ARM",
        0xAA64: "IMAGE_FILE_MACHINE_ARM64",
        0x1C4: "IMAGE_FILE_MACHINE_ARMNT",
        0xEBC: "IMAGE_FILE_MACHINE_EBC",
        0x14C: "IMAGE_FILE_MACHINE_I386",
        0x200: "IMAGE_FILE_MACHINE_IA64",
        0x9041: "IMAGE_FILE_MACHINE_M32R",
        0x266: "IMAGE_FILE_MACHINE_MIPS16",
        0x366: "IMAGE_FILE_MACHINE_MIPSFPU",
        0x466: "IMAGE_FILE_MACHINE_MIPSFPU16",
        0x1F0: "IMAGE_FILE_MACHINE_POWERPC",
        0x1F1: "IMAGE_FILE_MACHINE_POWERPCFP",
        0x166: "IMAGE_FILE_MACHINE_R4000",
        0x5032: "IMAGE_FILE_MACHINE_RISCV32",
        0x5064: "IMAGE_FILE_MACHINE_RISCV64",
        0x5128: "IMAGE_FILE_MACHINE_RISCV128",
        0x1A2: "IMAGE_FILE_MACHINE_SH3",
        0x1A3: "IMAGE_FILE_MACHINE_SH3DSP",
        0x1A6: "IMAGE_FILE_MACHINE_SH4",
        0x1A8: "IMAGE_FILE_MACHINE_SH5",
        0x1C2: "IMAGE_FILE_MACHINE_THUMB",
        0x169: "IMAGE_FILE_MACHINE_WCEMIPSV2",
    }
    FH_CHARACTERISTICS_T = {
        0x0001: "IMAGE_FILE_RELOCS_STRIPPED",
        0x0002: "IMAGE_FILE_EXECUTABLE_IMAGE",
        0x0004: "IMAGE_FILE_LINE_NUMS_STRIPPED",
        0x0008: "IMAGE_FILE_LOCAL_SYMS_STRIPPED",
        0x0010: "IMAGE_FILE_AGGRESSIVE_WS_TRIM",
        0x0020: "IMAGE_FILE_LARGE_ADDRESS_AWARE",
        0x0080: "IMAGE_FILE_BYTES_REVERSED_LO",
        0x0100: "IMAGE_FILE_32BIT_MACHINE",
        0x0200: "IMAGE_FILE_DEBUG_STRIPPED",
        0x0400: "IMAGE_FILE_REMOVABLE_RUN_FROM_SWAP",
        0x0800: "IMAGE_FILE_NET_RUN_FROM_SWAP",
        0x1000: "IMAGE_FILE_SYSTEM",
        0x2000: "IMAGE_FILE_DLL",
        0x4000: "IMAGE_FILE_UP_SYSTEM_ONLY",
        0x8000: "IMAGE_FILE_BYTES_REVERSED_HI",
    }

    def __init__(self):
        super().__init__(
            {
                "fh_machine":  2,
                "fh_number_of_sections": 2,
                "fh_timestamp":  4,
                "fh_pointer_to_symboltable": 4,
                "fh_number_of_symbols": 4,
                "fh_optional_header_size": 2,
                "fh_characteristics": 2
            }
        )

    def get_number_of_sections(self):
        return self.get_value("fh_number_of_sections")

    def __str__(self):
        out = "\n[FileHeader]\n"
        out += utils.formatter("Machine:", self.get_value("fh_machine"), table=FileHeader.FH_MACHINE_T)
        out += utils.formatter("NumberOfSections:", self.get_value("fh_number_of_sections"), hex=True)
        out += utils.formatter("TimeDateStamp:", self.get_value("fh_timestamp"), hex=True)
        out += utils.formatter("PointerToSymbolTable:", self.get_value("fh_pointer_to_symboltable"), hex=True)
        out += utils.formatter("NumberOfSymbols:", self.get_value("fh_number_of_symbols"), hex=True)
        out += utils.formatter("SizeOfOptionalHeader:", self.get_value("fh_optional_header_size"), hex=True)
        out += utils.formatter("Characteristics:", self.get_value("fh_characteristics"),
                               table=FileHeader.FH_CHARACTERISTICS_T, mask=True,)
        return out
