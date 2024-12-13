import utils
from packer import Packer


class FileHeader(Packer):
    FH_MACHINE_SZ = 2
    FH_NUMBER_OF_SECTIONS_SZ = 2
    FH_TIMESTAMP_SZ = 4
    FH_POINTER_TO_SYMBOLTABLE_SZ = 4
    FH_NUMBER_OF_SYMBOLS_SZ = 4
    FH_OPTIONAL_HEADER_SIZE_SZ = 2
    FH_CHARACTERISTICS_SZ = 2

    FH_MACHINE_T = {
        0x0: "IMAGE_FILE_MACHINE_UNKNOWN",
        0x1d3: "IMAGE_FILE_MACHINE_AM33",
        0x8664:	"IMAGE_FILE_MACHINE_AMD64",
        0x1c0:	"IMAGE_FILE_MACHINE_ARM",
        0xaa64:	"IMAGE_FILE_MACHINE_ARM64",
        0x1c4:	"IMAGE_FILE_MACHINE_ARMNT",
        0xebc:	"IMAGE_FILE_MACHINE_EBC",
        0x14c:	"IMAGE_FILE_MACHINE_I386",
        0x200:	"IMAGE_FILE_MACHINE_IA64",
        0x9041:	"IMAGE_FILE_MACHINE_M32R",
        0x266:	"IMAGE_FILE_MACHINE_MIPS16",
        0x366:	"IMAGE_FILE_MACHINE_MIPSFPU",
        0x466:	"IMAGE_FILE_MACHINE_MIPSFPU16",
        0x1f0:	"IMAGE_FILE_MACHINE_POWERPC",
        0x1f1:	"IMAGE_FILE_MACHINE_POWERPCFP",
        0x166:	"IMAGE_FILE_MACHINE_R4000",
        0x5032:	"IMAGE_FILE_MACHINE_RISCV32",
        0x5064:	"IMAGE_FILE_MACHINE_RISCV64",
        0x5128:	"IMAGE_FILE_MACHINE_RISCV128",
        0x1a2:	"IMAGE_FILE_MACHINE_SH3",
        0x1a3:	"IMAGE_FILE_MACHINE_SH3DSP",
        0x1a6:	"IMAGE_FILE_MACHINE_SH4",
        0x1a8:	"IMAGE_FILE_MACHINE_SH5",
        0x1c2:	"IMAGE_FILE_MACHINE_THUMB",
        0x169:	"IMAGE_FILE_MACHINE_WCEMIPSV2"
    }
    FH_CHARACTERISTICS_T = {
        0x0001: "IMAGE_FILE_RELOCS_STRIPPED",
        0x0002: "IMAGE_FILE_EXECUTABLE_IMAGE",
        0x0004: "IMAGE_FILE_LINE_NUMS_STRIPPED",
        0x0008: "IMAGE_FILE_LOCAL_SYMS_STRIPPED",
        0x0010: "IMAGE_FILE_AGGRESSIVE_WS_TRIM",
        0x0020: "IMAGE_FILE_LARGE_ADDRESS_ AWARE",
        0x0080: "IMAGE_FILE_BYTES_REVERSED_LO",
        0x0100: "IMAGE_FILE_32BIT_MACHINE",
        0x0200: "IMAGE_FILE_DEBUG_STRIPPED",
        0x0400: "IMAGE_FILE_REMOVABLE_RUN_ FROM_SWAP",
        0x0800: "IMAGE_FILE_NET_RUN_FROM_SWAP",
        0x1000: "IMAGE_FILE_SYSTEM",
        0x2000: "IMAGE_FILE_DLL",
        0x4000: "IMAGE_FILE_UP_SYSTEM_ONLY",
        0x8000: "IMAGE_FILE_BYTES_REVERSED_HI"}

    def __init__(self, fh_machine=0, fh_number_of_sections=0, fh_timestamp=0, fh_pointer_to_symboltable=0, fh_number_of_symbols=0, fh_optional_header_size=0, fh_characteristics=0):
        super().__init__(
            {
                "fh_machine": fh_machine,
                "fh_number_of_sections": fh_number_of_sections,
                "fh_timestamp": fh_timestamp,
                "fh_pointer_to_symboltable": fh_pointer_to_symboltable,
                "fh_number_of_symbols": fh_number_of_symbols,
                "fh_optional_header_size": fh_optional_header_size,
                "fh_characteristics": fh_characteristics,
            },
            always_32bit=True
        )

    def get_number_of_sections(self):
        return self.members["fh_number_of_sections"]

    def __str__(self):
        out = "\n[FileHeader]\n"
        out += utils.formatter("Machine:", self.members['fh_machine'], table=FileHeader.FH_MACHINE_T)
        out += utils.formatter("NumberOfSections:", self.members['fh_number_of_sections'], hex=True)
        out += utils.formatter("TimeDateStamp:", self.members['fh_timestamp'], hex=True)
        out += utils.formatter("PointerToSymbolTable:", self.members['fh_pointer_to_symboltable'], hex=True)
        out += utils.formatter("NumberOfSymbols:", self.members['fh_number_of_symbols'], hex=True)
        out += utils.formatter("SizeOfOptionalHeader:", self.members['fh_optional_header_size'], hex=True)
        out += utils.formatter("Characteristics:", self.members['fh_characteristics'], table=FileHeader.FH_CHARACTERISTICS_T, mask=True)
        return out
