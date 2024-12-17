import utils
from packer import Packer


class OptionalHeader(Packer):
    SIGNATURE_PE32 = 0x10B
    SIGNATURE_PE32PLUS = 0x20B
    OH_SIGNATURE_SZ = 2

    def __init__(self, oh_signature=0):
        super().__init__(
            {
                "oh_signature": oh_signature
            },
            always_32bit=True,
            always_little_endian=True
        )
        self.is64Bit = False

    def unpack(self, buffer):
        super().unpack(buffer)
        if self.members['oh_signature'] == OptionalHeader.SIGNATURE_PE32PLUS:
            Packer.set_packer_config(is_64bit=True, is_little_endian=True)
            self.is64Bit = True
        elif self.members['oh_signature'] == OptionalHeader.SIGNATURE_PE32:
            Packer.set_packer_config(is_64bit=False, is_little_endian=True)
        else:
            raise Exception(f"ERROR: Unknown PE32 Signature {self.members['oh_signature']}")

        self.opt_header = OptionalHeaderSub()
        self.opt_header.set_offset(self.get_offset() + super().get_members_size())
        return self.opt_header.unpack(buffer)

    def set_offset(self, offset):
        super().set_offset(offset)

    def get_members_size(self):
        return super().get_members_size() + self.opt_header.get_members_size()

    def get_image_base(self):
        return self.opt_header.get_image_base()

    def __str__(self):
        out = "\n[OptionalHeader]\n"
        out += utils.formatter("Signature:", self.members['oh_signature'], hex=True)
        out += str(self.opt_header)
        return out


class OptionalHeaderSub(Packer):
    SUBSYSTEM_TYPES_T = {
        0: "IMAGE_SUBSYSTEM_UNKNOWN",
        1: "IMAGE_SUBSYSTEM_NATIVE",
        2: "IMAGE_SUBSYSTEM_WINDOWS_GUI",
        3: "IMAGE_SUBSYSTEM_WINDOWS_CUI",
        7: "IMAGE_SUBSYSTEM_POSIX_CUI",
        9: "IMAGE_SUBSYSTEM_WINDOWS_CE_GUI",
        10: "IMAGE_SUBSYSTEM_EFI_APPLICATION",
        11: "IMAGE_SUBSYSTEM_EFI_BOOT_SERVICE_DRIVER",
        12: "IMAGE_SUBSYSTEM_EFI_RUNTIME_DRIVER",
        13: "IMAGE_SUBSYSTEM_EFI_ROM",
        14: "IMAGE_SUBSYSTEM_XBOX"
    }

    DLL_CHARACTERISTICS_TYPES_T = {
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

    OH_MAJOR_LINKER_VERSION_SZ = 1
    OH_MINOR_LINKER_VERSION_SZ = 1
    OH_SIZE_OF_CODE_SZ = 4
    OH_SIZE_OF_INITIALIZED_DATA_SZ = 4
    OH_SIZE_OF_UNINITIALIZED_DATA_SZ = 4
    OH_ADDRESS_OF_ENTRY_POINT_SZ = 4
    OH_BASE_OF_CODE_SZ = 4
    OH_BASE_OF_DATA_SZ = 4
    OH_IMAGE_BASE_SZ = 4
    OH_SECTION_ALIGNMENT_SZ = 4
    OH_FILE_ALIGNMENT_SZ = 4
    OH_MAJOR_OS_VERSION_SZ = 2
    OH_MINOR_OS_VERSION_SZ = 2
    OH_MAJOR_IMAGE_VERSION_SZ = 2
    OH_MINOR_IMAGE_VERSION_SZ = 2
    OH_MAJOR_SUBSYSTEM_VERSION_SZ = 2
    OH_MINOR_SUBSYSTEM_VERSION_SZ = 2
    OH_WIN32_VERSION_VALUE_SZ = 4
    OH_SIZE_OF_IMAGE_SZ = 4
    OH_SIZE_OF_HEADERS_SZ = 4
    OH_CHECKSUM_SZ = 4
    OH_SUBSYSTEM_SZ = 2
    OH_DLL_CHARACTERISTICS_SZ = 2
    OH_SIZE_OF_STACK_RESERVE_SZ = 4
    OH_SIZE_OF_STACK_COMMIT_SZ = 4
    OH_SIZE_OF_HEAP_RESERVE_SZ = 4
    OH_SIZE_OF_HEAP_COMMIT_SZ = 4
    OH_LOADER_FLAGS_SZ = 4
    OH_NUMBER_OF_RVA_AND_SIZES_SZ = 4

    OH_MAJOR_LINKER_VERSION_64SZ = 1
    OH_MINOR_LINKER_VERSION_64SZ = 1
    OH_SIZE_OF_CODE_64SZ = 4
    OH_SIZE_OF_INITIALIZED_DATA_64SZ = 4
    OH_SIZE_OF_UNINITIALIZED_DATA_64SZ = 4
    OH_ADDRESS_OF_ENTRY_POINT_64SZ = 4
    OH_BASE_OF_CODE_64SZ = 4
    OH_IMAGE_BASE_64SZ = 8
    OH_SECTION_ALIGNMENT_64SZ = 4
    OH_FILE_ALIGNMENT_64SZ = 4
    OH_MAJOR_OS_VERSION_64SZ = 2
    OH_MINOR_OS_VERSION_64SZ = 2
    OH_MAJOR_IMAGE_VERSION_64SZ = 2
    OH_MINOR_IMAGE_VERSION_64SZ = 2
    OH_MAJOR_SUBSYSTEM_VERSION_64SZ = 2
    OH_MINOR_SUBSYSTEM_VERSION_64SZ = 2
    OH_WIN32_VERSION_VALUE_64SZ = 4
    OH_SIZE_OF_IMAGE_64SZ = 4
    OH_SIZE_OF_HEADERS_64SZ = 4
    OH_CHECKSUM_64SZ = 4
    OH_SUBSYSTEM_64SZ = 2
    OH_DLL_CHARACTERISTICS_64SZ = 2
    OH_SIZE_OF_STACK_RESERVE_64SZ = 8
    OH_SIZE_OF_STACK_COMMIT_64SZ = 8
    OH_SIZE_OF_HEAP_RESERVE_64SZ = 8
    OH_SIZE_OF_HEAP_COMMIT_64SZ = 8
    OH_LOADER_FLAGS_64SZ = 4
    OH_NUMBER_OF_RVA_AND_SIZES_64SZ = 4

    def __init__(self,
                 oh_major_linker_version=0,
                 oh_minor_linker_version=0,
                 oh_size_of_code=0,
                 oh_size_of_initialized_data=0,
                 oh_size_of_uninitialized_data=0,
                 oh_address_of_entry_point=0,
                 oh_base_of_code=0,
                 oh_base_of_data=0,
                 oh_image_base=0,
                 oh_section_alignment=0,
                 oh_file_alignment=0,
                 oh_major_os_version=0,
                 oh_minor_os_version=0,
                 oh_major_image_version=0,
                 oh_minor_image_version=0,
                 oh_major_subsystem_version=0,
                 oh_minor_subsystem_version=0,
                 oh_win32_version_value=0,
                 oh_size_of_image=0,
                 oh_size_of_headers=0,
                 oh_checksum=0,
                 oh_subsystem=0,
                 oh_dll_characteristics=0,
                 oh_size_of_stack_reserve=0,
                 oh_size_of_stack_commit=0,
                 oh_size_of_heap_reserve=0,
                 oh_size_of_heap_commit=0,
                 oh_loader_flags=0,
                 oh_number_of_rva_and_sizes=0):
        super().__init__(
            {
                "oh_major_linker_version": oh_major_linker_version,
                "oh_minor_linker_version": oh_minor_linker_version,
                "oh_size_of_code": oh_size_of_code,
                "oh_size_of_initialized_data": oh_size_of_initialized_data,
                "oh_size_of_uninitialized_data": oh_size_of_uninitialized_data,
                "oh_address_of_entry_point": oh_address_of_entry_point,
                "oh_base_of_code": oh_base_of_code,
                "oh_base_of_data": oh_base_of_data,
                "oh_image_base": oh_image_base,
                "oh_section_alignment": oh_section_alignment,
                "oh_file_alignment": oh_file_alignment,
                "oh_major_os_version": oh_major_os_version,
                "oh_minor_os_version": oh_minor_os_version,
                "oh_major_image_version": oh_major_image_version,
                "oh_minor_image_version": oh_minor_image_version,
                "oh_major_subsystem_version": oh_major_subsystem_version,
                "oh_minor_subsystem_version": oh_minor_subsystem_version,
                "oh_win32_version_value": oh_win32_version_value,
                "oh_size_of_image": oh_size_of_image,
                "oh_size_of_headers": oh_size_of_headers,
                "oh_checksum": oh_checksum,
                "oh_subsystem": oh_subsystem,
                "oh_dll_characteristics": oh_dll_characteristics,
                "oh_size_of_stack_reserve": oh_size_of_stack_reserve,
                "oh_size_of_stack_commit": oh_size_of_stack_commit,
                "oh_size_of_heap_reserve": oh_size_of_heap_reserve,
                "oh_size_of_heap_commit": oh_size_of_heap_commit,
                "oh_loader_flags": oh_loader_flags,
                "oh_number_of_rva_and_sizes": oh_number_of_rva_and_sizes,
            },
            {
                "oh_major_linker_version": oh_major_linker_version,
                "oh_minor_linker_version": oh_minor_linker_version,
                "oh_size_of_code": oh_size_of_code,
                "oh_size_of_initialized_data": oh_size_of_initialized_data,
                "oh_size_of_uninitialized_data": oh_size_of_uninitialized_data,
                "oh_address_of_entry_point": oh_address_of_entry_point,
                "oh_base_of_code": oh_base_of_code,
                "oh_image_base": oh_image_base,
                "oh_section_alignment": oh_section_alignment,
                "oh_file_alignment": oh_file_alignment,
                "oh_major_os_version": oh_major_os_version,
                "oh_minor_os_version": oh_minor_os_version,
                "oh_major_image_version": oh_major_image_version,
                "oh_minor_image_version": oh_minor_image_version,
                "oh_major_subsystem_version": oh_major_subsystem_version,
                "oh_minor_subsystem_version": oh_minor_subsystem_version,
                "oh_win32_version_value": oh_win32_version_value,
                "oh_size_of_image": oh_size_of_image,
                "oh_size_of_headers": oh_size_of_headers,
                "oh_checksum": oh_checksum,
                "oh_subsystem": oh_subsystem,
                "oh_dll_characteristics": oh_dll_characteristics,
                "oh_size_of_stack_reserve": oh_size_of_stack_reserve,
                "oh_size_of_stack_commit": oh_size_of_stack_commit,
                "oh_size_of_heap_reserve": oh_size_of_heap_reserve,
                "oh_size_of_heap_commit": oh_size_of_heap_commit,
                "oh_loader_flags": oh_loader_flags,
                "oh_number_of_rva_and_sizes": oh_number_of_rva_and_sizes,
            }
        )

    def get_image_base(self):
        return self.members['oh_image_base']

    def __str__(self):
        out = ""
        out += utils.formatter("MajorLinkerVersion:", self.members['oh_major_linker_version'], hex=True)
        out += utils.formatter("MinorLinkerVersion:", self.members['oh_minor_linker_version'], hex=True)
        out += utils.formatter("SizeOfCode:", self.members['oh_size_of_code'], hex=True)
        out += utils.formatter("SizeOfInitializedData:", self.members['oh_size_of_initialized_data'], hex=True)
        out += utils.formatter("SizeOfUninitializedData:", self.members['oh_size_of_uninitialized_data'], hex=True)
        out += utils.formatter("AddressOfEntryPoint:", self.members['oh_address_of_entry_point'], hex=True)
        out += utils.formatter("BaseOfCode:", self.members['oh_base_of_code'], hex=True)
        if 'oh_base_of_data' in self.members:
            out += utils.formatter("BaseOfData:", self.members['oh_base_of_data'], hex=True)
        out += utils.formatter("ImageBase:", self.members['oh_image_base'], hex=True)
        out += utils.formatter("SectionAlignment:", self.members['oh_section_alignment'], hex=True)
        out += utils.formatter("FileAlignment:", self.members['oh_file_alignment'], hex=True)
        out += utils.formatter("MajorOSVersion:", self.members['oh_major_os_version'], hex=True)
        out += utils.formatter("MinorOSVersion:", self.members['oh_minor_os_version'], hex=True)
        out += utils.formatter("MajorImageVersion:", self.members['oh_major_image_version'], hex=True)
        out += utils.formatter("MinorImageVersion:", self.members['oh_minor_image_version'], hex=True)
        out += utils.formatter("MajorSubsystemVersion:", self.members['oh_major_subsystem_version'], hex=True)
        out += utils.formatter("MinorSubsystemVersion:", self.members['oh_minor_subsystem_version'], hex=True)
        out += utils.formatter("Win32VersionValue:", self.members['oh_win32_version_value'], hex=True)
        out += utils.formatter("SizeOfImage:", self.members['oh_size_of_image'], hex=True)
        out += utils.formatter("SizeOfHeaders:", self.members['oh_size_of_headers'], hex=True)
        out += utils.formatter("CheckSum:", self.members['oh_checksum'], hex=True)
        out += utils.formatter("Subsystem:", self.members['oh_subsystem'], table=OptionalHeaderSub.SUBSYSTEM_TYPES_T)
        out += utils.formatter("DllCharacteristics:", self.members['oh_dll_characteristics'], table=OptionalHeaderSub.DLL_CHARACTERISTICS_TYPES_T, mask=True)
        out += utils.formatter("SizeOfStackReserve:", self.members['oh_size_of_stack_reserve'], hex=True)
        out += utils.formatter("SizeOfStackCommit:", self.members['oh_size_of_stack_commit'], hex=True)
        out += utils.formatter("SizeOfHeapReserve:", self.members['oh_size_of_heap_reserve'], hex=True)
        out += utils.formatter("SizeOfHeapCommit:", self.members['oh_size_of_heap_commit'], hex=True)
        out += utils.formatter("LoaderFlags:", self.members['oh_loader_flags'], hex=True)
        out += utils.formatter("NumberOfRvaAndSizes:", self.members['oh_number_of_rva_and_sizes'], hex=True)
        return out
