import utils
from packer import Packer


class ElfHeader(Packer):
    E_TYPE_T = {0x00: "ET_NONE (Unknown)", 0x01: "ET_REL (Relocatable file)", 0x02: "ET_EXEC (Executable file)", 0x03: "ET_DYN (Shared object)", 0x04: "ET_CORE (Core file)",
                0xFE00: "ET_LOOS (OS Specific)", 0xFEFF: "ET_HIOS (OS Specific)", 0xFF00: "ET_LOPROC (CPU specific)", 0xFFFF: "ET_HIPROC (CPU specific)"}
    E_MACHINE_T = {0x00: "Not Specified", 0x01: "AT&T WE 32100", 0x02: "SPARC", 0x03: "x86", 0x04: "Motorola 68000 (M68k)", 0x05: "Motorola 68000 (M88k)",
                   0x06: "Intel MCU", 0x07: "Intel 80860", 0x08: "MIPS", 0x09: "IBM System370", 0x0A: "MIPS RS3000 Little-endian", 0x0B: "Future use", 0x0C: "Future use",
                   0x0D: "Future use", 0x0E: "Hewlett-Packard PA-RISC", 0x0F: "Future use", 0x13: "Intel 80960", 0x14: "PowerPC", 0x15: "PowerPC(64-bit)", 0x16: "S390, S390x",
                   0x17: "IBM SPU/SPC", 0x18: "Future use", 0x19: "Future use", 0x1A: "Future use", 0x1B: "Future use", 0x1C: "Future use", 0x1D: "Future use", 0x1E: "Future use",
                   0x1F: "Future use", 0x20: "Future use", 0x21: "Future use", 0x22: "Future use", 0x23: "Future use", 0x24: "NEC V800", 0x25: "Fujitsu FR20", 0x26: "TRW RH-32",
                   0x27: "Motorola RCE", 0x28: "ARM (up to ARMv7/Aarch32)", 0x29: "Digital Alpha", 0x2A: "SuperH", 0x2B: "SPARC Version 9", 0x2C: "Siemens TriCore", 0x2D: "Argonaut RISC Core",
                   0x2E: "Hitachi H8/300", 0x2F: "Hitachi H8/300H", 0x30: "Hitachi H8S", 0x31: "Hitachi H8/500", 0x32: "IA-64", 0x33: "Stanford MIPS-X", 0x34: "Motorola ColdFire",
                   0x35: "Motorola M68HC12", 0x36: "Fujitsu MMA Multimedia Accelerator", 0x37: "Siemens PCP", 0x38: "Sony nCPU embedded RISC processor", 0x39: "Denso NDR1 microprocessor",
                   0x3A: "Motorola Star*Core processor", 0x3B: "Toyota ME16 processor", 0x3C: "STMicroelectronics ST100 processor", 0x3D: "Advanced Logic Corp. TinyJ embedded processor family",
                   0x3E: "AMD x86-64", 0x8C: "TMS320C6000 Family", 0xAF: "MCST Elbrus e2k", 0xB7: "ARM 64-bits (ARMv8/Aarch64)", 0xF3: "RISC-V", 0xF7: "Berkeley Packet Filter", 0x101: "WDC 65C816"}
    E_VERSION_T = {0x01: "1 (Original)"}

    def __init__(self):
        super().__init__(
            {
                "e_type": 2,
                "e_machine": 2,
                "e_version": 4,
                "e_entry": 4,
                "e_ph_off": 4,
                "e_sh_off": 4,
                "e_flags": 4,
                "e_eh_size": 2,
                "e_ph_ent_size": 2,
                "e_ph_count": 2,
                "e_sh_ent_size": 2,
                "e_sh_count": 2,
                "e_sh_strndx": 2
            },
            {
                "e_type": 2,
                "e_machine": 2,
                "e_version": 4,
                "e_entry": 8,
                "e_ph_off": 8,
                "e_sh_off": 8,
                "e_flags": 4,
                "e_eh_size": 2,
                "e_ph_ent_size": 2,
                "e_ph_count": 2,
                "e_sh_ent_size": 2,
                "e_sh_count": 2,
                "e_sh_strndx": 2
            },
            start_offset=16
        )

    def set_ph_offset(self, ph_offset):
        self.members["e_ph_off"] = ph_offset

    def set_sh_offset(self, sh_offset):
        self.members["e_sh_off"] = sh_offset

    def get_size(self):
        return self.get_value("e_eh_size")

    def get_ph_count(self):
        return self.get_value("e_ph_count")

    def get_sh_count(self):
        return self.get_value("e_sh_count")

    def set_sh_count(self, sh_count):
        self.members["e_sh_count"] = sh_count

    def set_ph_count(self, ph_count):
        self.members["e_ph_count"] = ph_count

    def get_sh_ent_sz(self):
        return self.get_value("e_sh_ent_size")

    def get_ph_ent_sz(self):
        return self.get_value("e_ph_ent_size")

    def get_ph_off(self):
        return self.get_value("e_ph_off")

    def get_sh_off(self):
        return self.get_value("e_sh_off")

    def get_stridx(self):
        return self.get_value("e_sh_strndx")

    def __str__(self):
        out = "\n[Elf Header]\n"
        out += utils.formatter("Type:", self.get_value('e_type'), table=ElfHeader.E_TYPE_T)
        out += utils.formatter("Machine:", self.get_value('e_machine'), table=ElfHeader.E_MACHINE_T)
        out += utils.formatter("Version:", self.get_value('e_version'), table=ElfHeader.E_VERSION_T)
        out += utils.formatter("Entry point address:", self.get_value('e_entry'), hex=True)
        out += utils.formatter("Program headers file offset:", self.get_value('e_ph_off'), hex=True)
        out += utils.formatter("Section headers file offset:", self.get_value('e_sh_off'), hex=True)
        out += utils.formatter("Flags:", self.get_value('e_flags'), hex=True)
        out += utils.formatter("Size of this header:", self.get_value('e_eh_size'))
        out += utils.formatter("Size of program headers:", self.get_value('e_ph_ent_size'), hex=True)
        out += utils.formatter("Number of program headers:", self.get_value('e_ph_count'))
        out += utils.formatter("Size of section headers:", self.get_value('e_sh_ent_size'), hex=True)
        out += utils.formatter("Number of section headers:", self.get_value('e_sh_count'))
        out += utils.formatter("Section header string table index:", self.get_value('e_sh_strndx'), hex=True)
        return out
