import utils
from packer import Packer


class ProgramHeader(Packer):
    '''Program header
    '''

    PT_LOAD = 0x00000001
    PT_INTERP = 0x00000003
    PT_PHDR = 0x00000006
    PH_TYPE_T = {0x00000000: "PT_NULL (Unused)",
                 PT_LOAD: "PT_LOAD (Loadable segment)",
                 0x00000002: "PT_DYNAMIC (Dynamic linking information)",
                 PT_INTERP: "PT_INTERP (Interpreter information)",
                 0x00000004: "PT_NOTE (Auxiliary information)",
                 0x00000005: "PT_SHLIB (Reserved)",
                 0x00000006: "PT_PHDR (Contains program header table)",
                 0x00000007: "PT_TLS (Thread-Local Storage template)",
                 0x60000000: "PT_LOOS (OS specific)",
                 0x6474e550: "PT_GNU_EH_FRAME (Unwind information)",
                 0x6474e551: "PT_GNU_STACK (Stack flags)",
                 0x6474e552: "PT_GNU_RELRO (Read-only after relocation)",
                 0x6474e553: "PT_GNU_PROPERTY (Comment)",
                 0x6FFFFFFF: "PT_HIOS (OS specific)",
                 0x70000000: "PT_LOPROC (CPU specific)",
                 0x7FFFFFFF: "PT_HIPROC (CPU specific)"}
    PH_FLAGS_T = {0x01: "X", 0x02: "W", 0x04: "R", 0xf0000000: "U", }

    def __init__(self):
        super().__init__(
            {
                "ph_type": 4,
                "ph_offset": 4,
                "ph_vaddr": 4,
                "ph_paddr": 4,
                "ph_filesz": 4,
                "ph_memsz": 4,
                "ph_flags": 4,
                "ph_align": 4
            },
            {
                "ph_type": 4,
                "ph_flags": 4,
                "ph_offset": 8,
                "ph_vaddr": 8,
                "ph_paddr": 8,
                "ph_filesz": 8,
                "ph_memsz": 8,
                "ph_align": 8
            }
        )
        self.section_headers = []

    def get_offset(self):
        return self.get_value("ph_offset")

    def get_type(self):
        return self.get_value("ph_type")

    def get_vaddr(self):
        return self.get_value("ph_vaddr")

    def get_filesz(self):
        return self.get_value("ph_filesz")

    def get_memsz(self):
        return self.get_value("ph_memsz")

    def get_paddr(self):
        return self.get_value("ph_paddr")

    def get_align(self):
        return self.get_value("ph_align")

    def set_filesize(self, size):
        self.members["ph_filesz"] = size

    def set_offset(self, offset):
        self.members["ph_offset"] = offset

    def set_included_sections(self, section_headers):
        self.section_headers = section_headers

    def get_included_sections(self):
        return self.section_headers

    @staticmethod
    def get_column_titles():
        out = ""
        out += utils.formatter2("%-20s", "[File offset]")
        out += utils.formatter2("%-20s", "[File size]")
        out += utils.formatter2("%-20s", "[Physical address]")
        out += utils.formatter2("%-20s", "[Virtual address]")
        out += utils.formatter2("%-20s", "[Memory size]")
        out += utils.formatter2("%-10s", "[Align]")
        out += utils.formatter2("%-30s", "[Type]")
        out += utils.formatter2("%-10s", "[Flags]")
        return out

    def __str__(self):
        out = ""
        out += utils.formatter2("%-20x", self.get_value("ph_offset"))
        out += utils.formatter2("%-20x", self.get_value("ph_filesz"))
        out += utils.formatter2("%-20x", self.get_value("ph_paddr"))
        out += utils.formatter2("%-20x", self.get_value("ph_vaddr"))
        out += utils.formatter2("%-20x", self.get_value("ph_memsz"))
        out += utils.formatter2("%-10x", self.get_value("ph_align"))
        out += utils.formatter2("%-30s", self.get_value("ph_type"), table=ProgramHeader.PH_TYPE_T)
        out += utils.formatter2("%-10s", self.get_value("ph_flags"), table=ProgramHeader.PH_FLAGS_T, mask=True)
        return out
