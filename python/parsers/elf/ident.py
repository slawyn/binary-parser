import utils
from packer import Packer

class ElfIdent(Packer):
    ELF_MAGIC = 0x7F454C46
    EI_MAGIC_SZ = 4
    EI_CLASS_SZ = 1
    EI_DATA_SZ = 1
    EI_VERSION_SZ = 1
    EI_OSABI_SZ = 1
    EI_ABIVERSION_SZ = 1
    EI_PAD_SZ = 7

    EI_CLASS_T = {1: "ELF32", 2: "ELF64"}
    EI_DATA_T = {1: "Little Endian", 2: "Big Endian"}
    EI_VERSION_T = {0: "0 (Old)", 1: "1 (Current)"}
    EI_OSABI_T = {0x00: "System V",
                  0x01: "HP-UX",
                  0x02: "NetBSD",
                  0x03: "Linux",
                  0x04: "GNU Hurd",
                  0x06: "Solaris",
                  0x07: "AIX",
                  0x08: "IRIX",
                  0x09: "FreeBSD",
                  0x0A: "Tru64",
                  0x0B: "Novell Modesto",
                  0x0C: "OpenBSD",
                  0x0D: "OpenVMS",
                  0x0E: "NonStop Kernel",
                  0x0F: "AROS",
                  0x10: "FenixOS",
                  0x011: "Nuxi CloudABI",
                  0x12: "Stratus Technologies OpenVOS"}
    EI_ABIVERSION_T = {0: "0 (Standard)"}

    DATA_LITTLE_ENDIAN = 0x01
    CLASS_64_BIT = 0x02

    def __init__(self):
        super().__init__(
            {
                "ei_magic": 0,
                "ei_class": 0,
                "ei_data": 0,
                "ei_version": 0,
                "ei_osabi": 0,
                "ei_abiversion": 0,
                "ei_pad": 0
            },
            always_bit32=True,
            always_little_endian=False
        )

    def unpack(self, buffer):
        super().unpack(buffer)

        if self.members["ei_magic"] != ElfIdent.ELF_MAGIC:
            raise Exception(f"ERROR: Not an Elf file with tag {self.members['ei_magic']:x}")

        # Update Packer settings
        Packer.set_packer_config(is_little_endian=(self.members['ei_data'] == ElfIdent.DATA_LITTLE_ENDIAN),
                                 is_64bit=(self.members['ei_class'] == ElfIdent.CLASS_64_BIT))

    def __str__(self):
        out = "\n[Elf Identification]\n"
        out += utils.formatter("Class:", self.members['ei_class'], table=ElfIdent.EI_CLASS_T)
        out += utils.formatter("Data:", self.members['ei_data'], table=ElfIdent.EI_DATA_T)
        out += utils.formatter("Version:", self.members['ei_version'], table=ElfIdent.EI_VERSION_T)
        out += utils.formatter("OSABI:", self.members['ei_osabi'], table=ElfIdent.EI_OSABI_T)
        out += utils.formatter("Abi Version:", self.members['ei_abiversion'], table=ElfIdent.EI_ABIVERSION_T)
        return out
