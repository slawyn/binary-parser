from packer import Packer
import utils


class SECTIONHEADER(Packer):
    SH_CHARACTERISTICS_T = {
        0x00000008: "IMAGE_SCN_TYPE_NO_PAD",
        0x00000020: "IMAGE_SCN_CNT_CODE",
        0x00000040: "IMAGE_SCN_CNT_INITIALIZED_DATA",
        0x00000080: "IMAGE_SCN_CNT_UNINITIALIZED_DATA",
        0x00000100: "IMAGE_SCN_LNK_OTHER",
        0x00000200: "IMAGE_SCN_LNK_INFO",
        0x00000800: "IMAGE_SCN_LNK_REMOVE",
        0x00001000: "IMAGE_SCN_LNK_COMDAT",
        0x00008000: "IMAGE_SCN_GPREL",
        0x00020000: "IMAGE_SCN_MEM_PURGEABLE",
        0x00020000: "IMAGE_SCN_MEM_16BIT",
        0x00040000: "IMAGE_SCN_MEM_LOCKED",
        0x00080000: "IMAGE_SCN_MEM_PRELOAD",
        0x00100000: "IMAGE_SCN_ALIGN_1BYTES",
        0x00200000: "IMAGE_SCN_ALIGN_2BYTES",
        0x00300000: "IMAGE_SCN_ALIGN_4BYTES",
        0x00400000: "IMAGE_SCN_ALIGN_8BYTES",
        0x00500000: "IMAGE_SCN_ALIGN_16BYTES",
        0x00600000: "IMAGE_SCN_ALIGN_32BYTES",
        0x00700000: "IMAGE_SCN_ALIGN_64BYTES",
        0x00800000: "IMAGE_SCN_ALIGN_128BYTES",
        0x00900000: "IMAGE_SCN_ALIGN_256BYTES",
        0x00A00000: "IMAGE_SCN_ALIGN_512BYTES",
        0x00B00000: "IMAGE_SCN_ALIGN_1024BYTES",
        0x00C00000: "IMAGE_SCN_ALIGN_2048BYTES",
        0x00D00000: "IMAGE_SCN_ALIGN_4096BYTES",
        0x00E00000: "IMAGE_SCN_ALIGN_8192BYTES",
        0x01000000: "IMAGE_SCN_LNK_NRELOC_OVFL",
        0x02000000: "IMAGE_SCN_MEM_DISCARDABLE",
        0x04000000: "IMAGE_SCN_MEM_NOT_CACHED",
        0x08000000: "IMAGE_SCN_MEM_NOT_PAGED",
        0x10000000: "IMAGE_SCN_MEM_SHARED",
        0x20000000: "IMAGE_SCN_MEM_EXECUTE",
        0x40000000: "IMAGE_SCN_MEM_READ",
        0x80000000: "IMAGE_SCN_MEM_WRITE"
    }

    # Define size constants
    SH_NAME_64SZ = 8
    SH_VIRTUAL_SIZE_64SZ = 4
    SH_VIRTUAL_ADDRESS_64SZ = 4
    SH_SIZE_OF_RAW_DATA_64SZ = 4
    SH_POINTER_TO_RAW_DATA_64SZ = 4
    SH_POINTER_TO_RELOCATIONS_64SZ = 4
    SH_POINTER_TO_LINE_NUMBERS_64SZ = 4
    SH_NUMBER_OF_RELOCATIONS_64SZ = 2
    SH_NUMBER_OF_LINENUMBERS_64SZ = 2
    SH_CHARACTERISTICS_64SZ = 4

    SH_NAME_SZ = 8
    SH_VIRTUAL_SIZE_SZ = 4
    SH_VIRTUAL_ADDRESS_SZ = 4
    SH_SIZE_OF_RAW_DATA_SZ = 4
    SH_POINTER_TO_RAW_DATA_SZ = 4
    SH_POINTER_TO_RELOCATIONS_SZ = 4
    SH_POINTER_TO_LINE_NUMBERS_SZ = 4
    SH_NUMBER_OF_RELOCATIONS_SZ = 2
    SH_NUMBER_OF_LINENUMBERS_SZ = 2
    SH_CHARACTERISTICS_SZ = 4

    def __init__(self, sh_name=0, sh_virtual_size=0, sh_virtual_address=0, sh_size_of_raw_data=0, sh_pointer_to_raw_data=0, sh_pointer_to_relocations=0, sh_pointer_to_line_numbers=0, sh_number_of_relocations=0, sh_number_of_linenumbers=0, sh_characteristics=0):
        super().__init__(
            {
                "sh_name": sh_name,
                "sh_virtual_size": sh_virtual_size,
                "sh_virtual_address": sh_virtual_address,
                "sh_size_of_raw_data": sh_size_of_raw_data,
                "sh_pointer_to_raw_data": sh_pointer_to_raw_data,
                "sh_pointer_to_relocations": sh_pointer_to_relocations,
                "sh_pointer_to_line_numbers": sh_pointer_to_line_numbers,
                "sh_number_of_relocations": sh_number_of_relocations,
                "sh_number_of_linenumbers": sh_number_of_linenumbers,
                "sh_characteristics": sh_characteristics,
            }
        )

    def get_virtual_address(self):
        return self.members['sh_virtual_address']

    def get_virtual_size(self):
        return self.members['sh_virtual_size']

    def get_pointer_to_raw_data(self):
        return self.members['sh_pointer_to_raw_data']

    def get_name(self):
        return self.members['sh_name']

    def get_formatted_name(self):
        return utils.convert_long_to_str(self.members['sh_name'])

    def GetCharacteristics(self):
        out = "Characteristics :"
        characteristics = self.Characteristics
        shifter = 0x80000000
        while shifter != 0:
            if shifter & characteristics in self._characteristictypes.keys():
                cha = self._characteristictypes[shifter & characteristics]
                out = out + "\n\t\t" + cha
            shifter = shifter >> 1
        out = out + "\n"
        return out

    def get_column_titles():
        out = ""
        out += utils.formatter2("%-20s", "[Name]")
        out += utils.formatter2("%-20s", "[VirtualSize]")
        out += utils.formatter2("%-20s", "[VirtualAddress]")
        out += utils.formatter2("%-20s", "[SizeOfRawData]")
        out += utils.formatter2("%-20s", "[PointerToRawData]")
        out += utils.formatter2("%-20s", "[PointerToRelocations]")
        out += utils.formatter2("%-20s", "[PointerToLineNumbers]")
        out += utils.formatter2("%-20s", "[NumberOfRelocations]")
        out += utils.formatter2("%-30s", "[NumberOfLineNumbers]")
        out += utils.formatter2("%-30s", "[Characteristics]")
        return out

    def __str__(self):
        out = ""
        out += utils.formatter2("%-20s",  self.get_formatted_name())
        out += utils.formatter2("%-20x",self.members['sh_virtual_size'])
        out += utils.formatter2("%-20x",self.members['sh_virtual_address'])
        out += utils.formatter2("%-20x",self.members['sh_size_of_raw_data'])
        out += utils.formatter2("%-20x",self.members['sh_pointer_to_raw_data'])
        out += utils.formatter2("%-20x",self.members['sh_pointer_to_relocations'])
        out += utils.formatter2("%-20x",self.members['sh_pointer_to_line_numbers'])
        out += utils.formatter2("%-20x",self.members['sh_number_of_relocations'])
        out += utils.formatter2("%-30x",self.members['sh_number_of_linenumbers'])
        out += utils.formatter2("%-30s",self.members['sh_characteristics'], table=SECTIONHEADER.SH_CHARACTERISTICS_T, mask=True)
        return out
