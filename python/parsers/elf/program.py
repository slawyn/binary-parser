import utils
from packer import Packer

class ProgramHeader(Packer):
    '''Program header
    '''
    PH_TYPE_SZ = 4
    PH_OFFSET_SZ = 4
    PH_VADDR_SZ = 4
    PH_PADDR_SZ = 4
    PH_FILESZ_SZ = 4
    PH_MEMSZ_SZ = 4
    PH_FLAGS_SZ = 4
    PH_ALIGN_SZ = 4

    PH_TYPE_64SZ = 4
    PH_FLAGS_64SZ = 4
    PH_OFFSET_64SZ = 8
    PH_VADDR_64SZ = 8
    PH_PADDR_64SZ = 8
    PH_FILESZ_64SZ = 8
    PH_MEMSZ_64SZ = 8
    PH_ALIGN_64SZ = 8

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

    def __init__(self, ph_type=0, ph_flags=0, ph_offset=0, ph_vaddr=0, ph_paddr=0, ph_filesz=0, ph_memsz=0, ph_align=0):
        super().__init__(
            {
                "ph_type": ph_type,
                "ph_offset": ph_offset,
                "ph_vaddr": ph_vaddr,
                "ph_paddr": ph_paddr,
                "ph_filesz": ph_filesz,
                "ph_memsz": ph_memsz,
                "ph_flags": ph_flags,
                "ph_align": ph_align
            },
            {
                "ph_type": ph_type,
                "ph_flags": ph_flags,
                "ph_offset": ph_offset,
                "ph_vaddr": ph_vaddr,
                "ph_paddr": ph_paddr,
                "ph_filesz": ph_filesz,
                "ph_memsz": ph_memsz,
                "ph_align": ph_align
            }
        )
        self.section_headers = []

    def get_offset(self):
        return self.members["ph_offset"]

    def get_type(self):
        return self.members["ph_type"]

    def get_vaddr(self):
        return self.members["ph_vaddr"]

    def get_filesz(self):
        return self.members["ph_filesz"]

    def get_memsz(self):
        return self.members["ph_memsz"]

    def get_paddr(self):
        return self.members["ph_paddr"]
    
    def get_align(self):
        return self.members["ph_align"]

    def set_filesize(self, size):
        self.members["ph_filesz"] = size

    def set_offset(self, offset):
        self.members["ph_offset"] = offset

    def set_included_sections(self, section_headers):
        self.section_headers = section_headers

    def get_included_sections(self):
        return self.section_headers
    
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
        out += utils.formatter2("%-20x", self.members["ph_offset"])
        out += utils.formatter2("%-20x", self.members["ph_filesz"])
        out += utils.formatter2("%-20x", self.members["ph_paddr"])
        out += utils.formatter2("%-20x", self.members["ph_vaddr"])
        out += utils.formatter2("%-20x", self.members["ph_memsz"])
        out += utils.formatter2("%-10x", self.members["ph_align"])
        out += utils.formatter2("%-30s", self.members["ph_type"], table=ProgramHeader.PH_TYPE_T)
        out += utils.formatter2("%-10s", self.members["ph_flags"], table=ProgramHeader.PH_FLAGS_T, mask=True)
        return out

