import utils
from packer import Packer


class OptionalHeader(Packer):
    SIGNATURE_PE32 = 0x10B
    SIGNATURE_PE32PLUS = 0x20B

    def __init__(self):
        super().__init__({"oh_signature": 2}, always_little_endian=True)

    def unpack(self, buffer):
        super().unpack(buffer)

        signature = self.get_value("oh_signature")
        if signature == OptionalHeader.SIGNATURE_PE32PLUS:
            Packer.set_packer_config(is_64bit=True, is_little_endian=True)
        elif signature == OptionalHeader.SIGNATURE_PE32:
            Packer.set_packer_config(is_64bit=False, is_little_endian=True)
        else:
            raise Exception(f"ERROR: Unknown PE32 Signature {signature}")

        self.opt_header = OptionalSubHeader()
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
        out += utils.formatter("Signature:", self.get_value("oh_signature"), hex=True)
        out += str(self.opt_header)
        return out


class OptionalSubHeader(Packer):
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
        14: "IMAGE_SUBSYSTEM_XBOX",
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
        0x8000: "IMAGE_DLLCHARACTERISTICS_TERMINAL_SERVER_AWARE",
    }

    def __init__(self):
        super().__init__(
            {
                "oh_major_linker_version": 1,
                "oh_minor_linker_version": 1,
                "oh_size_of_code": 4,
                "oh_size_of_initialized_data": 4,
                "oh_size_of_uninitialized_data": 4,
                "oh_address_of_entry_point": 4,
                "oh_base_of_code": 4,
                "oh_base_of_data": 4,
                "oh_image_base": 4,
                "oh_section_alignment": 4,
                "oh_file_alignment": 4,
                "oh_major_os_version": 2,
                "oh_minor_os_version": 2,
                "oh_major_image_version": 2,
                "oh_minor_image_version": 2,
                "oh_major_subsystem_version": 2,
                "oh_minor_subsystem_version": 2,
                "oh_win32_version_value": 4,
                "oh_size_of_image": 4,
                "oh_size_of_headers": 4,
                "oh_checksum": 4,
                "oh_subsystem": 2,
                "oh_dll_characteristics": 2,
                "oh_size_of_stack_reserve": 4,
                "oh_size_of_stack_commit": 4,
                "oh_size_of_heap_reserve": 4,
                "oh_size_of_heap_commit": 4,
                "oh_loader_flags": 4,
                "oh_number_of_rva_and_sizes": 4,
            },
            {
                "oh_major_linker_version": 1,
                "oh_minor_linker_version": 1,
                "oh_size_of_code": 4,
                "oh_size_of_initialized_data": 4,
                "oh_size_of_uninitialized_data": 4,
                "oh_address_of_entry_point": 4,
                "oh_base_of_code": 4,
                # "oh_base_of_data" is not present in PE32+ (64-bit)
                "oh_image_base": 8,
                "oh_section_alignment": 4,
                "oh_file_alignment": 4,
                "oh_major_os_version": 2,
                "oh_minor_os_version": 2,
                "oh_major_image_version": 2,
                "oh_minor_image_version": 2,
                "oh_major_subsystem_version": 2,
                "oh_minor_subsystem_version": 2,
                "oh_win32_version_value": 4,
                "oh_size_of_image": 4,
                "oh_size_of_headers": 4,
                "oh_checksum": 4,
                "oh_subsystem": 2,
                "oh_dll_characteristics": 2,
                "oh_size_of_stack_reserve": 8,
                "oh_size_of_stack_commit": 8,
                "oh_size_of_heap_reserve": 8,
                "oh_size_of_heap_commit": 8,
                "oh_loader_flags": 4,
                "oh_number_of_rva_and_sizes": 4,
            },
        )

    def get_image_base(self):
        return self.get_value("oh_image_base")

    def __str__(self):
        out = ""
        out += utils.formatter("MajorLinkerVersion:", self.get_value("oh_major_linker_version"), hex=True)
        out += utils.formatter("MinorLinkerVersion:", self.get_value("oh_minor_linker_version"), hex=True)
        out += utils.formatter("SizeOfCode:", self.get_value("oh_size_of_code"), hex=True)
        out += utils.formatter("SizeOfInitializedData:", self.get_value("oh_size_of_initialized_data"), hex=True)
        out += utils.formatter("SizeOfUninitializedData:", self.get_value("oh_size_of_uninitialized_data"), hex=True)
        out += utils.formatter("AddressOfEntryPoint:", self.get_value("oh_address_of_entry_point"), hex=True)
        out += utils.formatter("BaseOfCode:", self.get_value("oh_base_of_code"), hex=True)
        if self.key_exists("oh_base_of_data"):
            out += utils.formatter("BaseOfData:", self.get_value("oh_base_of_data"), hex=True)
        out += utils.formatter("ImageBase:", self.get_value("oh_image_base"), hex=True)
        out += utils.formatter("SectionAlignment:", self.get_value("oh_section_alignment"), hex=True)
        out += utils.formatter("FileAlignment:", self.get_value("oh_file_alignment"), hex=True)
        out += utils.formatter("MajorOSVersion:", self.get_value("oh_major_os_version"), hex=True)
        out += utils.formatter("MinorOSVersion:", self.get_value("oh_minor_os_version"), hex=True)
        out += utils.formatter("MajorImageVersion:", self.get_value("oh_major_image_version"), hex=True)
        out += utils.formatter("MinorImageVersion:", self.get_value("oh_minor_image_version"), hex=True)
        out += utils.formatter("MajorSubsystemVersion:", self.get_value("oh_major_subsystem_version"), hex=True)
        out += utils.formatter("MinorSubsystemVersion:", self.get_value("oh_minor_subsystem_version"), hex=True)
        out += utils.formatter("Win32VersionValue:", self.get_value("oh_win32_version_value"), hex=True)
        out += utils.formatter("SizeOfImage:", self.get_value("oh_size_of_image"), hex=True)
        out += utils.formatter("SizeOfHeaders:", self.get_value("oh_size_of_headers"), hex=True)
        out += utils.formatter("CheckSum:", self.get_value("oh_checksum"), hex=True)
        out += utils.formatter("Subsystem:", self.get_value("oh_subsystem"),
                               table=OptionalSubHeader.SUBSYSTEM_TYPES_T)
        out += utils.formatter("DllCharacteristics:", self.get_value("oh_dll_characteristics"),
                               table=OptionalSubHeader.DLL_CHARACTERISTICS_TYPES_T, mask=True)
        out += utils.formatter("SizeOfStackReserve:", self.get_value("oh_size_of_stack_reserve"), hex=True)
        out += utils.formatter("SizeOfStackCommit:", self.get_value("oh_size_of_stack_commit"), hex=True)
        out += utils.formatter("SizeOfHeapReserve:", self.get_value("oh_size_of_heap_reserve"), hex=True)
        out += utils.formatter("SizeOfHeapCommit:", self.get_value("oh_size_of_heap_commit"), hex=True)
        out += utils.formatter("LoaderFlags:", self.get_value("oh_loader_flags"), hex=True)
        out += utils.formatter("NumberOfRvaAndSizes:", self.get_value("oh_number_of_rva_and_sizes"), hex=True)
        return out
