import utils
from packer import Packer


class ElfIdent(Packer):
    ELF_MAGIC = 0x7F454C46

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
                  0x11: "Nuxi CloudABI",
                  0x12: "Stratus Technologies OpenVOS"}
    EI_ABIVERSION_T = {0: "0 (Standard)"}

    DATA_LITTLE_ENDIAN = 0x01
    CLASS_64_BIT = 0x02

    def __init__(self):
        super().__init__(
            {
                "ei_magic": 4,
                "ei_class": 1,
                "ei_data": 1,
                "ei_version": 1,
                "ei_osabi": 1,
                "ei_abiversion": 1,
                "ei_pad": 7
            },
            always_32bit=True,
            always_little_endian=False
        )

    def unpack(self, buffer):
        super().unpack(buffer)

        if self.get_value("ei_magic") != ElfIdent.ELF_MAGIC:
            raise Exception(f"ERROR: Not an Elf file with tag {self.get_value('ei_magic'):x}")

        # Update Packer settings
        Packer.set_packer_config(
            is_little_endian=(self.get_value('ei_data') == ElfIdent.DATA_LITTLE_ENDIAN),
            is_64bit=(self.get_value('ei_class') == ElfIdent.CLASS_64_BIT)
        )

    def __str__(self):
        out = "\n[Elf Identification]\n"
        out += utils.formatter("Class:", self.get_value('ei_class'), table=ElfIdent.EI_CLASS_T)
        out += utils.formatter("Data:", self.get_value('ei_data'), table=ElfIdent.EI_DATA_T)
        out += utils.formatter("Version:", self.get_value('ei_version'), table=ElfIdent.EI_VERSION_T)
        out += utils.formatter("OSABI:", self.get_value('ei_osabi'), table=ElfIdent.EI_OSABI_T)
        out += utils.formatter("Abi Version:", self.get_value('ei_abiversion'), table=ElfIdent.EI_ABIVERSION_T)
        return out
