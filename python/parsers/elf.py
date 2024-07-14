
import struct
import sys
from intelhex import IntelHex
import utils


class Packer:
    is_64bit = False
    is_little_endian = False

    def set(is_64bit, is_little_endian):
        Packer.is_64bit = is_64bit
        Packer.is_little_endian = is_little_endian

    def unpack(buffer):
        return utils.unpack(buffer, little_endian=Packer.is_little_endian)

    def pack(data, size):
        return utils.pack(data, size, little_endian=Packer.is_little_endian)

    def get(key, override=False):
        if not override and Packer.is_64bit == True:
            return key.upper() + "_64SZ"
        return key.upper() + "_SZ"


def formatter2(format, value, table=None, mask=False):
    _value = value
    if table != None:
        out = ""
        if mask:
            for flag in table:
                if (_value & flag) == flag:
                    out += table[_value & flag] + " "
                    _value = (_value & ~flag)

                if _value == 0:
                    break
            
            if _value !=0:
                out += hex(_value)
            
            if out == "":
                out += hex(_value)
            _value = out
        else:
            if _value in table:
                _value = table[_value]

       
    return format%_value

def formatter(string, value, table=None, hex=False, mask=False):
    if table != None:
        _value = value
        out = ""
        if mask:
            for flag in table:
                if (_value & flag) == flag:
                    out += table[_value & flag] + " "
                    _value = (_value & ~flag)
                if _value == 0:
                    break
        else:
            if _value in table:
                out = table[_value]
                _value = 0

        if out == "" or _value != 0:
            return f"{string:40} {value:x}\n"
        return f"{string:40} {out}\n"
    elif hex:
        return f"{string:40} {value:x}\n"
    else:
        return f"{string:40} {value}\n"


class Segment:
    
    def __init__(self, start_address, data):
        self.data = data
        self.start_address = start_address
        
    def get_address(self):
        return self.start_address
    
    def get_data(self):
        return self.data

class Crc32:
    ''' Corresponds to address:4,crc32:Li,0xFFFFFFFFF;start_address-end_address
    '''

    def __init__(self, size=4, unit_size=4, start_value=0xFFFFFFFF):
        self.size = size
        self.unit_size = unit_size
        self.start_value = start_value
        self.table = []
        self._create_lookup_table()

    def _mirror(self, orig, size):
        one = 1
        d = 0
        r = 0
        for d in range(8 * size):

            if (orig & (one << d)):
                r |= ((one << (8 * size - 1)) >> d)

        return r

    def _create_lookup_table(self):
        rem = 0
        mask = 1
        left = (self.size - 1) * 8
        mask <<= (self.size * 8 - 1)
        for i in range(256):
            rem = i << left
            for j in range(8):
                if (rem & mask):
                    rem = (rem << 1) ^ 0x4C11DB7
                else:
                    rem <<= 1

            self.table.append(rem)

    def calculate(self, buf):
        mSum = self.start_value
        stack = []
        for byte in buf:
            stack.append(byte)
            if len(stack) == self.unit_size:
                while len(stack) > 0:
                    index = ((mSum >> 24) ^ stack.pop()) & 0xFF
                    t = self.table[index]
                    mSum = (t ^ (mSum << 8)) & 0xFFFFFFFF

        return mSum


def update(source, destination, offset):
    for idx in range(len(source)):
        if (offset + idx) >= len(destination):
            destination.extend(source[idx:])
        else:
            destination[offset + idx] = source[idx]


class SymTable:
    def __init__(self, section_header, section_data, linked_str_tab_idx):
        self.symbols = []
        self.linked_str_tab_idx = linked_str_tab_idx
        count = int(section_data.get_size() / section_header.get_entry_size())
        for sidx in range(count):
            _start = sidx * section_header.get_entry_size()
            _end = _start + section_header.get_entry_size()
            symbol = Symbol()
            binary = section_data.get_data()
            symbol.unpack(binary[_start:_end])
            self.symbols.append(symbol)

    def get_entries(self):
        return self.symbols

    def get_column_titles(self):
        out = ""
        out += formatter2("%-10s","[Value]")
        out += formatter2("%-10s","[Size]")
        out += formatter2("%-20s","[Bind]")
        out += formatter2("%-20s","[Info]")
        out += formatter2("%-20s","[Other]")
        out += formatter2("%-10s","[Ndx]")
        out += formatter2("%-10s","[Name]")
        return out

    def get_strtab_idx(self):
        return self.linked_str_tab_idx
    
class DynamicEntry:
    D_TAG = 0x00
    D_TAG_SZ = 4
    D_VAL_SZ = 2
    D_PTR_SZ = 4
    D_OFF_SZ = 4

    D_TAG_64SZ = 8
    D_VAL_64SZ = 2
    D_PTR_64SZ = 4

    D_TAG_T = {
                0: 'DT_NULL',
                1: 'DT_NEEDED',
                2: 'DT_PLTRELSZ',
                4: 'DT_HASH',
                5: 'DT_STRTAB',
                6: 'DT_SYMTAB',
    }



    def __init__(self, d_tag=0, d_val=0, d_ptr=0, d_off=0):
        if Packer.is_64bit:
            self.members = {
                "d_tag": d_tag,
                "d_val": d_val,
                "d_ptr": d_ptr
            }
        else:
            self.members = {
                "d_tag": d_tag,
                "d_val": d_val,
                "d_ptr": d_ptr,
                "d_off": d_off
            }

    def unpack(self, buffer):
        offset = DynamicEntry.D_TAG
        for key in self.members:
            self.members[key] = Packer.unpack(buffer[offset:offset + getattr(DynamicEntry, Packer.get(key))])
            offset += getattr(DynamicEntry, Packer.get(key))

    def pack(self):
        buffer = []
        for key in self.members:
            buffer.extend(Packer.pack(self.members[key], getattr(DynamicEntry, Packer.get(key))))
        return buffer

    def __str__(self):
        out=""
        out += formatter2("%-20s", self.members["d_tag"],  table=DynamicEntry.D_TAG_T)
        out += formatter2("%-10x", self.members["d_val"])
        out += formatter2("%-10x", self.members["d_ptr"])
        out += formatter2("%-20s", self.members.get("d_off", "NONE"))
        return out

class Dynamic:
    def __init__(self, section_header, section_data):
        self.entries = []
        count = int(section_data.get_size() / section_header.get_entry_size())
        for sidx in range(count):
            _start = sidx * section_header.get_entry_size()
            _end = _start + section_header.get_entry_size()
            entry = DynamicEntry()
            binary = section_data.get_data()
            entry.unpack(binary[_start:_end])
            self.entries.append(entry)

    def get_column_titles(self):
        out = ""
        out += formatter2("%-20s","[Tag]")
        out += formatter2("%-10s","[Value]")
        out += formatter2("%-10s","[Pointer]")
        out += formatter2("%-20s","[Offset]")
        return out

    def get_entries(self):
        return self.entries
    
class StringTable:

    def __init__(self, section_header, section_data):
        self.section_header= section_header
        self.section_data = section_data

    def find_string(self,str_idx):
        return utils.readstring(self.section_data.get_data(), str_idx)
    
    def add_string(self):
        str_idx = self.section_data.get_size()
        update(f".partial_{str_idx:x}\0".encode(), self.section_data.get_data(), str_idx)
        self.section_header.set_size(self.section_data.get_size())
        return str_idx

class Symbol:
    ST_NAME = 0x0
    ST_NAME_SZ = 0x4
    ST_VALUE_SZ = 0x4
    ST_SIZE_SZ = 0x4
    ST_INFO_SZ = 0x1
    ST_OTHER_SZ = 0x1
    ST_SHNDX_SZ = 0x4

    ST_NAME_64SZ = 0x4
    ST_INFO_64SZ = 0x1
    ST_OTHER_64SZ = 0x1
    ST_SHNDX_64SZ = 0x2
    ST_VALUE_64SZ = 0x8
    ST_SIZE_64SZ = 0x8

    ST_INFO_BIND_M = 0xF0
    ST_INFO_TYPE_M = 0x0F

    ST_BIND_T = {
                0x00: "STB_LOCAL",
                0x10: "STB_GLOBAL",
                0x20: "STB_WEAK",
                0xA0: "STB_LOOS",
                0xC0: "STB_HIOS",
                0xD0: "STB_LOPROC",
                0xF0: "STB_HIPROC"
    }

    ST_OTHER_T = {
                0: "STV_DEFAULT",
                1: "STV_INTERNAL",
                2: "STV_HIDDEN",
                3: "STV_PROTECTED",
                4: "STV_EXPORTED",
                5: "STV_SINGLETON",
                6: "STV_ELIMINATE"
    }

    ST_TYPE_T = {
                0: "STT_NOTYPE",
                1: "STT_OBJECT",
                2: "STT_FUNC",
                3: "STT_SECTION",
                4: "STT_FILE",
                5: "STT_COMMON",
                6: "STT_TLS",
                10: "STT_LOOS",
                12: "STT_HIOS",
                13: "STT_LOPROC",
                14: "STT_SPARC_REGISTER",
                15: "STT_HIPROC"
    }

    ST_SHNDX_T = {
                0x0000: "SHN_UNDEF",
                0xFFF1: "SHN_ABS",
                0xFF00: "SHN_LOPROC",
                0xFF1F: "SHN_HIPROC",
                0xFF20: "HN_LIVEPATCH",
                0xFFF1: "SHN_ABS",
                0xFFF2: "SHN_COMMON",
                0xFFFF: "SHN_HIRESERVE"
    }

    def __init__(self, st_name="", st_value=0, st_size=0, st_info=0, st_other=0, st_shndx=0):
        if Packer.is_64bit:
            self.members = {
                "st_name": st_name,
                "st_info": st_info,
                "st_other": st_other,
                "st_shndx": st_shndx,
                "st_value": st_value,
                "st_size": st_size,
            }
        else:
            self.members = {
                "st_name": st_name,
                "st_value": st_value,
                "st_size": st_size,
                "st_info": st_info,
                "st_other": st_other,
                "st_shndx": st_shndx
            }

        self.syminfo = {
            "si_boundto":0,
            "si_flags":0
        }

    def unpack(self, buffer):
        offset = Symbol.ST_NAME
        for key in self.members:
            self.members[key] = Packer.unpack(buffer[offset:offset + getattr(Symbol, Packer.get(key))])
            offset += getattr(Symbol, Packer.get(key))

    def pack(self):
        buffer = []
        for key in self.members:
            buffer.extend(Packer.pack(self.members[key], getattr(Symbol, Packer.get(key))))
        return buffer
   
    
    def get_name_idx(self):
        return self.members["st_name"]
    
    def get_strtab_idx(self):
        return self.members["st_shndx"]

    def set_resolved_name(self, name):
        self.members["st_name"] = name

    def __str__(self):
        out=""
        out += formatter2("%-010x", self.members["st_value"])
        out += formatter2("%-10s", self.members["st_size"])
        out += formatter2("%-20s", self.members["st_info"]&Symbol.ST_INFO_BIND_M, table=Symbol.ST_BIND_T)
        out += formatter2("%-20s", self.members["st_info"]&Symbol.ST_INFO_TYPE_M, table=Symbol.ST_TYPE_T)
        out += formatter2("%-20s", self.members["st_other"], table=Symbol.ST_OTHER_T)
        out += formatter2("%-10s", self.members["st_shndx"], table=Symbol.ST_SHNDX_T)
        out += formatter2("%-10s", self.members["st_name"])
        return out
    
    
class SectionHeader:
    '''Section Header
    '''
    SH_NAME = 0x00  # .shstrab offset
    SH_NAME_OFF_SZ = 4
    SH_TYPE_SZ = 4
    SH_FLAGS_SZ = 4
    SH_ADDR_SZ = 4
    SH_OFFSET_SZ = 4
    SH_SIZE_SZ = 4
    SH_LINK_SZ = 4
    SH_INFO_SZ = 4
    SH_ADDRALIGN_SZ = 4
    SH_ENTSIZE_SZ = 4

    SH_NAME_OFF_64SZ = 4
    SH_TYPE_64SZ = 4
    SH_FLAGS_64SZ = 8
    SH_ADDR_64SZ = 8
    SH_OFFSET_64SZ = 8
    SH_SIZE_64SZ = 8
    SH_LINK_64SZ = 4
    SH_INFO_64SZ = 4
    SH_ADDRALIGN_64SZ = 8
    SH_ENTSIZE_64SZ = 8

    SH_TYPE_T = {0x00: "SHT_NULL (Unused)",
                 0x01: "SHT_PROGBITS (Program data)",
                 0x02: "SHT_SYMTAB (Symbol table)",
                 0x03: "SHT_STRTAB (String table)",
                 0x04: "SHT_RELA (Relocation entries with addends)",
                 0x05: "SHT_HASH (Symbol hash table)",
                 0x06: "SHT_DYNAMIC (Dynamic linking inmformation)",
                 0x07: "SHT_NOTE (Notes)",
                 0x08: "SHT_NOBITS (bss)",
                 0x09: "SHT_REL (Relocation entries, no addends)",
                 0x0A: "SHT_SHLIB (Reserved)",
                 0x0B: "SHT_DYNSYM (Dynamic linker symbol table)",
                 0x0E: "SHT_INIT_ARRAY (Array of constructors)",
                 0x0F: "SHT_FINI_ARRAY (Array of destructors)",
                 0x10: "SHT_PREINIT_ARRAY (Array of pre-constructors)",
                 0x11: "SHT_GROUP (Section group)",
                 0x12: "SHT_SYMTAB_SHDX (Extended section indices)",
                 0x13: "SHT_NUM (Number of defined types)",
                 0x60000000: "Start OS-specific"}


    _FLAGS_FULL = {0x01: "SHF_WRITE (Writable)",
                  0x02: "SHF_ALLOC (Occupies memory during execution)",
                  0x04: "SHF_EXECINSTR (Executable)",
                  0x10: "SHF_MERGE (Might be merged)",
                  0x20: "SHF_STRINGS (Null-terminated strings)",
                  0x40: "SHF_INFO_LINK (\'sh_info\' contains SHT index)",
                  0x80: "SHF_LINK_ORDER (Preserved order after combining)",
                  0x100: "SHF_OS_NONCONFORMING (Non-standard OS specific handling required)",
                  0x200: "SHF_GROUP (Section is member of a group)",
                  0x400: "SHF_TLS (Section hold thread-local data)",
                  0x0FF00000: "SHF_MASKOS (OS-specific)",
                  0xF0000000: "SHF_MASKPROC (Processor-specific)",
                  0x800: "SHF_COMPRESSED (Compressed)",
                  0x4000000: "SHF_ORDERED (Special ordering requirement (Solaris))",
                  0x8000000: "SHF_EXCLUDE (Section is excluded unless referenced or allocated (Solaris))"}

    SH_FLAGS_T = {0x01: "SHF_WRITE",
                  0x02: "SHF_ALLOC",
                  0x04: "SHF_EXECINSTR",
                  0x10: "SHF_MERGE",
                  0x20: "SHF_STRINGS",
                  0x40: "SHF_INFO_LINK",
                  0x80: "SHF_LINK_ORDER",
                  0x100: "SHF_OS_NONCONFORMING",
                  0x200: "SHF_GROUP",
                  0x400: "SHF_TLS",
                  0x0FF00000: "SHF_MASKOS",
                  0xF0000000: "SHF_MASKPROC",
                  0x800: "SHF_COMPRESSED",
                  0x4000000: "SHF_ORDERED",
                  0x8000000: "SHF_EXCLUDE"}
    TYPE_SHT_NULL = 0x00
    TYPE_SHT_PROGBITS = 0x01
    TYPE_SHT_SYMTAB = 0x02
    TYPE_SHT_STRTAB = 0x03
    TYPE_SHT_NOBITS = 0x08
    TYPE_SHT_DYNSYM = 0x0B
    TYPE_SHT_DYNAMIC = 0x06
    FLAGS_SHF_ALLOC = 0x02
    FLAGS_SHF_EXECINSTR = 0x04

    def __init__(self, sh_name_off=0, sh_type=0, sh_flags=0, sh_size=0, sh_offset=0, sh_addr=0):
        self.name = ""
        if Packer.is_64bit:
            self.members = {
                "sh_name_off": sh_name_off,
                "sh_type": sh_type,
                "sh_flags": sh_flags,
                "sh_addr": sh_addr,
                "sh_offset": sh_offset,
                "sh_size": sh_size,
                "sh_link": 0,
                "sh_info": 0,
                "sh_addralign": 0,
                "sh_entsize": 0
            }

        else:
            self.members = {
                "sh_name_off": sh_name_off,
                "sh_type": sh_type,
                "sh_flags": sh_flags,
                "sh_addr": sh_addr,
                "sh_offset": sh_offset,
                "sh_size": sh_size,
                "sh_link": 0,
                "sh_info": 0,
                "sh_addralign": 0,
                "sh_entsize": 0
            }

    def unpack(self, buffer):
        offset = SectionHeader.SH_NAME
        for key in self.members:
            self.members[key] = Packer.unpack(buffer[offset:offset + getattr(SectionHeader, Packer.get(key))])
            offset += getattr(SectionHeader, Packer.get(key))

    def pack(self):
        buffer = []
        for key in self.members:
            buffer.extend(Packer.pack(self.members[key], getattr(SectionHeader, Packer.get(key))))
        return buffer

    def get_size(self):
        return self.members["sh_size"]
    
    def get_entry_size(self):
        return self.members["sh_entsize"]

    def get_offset(self):
        return self.members["sh_offset"]

    def get_type(self):
        return self.members["sh_type"]

    def get_align(self):
        return self.members["sh_addralign"]

    def get_addr(self):
        return self.members["sh_addr"]
    
    def get_link(self):
        return self.members["sh_link"]

    def is_allocatable(self):
        return self.members["sh_flags"] & SectionHeader.FLAGS_SHF_ALLOC

    def set_offset(self, offset):
        self.members["sh_offset"] = offset

    def get_name_off(self):
        return self.members["sh_name_off"]

    def set_size(self, size):
        self.members["sh_size"] = size

    def resolve_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_column_titles():
        out = ""
        out += formatter2("%-10s","[Offset]")
        out += formatter2("%-20s","[File offset]")
        out += formatter2("%-20s","[File size]")
        out += formatter2("%-20s","[Physical address]")
        out += formatter2("%-10s","[Link]")
        out += formatter2("%-10s","[Info]")
        out += formatter2("%-20s","[Entry Size]")
        out += formatter2("%-30s","[Type]")
        out += formatter2("%-30s","[Flags]")
        return out
    
    def __str__(self):
        out = ""
        out += formatter2("%-10s", self.members["sh_name_off"])
        out += formatter2("%-20x", self.members["sh_offset"])
        out += formatter2("%-20x", self.members["sh_size"])
        out += formatter2("%-20x", self.members["sh_addr"])
        out += formatter2("%-10x", self.members["sh_link"])
        out += formatter2("%-10x", self.members["sh_info"])
        out += formatter2("%-20x", self.members["sh_entsize"])
        out += formatter2("%-30s", self.members["sh_type"], table=SectionHeader.SH_TYPE_T)
        out += formatter2("%-30s", self.members["sh_flags"], table=SectionHeader.SH_FLAGS_T, mask=True)
        return out


class ProgramHeader:
    '''Program header
    '''
    PH_TYPE = 0x00
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
    PT_PHDR = 0x00000006
    PH_TYPE_T = {0x00000000: "PT_NULL (Unused)",
                 0x00000001: "PT_LOAD (Loadable segment)",
                 0x00000002: "PT_DYNAMIC (Dynamic linking information)",
                 0x00000003: "PT_INTERP (Interpreter information)",
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
        if Packer.is_64bit:
            self.members = {"ph_type": ph_type,
                            "ph_flags": ph_flags,
                            "ph_offset": ph_offset,
                            "ph_vaddr": ph_vaddr,
                            "ph_paddr": ph_paddr,
                            "ph_filesz": ph_filesz,
                            "ph_memsz": ph_memsz,
                            "ph_align": ph_align}

        else:
            self.members = {"ph_type": ph_type,
                            "ph_offset": ph_offset,
                            "ph_vaddr": ph_vaddr,
                            "ph_paddr": ph_paddr,
                            "ph_filesz": ph_filesz,
                            "ph_memsz": ph_memsz,
                            "ph_flags": ph_flags,
                            "ph_align": ph_align}

    def unpack(self, buffer):
        offset = ProgramHeader.PH_TYPE
        for key in self.members:
            self.members[key] = Packer.unpack(buffer[offset:offset + getattr(ProgramHeader,  Packer.get(key))])
            offset += getattr(ProgramHeader,  Packer.get(key))

    def pack(self):
        buffer = []
        for key in self.members:
            buffer.extend(Packer.pack(self.members[key], getattr(ProgramHeader,  Packer.get(key))))
        return buffer

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

    def set_offset(self, offset):
        self.members["ph_offset"] = offset

    def get_column_titles():
        out = ""
        out += formatter2("%-20s","[File offset]")
        out += formatter2("%-20s","[File size]")
        out += formatter2("%-20s","[Physical address]")
        out += formatter2("%-20s","[Virtual address]")
        out += formatter2("%-20s","[Memory size]")
        out += formatter2("%-10s","[Align]")
        out += formatter2("%-30s","[Type]")
        out += formatter2("%-10s","[Flags]")
        return out
    
    def __str__(self):
        out = ""
        out += formatter2("%-20x", self.members["ph_offset"])
        out += formatter2("%-20x", self.members["ph_filesz"])
        out += formatter2("%-20x", self.members["ph_paddr"])
        out += formatter2("%-20x", self.members["ph_vaddr"])
        out += formatter2("%-20x", self.members["ph_memsz"])
        out += formatter2("%-10x", self.members["ph_align"])
        out += formatter2("%-30s", self.members["ph_type"], table=ProgramHeader.PH_TYPE_T)
        out += formatter2("%-10s", self.members["ph_flags"], table=ProgramHeader.PH_FLAGS_T, mask=True)
        return out



class Abreviation:

    DW_AT_PRODUCER_SZ = 4
    DW_AT_LANGUAGE_SZ = 1
    DW_AT_NAME_SZ = 4
    DW_AT_COMP_DIR_SZ = 4
    DW_AT_LOW_PC_SZ = 8
    DW_AT_HIGH_PC_SZ = 8
    DW_AT_STMT_SZ = 4

    def __init__(self, type):
        pass


    

class CompileUnitHeader:

    CU_POINTER_SIZE_OFFSET = 0
    CU_POINTER_SIZE_SZ = 1
    CU_ABBREV_OFFSET_SZ = 4

    CU_POINTER_SIZE_64SZ = 1
    CU_ABBREV_OFFSET_64SZ = 4

    def __init__(self):
        self.members = {
                        "cu_pointer_size": 0,
                        "cu_abbrev_offset": 0
                        }
        
    def unpack(self, buffer):
        offset = CompileUnitHeader.CU_POINTER_SIZE_OFFSET
        for key in self.members:
            self.members[key] = Packer.unpack(buffer[offset:offset + getattr(CompileUnitHeader,  Packer.get(key))])
            offset += getattr(CompileUnitHeader,  Packer.get(key))
             
    def pack(self):
        buffer = []
        for key in self.members:
            buffer.extend(Packer.pack(self.members[key], getattr(CompileUnitHeader,  Packer.get(key))))
        return buffer
    
    def get_abbrev_offset(self):
        return self.members["cu_abbrev_offset"]
    
    def get_header_size(self):
        return CompileUnitHeader.CU_POINTER_SIZE_SZ + CompileUnitHeader.CU_ABBREV_OFFSET_SZ

    def __str__(self):
        out = ""
        out += formatter("Pointer Size", self.members["cu_pointer_size"])
        out += formatter("Abbrev. Offset", self.members["cu_abbrev_offset"])
        return out

class CompileUnit:
    CU_LENGTH_OFFSET = 0

    CU_LENGTH_SZ = 4
    CU_VERSION_SZ = 2
    CU_UNIT_TYPE_SZ = 1

    DW_UNIT_TYPES = {
        1: "DW_UT_COMPILE"
    }

    SUPPORTED_VERSIONS = [5]

    def __init__(self):
        self.abbreviations = []
        self.members = {
                        "cu_length": 0,
                        "cu_version": 0,
                        "cu_unit_type": 0
        }

        self.cu_header = CompileUnitHeader()
     
    def unpack(self, buffer):
        offset = CompileUnit.CU_LENGTH_OFFSET
        for key in self.members:
            self.members[key] = Packer.unpack(buffer[offset:offset + getattr(CompileUnit,  Packer.get(key, override=True))])
            offset += getattr(CompileUnit,  Packer.get(key, override=True))

        if self.members["cu_version"] in CompileUnit.SUPPORTED_VERSIONS and self.members["cu_unit_type"] in CompileUnit.DW_UNIT_TYPES:
            self.cu_header.unpack(buffer[offset:])

            # Init values before parsing abbreviations
            header_size = self.cu_header.get_header_size() 
            abbrev_offset = self.cu_header.get_abbrev_offset() 
            offset += abbrev_offset +  header_size 
            length = self.members["cu_length"]

            #
            buffer[offset: offset + length]
        else:
            raise Exception(f'ERROR: unsupported Compilation Unit version:{self.members["cu_version"]} unit:{self.members["cu_unit_type"]}')
    def pack(self):
        buffer = []
        for key in self.members:
            buffer.extend(Packer.pack(self.members[key], getattr(CompileUnit,  Packer.get(key))))

        buffer.extend(self.cu_header.pack())
        return buffer

    def __str__(self):
        out = ""
        out += formatter("Length", self.members["cu_length"], hex=True)
        out += formatter("Version", self.members["cu_version"])
        out += formatter("Unit Type", self.members["cu_unit_type"], table=CompileUnit.DW_UNIT_TYPES)
        out += str(self.cu_header)
        return out
    
        
class Dwarf:
    def __init__(self):
        self.entries = []
        self.section_headers = []
        self.section_data = []

    def add_debug_section(self, sh, sh_data):
        self.section_headers.append(sh)
        self.section_data.append(sh_data)

    def get_entries(self):
        return self.entries

    def get_column_titles(self):
        return ""

    def parse_debug_info(self):
        for sh, sh_data in zip(self.section_headers, self.section_data):
            if "debug_info" in sh.get_name():
                unit = CompileUnit()
                unit.unpack(sh_data.get_data())
                self.entries.append(unit)


class ElfIdent:
    ELF_MAGIC = 0x464C457F
    EI_MAGIC = 0x0
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
        self.members = {
            "ei_magic": 0,
            "ei_class": 0,
            "ei_data": 0,
            "ei_version": 0,
            "ei_osabi": 0,
            "ei_abiversion": 0,
            "ei_pad": 0
        }

    def unpack(self, buffer):
        offset = ElfIdent.EI_MAGIC
        for key in self.members:
            self.members[key] = utils.unpack(buffer[offset:offset + getattr(ElfIdent,  Packer.get(key))])
            offset += getattr(ElfIdent, Packer.get(key))

        if self.members["ei_magic"] != ElfIdent.ELF_MAGIC:
            raise Exception("Not an Elf file")

        # Update Packer settings
        Packer.set(is_little_endian=(self.members['ei_data'] == ElfIdent.DATA_LITTLE_ENDIAN),
                   is_64bit=(self.members['ei_class'] == ElfIdent.CLASS_64_BIT))

    def pack(self):
        buffer = []
        for key in self.members:
            buffer.extend(utils.pack(self.members[key], getattr(ElfIdent,  Packer.get(key))))
        return buffer

    def get_size(self):
        return sum([getattr(ElfIdent,  Packer.get(key)) for key in self.members])

    def __str__(self):
        out = "\n[Elf Identification]\n"
        out += formatter("Class:", self.members['ei_class'], table=ElfIdent.EI_CLASS_T)
        out += formatter("Data:", self.members['ei_data'], table=ElfIdent.EI_DATA_T)
        out += formatter("Version:", self.members['ei_version'], table=ElfIdent.EI_VERSION_T)
        out += formatter("OSABI:", self.members['ei_osabi'], table=ElfIdent.EI_OSABI_T)
        out += formatter("Abi Version:", self.members['ei_abiversion'], table=ElfIdent.EI_ABIVERSION_T)
        return out


class ElfHeader:
    E_TYPE = 16
    E_TYPE_SZ = 2
    E_MACHINE_SZ = 2
    E_VERSION_SZ = 4
    E_ENTRY_SZ = 4
    E_PH_OFF_SZ = 4
    E_SH_OFF_SZ = 4
    E_FLAGS_SZ = 4
    E_EH_SIZE_SZ = 2
    E_PH_ENT_SIZE_SZ = 2
    E_PH_COUNT_SZ = 2
    E_SH_ENT_SIZE_SZ = 2
    E_SH_COUNT_SZ = 2
    E_SH_STRNDX_SZ = 2

    E_TYPE_64SZ = 2
    E_MACHINE_64SZ = 2
    E_VERSION_64SZ = 4
    E_ENTRY_64SZ = 8
    E_PH_OFF_64SZ = 8
    E_SH_OFF_64SZ = 8
    E_FLAGS_64SZ = 4
    E_EH_SIZE_64SZ = 2
    E_PH_ENT_SIZE_64SZ = 2
    E_PH_COUNT_64SZ = 2
    E_SH_ENT_SIZE_64SZ = 2
    E_SH_COUNT_64SZ = 2
    E_SH_STRNDX_64SZ = 2

    E_TYPE_T = {0x00: "ET_NONE (Unknown)", 0x01: "ET_REL (Relocatable file)", 0x02: "ET_EXEC (Executable file)", 0x03: "ET_DYN (Shared object)", 0x04: "ET_CORE (Core file)", 0xFE00: "ET_LOOS (OS Specific)", 0xFEFF: "ET_HIOS (OS Specific)", 0xFF00: "ET_LOPROC (CPU specific)", 0xFFFF: "ET_HIPROC (CPU specific)"}
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
        self.members = {
            "e_type": 0,
            "e_machine": 0,
            "e_version": 0,
            "e_entry": 0,
            "e_ph_off": 0,
            "e_sh_off": 0,
            "e_flags": 0,
            "e_eh_size": 0,
            "e_ph_ent_size": 0,
            "e_ph_count": 0,
            "e_sh_ent_size": 0,
            "e_sh_count": 0,
            "e_sh_strndx": 0
        }

    def unpack(self, buffer):
        offset = ElfHeader.E_TYPE
        for key in self.members:
            self.members[key] = Packer.unpack(buffer[offset:offset + getattr(ElfHeader, Packer.get(key))])
            offset += getattr(ElfHeader,  Packer.get(key))

    def pack(self):
        buffer = []
        for key in self.members:
            buffer.extend(Packer.pack(self.members[key], getattr(ElfHeader, Packer.get(key))))
        return buffer

    def set_ph_offset(self, ph_offset):
        self.members["e_ph_off"] = ph_offset

    def set_sh_offset(self, sh_offset):
        self.members["e_sh_off"] = sh_offset

    def get_size(self):
        return self.members["e_eh_size"]

    def get_ph_count(self):
        return self.members["e_ph_count"]

    def get_sh_count(self):
        return self.members["e_sh_count"]

    def set_sh_count(self, sh_count):
        self.members["e_sh_count"] = sh_count

    def set_ph_count(self, ph_count):
        self.members["e_ph_count"] = ph_count

    def get_sh_ent_sz(self):
        return self.members["e_sh_ent_size"]

    def get_ph_ent_sz(self):
        return self.members["e_ph_ent_size"]

    def get_ph_off(self):
        return self.members["e_ph_off"]

    def get_sh_off(self):
        return self.members["e_sh_off"]

    def get_stridx(self):
        return self.members["e_sh_strndx"]

    def __str__(self):
        out = "\n[Elf Header]\n"
        out += formatter("Type:", self.members['e_type'], table=ElfHeader.E_TYPE_T)
        out += formatter("Machine:", self.members['e_machine'], table=ElfHeader.E_MACHINE_T)
        out += formatter("Version:", self.members['e_version'], table=ElfHeader.E_VERSION_T)
        out += formatter("Entry point address:", self.members['e_entry'], hex=True)
        out += formatter("Program headers file offset:", self.members['e_ph_off'], hex=True)
        out += formatter("Section headers file offset:", self.members['e_sh_off'], hex=True)
        out += formatter("Flags:", self.members['e_flags'], hex=True)
        out += formatter("Size of this header:", self.members['e_eh_size'])
        out += formatter("Size of program headers:", self.members['e_ph_ent_size'], hex=True)
        out += formatter("Number of program headers:", self.members['e_ph_count'])
        out += formatter("Size of section headers:", self.members['e_sh_ent_size'], hex=True)
        out += formatter("Number of section headers:", self.members['e_sh_count'])
        out += formatter("Section header string table index:", self.members['e_sh_strndx'], hex=True)
        return out


class SectionData:
    '''SectionData
    '''

    def __init__(self, data):
        self.data = data
        self.section_headers = []
        self.program_headers = []

    def update(self, offset):
        base_offset = self.get_offset()

        if base_offset != offset:
            diff_off = offset - base_offset
            self._update_section_headers(diff_off)
            self._update_program_headers(diff_off)

    def _update_section_headers(self, diff_offset):
        for section in self.section_headers:
            original_offset = section.get_offset()
            updated_offset = original_offset + diff_offset
            section.set_offset(updated_offset)

    def _update_program_headers(self, diff_offset):
        for program in self.program_headers:
            original_offset = program.get_offset()
            updated_offset = original_offset + diff_offset
            program.set_offset(updated_offset)

    def get_address_range(self):
        '''Get Address Range
        '''
        if self.program_headers:
            program_header = self.program_headers[0]
            start_address = program_header.get_paddr()
            end_address = start_address + program_header.get_memsz()
            return start_address, end_address

        return 0, 0

    def get_offset(self):
        '''Get offset of data
        '''
        offset = self.section_headers[0].get_offset()
        for section in self.section_headers:
            if section.get_offset() < offset:
                offset = section.get_offset()
        return offset

    def get_addr(self):
        '''Get offset of data
        '''
        address = self.section_headers[0].get_addr()
        for section in self.section_headers:
            if section.get_addr() < address:
                address = section.get_get_addrffset()
        return address

    def get_vaddr(self):
        '''Get offset of data
        '''
        if self.program_headers:
            address = self.program_headers[0].get_vaddr()
            for program in self.program_headers:
                if program.get_vaddr() < address:
                    address = program.get_vaddr()
            return address
        return 0

    def get_size(self):
        '''Get Size
        '''
        return len(self.data)

    def get_data(self):
        '''Get Data
        '''
        return self.data

    def get_alignment(self):
        '''Get Alignment
        '''
        alignment = 0
        for section in self.section_headers:
            if section.get_align() > alignment:
                alignment = section.get_align()
        return alignment

    def add_section_header(self, sh):
        '''Add section header
        '''
        self.section_headers.append(sh)

    def add_program_header(self, ph):
        '''Add program header
        '''
        self.program_headers.append(ph)

    def get_section_headers(self):
        return self.section_headers


class ElfParser:
    """Elf Parser
       https://en.wikipedia.org/wiki/Executable_and_Linkable_Format
       https://docs.oracle.com/cd/E19683-01/816-1386/chapter6-83432/index.html
       https://www.uclibc.org/docs/elf-64-gen.pdf
    """

    def __init__(self, buffer):
        self.binary = buffer
        self.section_data = []
        self.shstrtab = None
        self.symtab = None
        self.dynsymtab = None
        self.dynamic = None
        self.dwarf  = Dwarf()
        self.strtab = {}

        self.elf_ident = self._load_identification()
        self.elf_header = self._load_elf_header()
        self.program_headers = self._load_program_headers()
        self.section_headers = self._load_section_headers()

        self._load_section_data()
        self._load_symbols()
        self._load_debug_info()

        self.crc32 = Crc32()

    def _load_identification(self):
        ident = ElfIdent()
        ident.unpack(self.binary)
        return ident

    def _load_elf_header(self):
        header = ElfHeader()
        header.unpack(self.binary)
        return header

    def _load_symbols(self):
        '''Loads symbols .elf
        '''
        if self.dynsymtab:
            strtab = self.strtab[self.dynsymtab.get_strtab_idx()]
            for _idx, symbol in enumerate(self.dynsymtab.get_entries()):
                symbol.set_resolved_name(strtab.find_string(symbol.get_name_idx()))

        if self.symtab:
            strtab = self.strtab[self.symtab.get_strtab_idx()]
            for _idx, symbol in enumerate(self.symtab.get_entries()):
                symbol.set_resolved_name(strtab.find_string(symbol.get_name_idx()))

    def _load_debug_info(self):
        self.dwarf.parse_debug_info()

    def _load_program_headers(self):
        '''Loads program headers from .elf
        '''
        program_headers = []
        for pidx in range(self.elf_header.get_ph_count()):
            _start = self.elf_header.get_ph_off() + pidx * self.elf_header.get_ph_ent_sz()
            _end = _start + self.elf_header.get_ph_ent_sz()
            ph = ProgramHeader()
            ph.unpack(self.binary[_start:_end])
            program_headers.append(ph)
        return program_headers

    def _load_section_headers(self):
        '''Loads section headers from .elf
        '''
        section_headers = []
        for sidx in range(self.elf_header.get_sh_count()):
            _start = self.elf_header.get_sh_off() + sidx * self.elf_header.get_sh_ent_sz()
            _end = _start + self.elf_header.get_sh_ent_sz()
            sh = SectionHeader()
            sh.unpack(self.binary[_start:_end])
            section_headers.append(sh)
        return section_headers

    def _load_section_data(self):
        '''Loads section data from .elf
        '''

        for idx, sh in enumerate(self.section_headers):
            _start = sh.get_offset()
            _end = _start + sh.get_size()
            type = sh.get_type()
            if type not in [SectionHeader.TYPE_SHT_NOBITS, SectionHeader.TYPE_SHT_NULL]:
                sh_data = SectionData(self.binary[_start:_end])
                sh_data.add_section_header(sh)
                self.section_data.append(sh_data)

                ## strtab
                if type == SectionHeader.TYPE_SHT_STRTAB:
                    strtab = StringTable(sh, sh_data)
                    self.strtab[idx] = strtab
                    if idx == self.elf_header.get_stridx():
                        self.shstrtab = strtab
                    
                ## symtab
                elif type == SectionHeader.TYPE_SHT_SYMTAB:
                    if self.symtab is not None:
                        print("WARNING: only one symtab is supported at the moment")
                    else:
                        self.symtab = SymTable(sh, sh_data, sh.get_link())

                elif type == SectionHeader.TYPE_SHT_DYNSYM:
                    if self.dynsymtab is not None:
                        print("WARNING: only one dynsymtab is supported at the moment")
                    else:
                        self.dynsymtab = SymTable(sh, sh_data, sh.get_link())
                
                elif type == SectionHeader.TYPE_SHT_DYNAMIC:
                    if self.dynamic is not None:
                        print("WARNING: only one dynamic is supported at the moment")
                    else:
                        self.dynamic = Dynamic(sh, sh_data)

                elif type == SectionHeader.TYPE_SHT_PROGBITS:
                    if not sh.is_allocatable():
                        self.dwarf.add_debug_section(sh, sh_data)

        if self.shstrtab is None:
            raise Exception("ERROR: Symbol or String table not found")

        else:
            # Resolve names of the section headers
            for idx, sh in enumerate(self.section_headers):
                sh.resolve_name(self.shstrtab.find_string(sh.get_name_off()))

        self._place_program_headers()

    def _place_program_headers(self):
        '''Assigns program headers to describe corresponding section data
        '''
        for ph in self.program_headers:
            found = False
            _start = ph.get_offset()
            _end = _start + ph.get_filesz()
            for data in self.section_data:
                start = data.get_offset()
                end = start + data.get_size()
                if start <= _start < _end <= end:
                    found = True
                    data.add_program_header(ph)

            if not found:
                print(f"WARNING: couldn't place {ph.get_type()} {_start:x}-{_end:x}")

    def _create_data(self, address, new_data):
        '''Create data
        '''
        section_data = self._create_section_data(new_data)
        strindex = self.shstrtab.add_string()

        offset = sum(_sd.get_size() for _sd in self.section_data)
        size = len(new_data)

        sh = self._create_section_header(strindex, size, offset, address)
        section_data.add_section_header(sh)
        self.section_headers.append(sh)

        ph = self._create_program_header(address, size, offset)
        self.program_headers.append(ph)
        section_data.add_program_header(ph)

    def _create_section_data(self, new_data):
        section_data = SectionData(new_data)
        self.section_data.append(section_data)
        return section_data

    def _create_section_header(self, strindex, size, offset, address):
        return SectionHeader(
            sh_name_off=strindex,
            sh_type=SectionHeader.TYPE_SHT_PROGBITS,
            sh_flags=(SectionHeader.FLAGS_SHF_ALLOC | SectionHeader.FLAGS_SHF_EXECINSTR),
            sh_size=size,
            sh_offset=offset,
            sh_addr=address
        )

    def _create_program_header(self, address, size, offset):
        return ProgramHeader(
            ph_type=ProgramHeader.PT_LOAD,
            ph_vaddr=address,
            ph_paddr=address,
            ph_offset=offset,
            ph_filesz=size,
            ph_memsz=size
        )

    def _overwrite_data_forward_overlap(self, source, destination, can_overwrite, offset, split_idx):
        s1, s2 = source[:split_idx], source[split_idx:]
        if can_overwrite:
            update(s2, destination, offset)

        return s1

    def _overwrite_data_backward_overlap(self, source, destination, can_overwrite, offset, split_idx):
        s1, s2 = source[:split_idx], source[split_idx:]
        if can_overwrite:
            update(s1, destination, offset)

        return s2

    def _overwrite_data_overlap(self, source, destination, can_overwrite, offset):
        if can_overwrite:
            update(source, destination, offset)

        return []

    def fill(self, start_address, end_address, byte):
        ''' Fill section
        '''
        length = end_address - start_address
        new_data = []
        new_data.extend([byte]*length)
        self.add(start_address, new_data, can_overwrite=False)

    def calculate_checksum(self, start_address, end_address, target_address):

        binary = []

        total_length = end_address - start_address
        for data in sorted(self.section_data, key=lambda x: x.get_addr()):
            s_addr, e_addr = data.get_address_range()

            if s_addr <= start_address < e_addr:
                split_idx = start_address - s_addr
                _data = data.get_data()[split_idx:]
                length = len(_data)
                if start_address + length < end_address:
                    start_address += length
                    binary.extend(_data)
                else:
                    length = end_address - start_address
                    _data = _data[:length]
                    binary.extend(_data)

                if start_address == end_address:
                    break

        if len(binary) != total_length:
            raise Exception(f"ERROR: Data not available for checksum starting from {start_address:x}")

        checksum = self.crc32.calculate(binary)
        self.add(target_address, utils.convert_int_to_list(checksum))
        return checksum

    def get_segments(self):
        segments = []
        for data in sorted(self.section_data, key=lambda x: x.get_vaddr()):
            s_addr, e_addr = data.get_address_range()
            if s_addr<e_addr:
                segments.append(Segment(s_addr, data.get_data()))
        return segments
            
    def get(self, start_address, size):
        '''Get data by address
            -> start_address: address at which the data can be found
            -> size: size of data to read
            <- : data buffer
        '''
        end_address = start_address + size
        o_data = []
        for data in sorted(self.section_data, key=lambda x: x.get_vaddr()):
             s_addr, e_addr = data.get_address_range()
             if s_addr<e_addr:
                if s_addr <= start_address < e_addr:
                    _offset_start = start_address - s_addr
                    _offset_end = start_address - s_addr + size
                    o_data.extend(data.get_data()[_offset_start:_offset_end])
                    break
        return o_data
    
    def add(self, start_address, buffer,  can_overwrite=True):
        ''' Adds data by address
            -> start_address: address to which data should be written 
            -> buffer: data to write
            -> can_overwrite: if data exists, it should be overwritten
        '''
        end_address = start_address + len(buffer)
        idx = 0
        section_data = sorted(self.section_data, key=lambda x: x.get_vaddr()) 
        while idx < len(section_data) and len(buffer) > 0:
            data = section_data[idx]
            idx += 1
            s_addr, e_addr = data.get_address_range()
            
            if s_addr<e_addr:
                # Full:
                if s_addr <= start_address < end_address <= e_addr:
                    buffer = self._overwrite_data_overlap(buffer,
                                                                     data.get_data(),
                                                                     can_overwrite,
                                                                     start_address - s_addr)
                # Partial 
                elif s_addr <= start_address < e_addr < end_address:
                    buffer = self._overwrite_data_backward_overlap(buffer,
                                                                          data.get_data(),
                                                                          can_overwrite,
                                                                          (start_address - s_addr),
                                                                          e_addr - start_address)
                    start_address = e_addr


                # Full before block 
                elif start_address < end_address <= s_addr:
                    self._create_data(start_address, buffer)
                    buffer = []

                # Partial block: forward
                elif start_address < s_addr < end_address:
                    _slice_idx = s_addr-start_address
                    _slice, buffer = buffer[:_slice_idx], buffer[_slice_idx:]
                    self._create_data(start_address, _slice)
                    start_address = s_addr
                    idx = 0
                
        # Block could not be created, probably outside of the parsed range
        if len(buffer) > 0:
            self._create_data(start_address, buffer)

    def write_data_to_file(self, elf_out="", hex_out="", bin_out=""):
        '''Write data to file
        '''
        # Initialize binary
        binary = [0] * self.elf_header.get_size()

        # Write data
        for data in sorted(self.section_data, key=lambda x: x.get_offset()):

            # Add alignment bytes
            alignment = data.get_alignment()
            if alignment > 0:
                count = len(binary) & (alignment - 1)
                if count > 0:
                    binary.extend([0] * count)

            # Update offset
            data.update(len(binary))
            binary.extend(data.get_data())

    def write_data_to_file(self, elf_out="", hex_out=""):
        '''Write data to file
        '''
        # Initialize binary
        binary = [0] * (self.elf_ident.get_size() + self.elf_header.get_size())

        self._write_section_data(binary)
        self._write_program_headers(binary)
        self._write_section_headers(binary)
        self._update_elf_ident(binary)
        self._update_elf_header(binary)

        if elf_out != "":
            with open(elf_out, 'wb') as f:
                f.write(bytes(binary))

        if hex_out != "":
            ihex = IntelHex()

            for data in sorted(self.section_data, key=lambda x: x.get_vaddr()):
                address = data.get_vaddr()
                if address == 0:
                    ihex.frombytes(data.get_data(), offset=address)
            ihex.write_hex_file(hex_out)

    def _write_program_headers(self, binary):
        self.elf_header.set_ph_count(len(self.program_headers))
        self.elf_header.set_ph_offset(len(binary))
        for program_header in self.program_headers:
            buffer = program_header.pack()
            binary.extend(buffer)

    def _write_section_headers(self, binary):
        self.elf_header.set_sh_count(len(self.section_headers))
        self.elf_header.set_sh_offset(len(binary))
        for section_header in self.section_headers:
            buffer = section_header.pack()
            binary.extend(buffer)

    def _update_elf_header(self, binary):
        update(self.elf_header.pack(), binary, self.elf_ident.get_size())

    def _update_elf_ident(self, binary):
        update(self.elf_ident.pack(), binary, 0)

    def get_section_data(self, section_name):
        for sd in self.section_data:
            for sh in sd.get_section_headers():
                string = self.shstrtab.find_string(idx = sh.get_name_off())
                if section_name in string:
                    return sd.get_data()

        raise Exception(f"ERROR: section data was not found for name {section_name}")


    def __str__(self):
        name_fmt = "%-40s"
        out = ""
        out += str(self.elf_ident)
        out += str(self.elf_header)
        out += f"\n[Program Headers] ({len(self.program_headers)})\n"
        out += name_fmt % ("[Segment Name]") + ProgramHeader.get_column_titles() + "\n"
        for idx, program_header in enumerate(self.program_headers):
            out += name_fmt % f"[{idx}][{program_header.get_vaddr():x}-{program_header.get_vaddr() +program_header.get_memsz():x}]"
            out += str(program_header)
            out +="\n"

        out += f"\n[Section Headers] ({len(self.section_headers)})\n"
        out += name_fmt % ("[Section Name]") + SectionHeader.get_column_titles() + "\n"
        for idx, section_header in enumerate(self.section_headers):
            out += name_fmt % f"[{idx}] {section_header.get_name()} [{section_header.get_offset():x}-{section_header.get_offset() + section_header.get_size():x}]"
            out += str(section_header)
            out +="\n"

        
        special_sections = {"Symtable":self.symtab,\
                            "DynSymtable":self.dynsymtab,\
                            "Dynamic":self.dynamic
                            }
        for key, tab in special_sections.items():
            if tab:
                out += f"\n[{key}] ({len(tab.get_entries())})\n"
                out += name_fmt % ("[Idx]") + tab.get_column_titles() + "\n"
                for idx, symbol in enumerate(tab.get_entries()):
                    out += name_fmt % f"[{idx}]" 
                    out += str(symbol)
                    out +="\n"   

        if self.dwarf:
            out += f"\n[Debug] ({len(self.dwarf.get_entries())})\n"
            for idx, tab in enumerate(self.dwarf.get_entries()):
                out += name_fmt % f"[{idx}]"
                out +="\n"
                out += str(tab)
                out +="\n"

        return out


if __name__ == "__main__":
    filein = sys.argv[1]
    fileout = sys.argv[2]
    fileout_hex = sys.argv[3]

    elf = ElfParser(filein)
    # print(elf)
    elf.calculate_checksum(start_address=0x8004000, end_address=0x080040C8, target_address=0x080040C8)

    elf.fill(start_address=0x8010000, end_address=0x8060000, byte=0xFF)
    elf.calculate_checksum(start_address=0x801004C, end_address=0x8060000, target_address=0x8010048)

    elf.fill(start_address=0x8060000, end_address=0x807fff8, byte=0xFF)
    elf.fill(start_address=0x807fff8, end_address=0x807fffc, byte=0x5A)
    elf.calculate_checksum(start_address=0x8060000, end_address=0x807fffc, target_address=0x807fffC)

    d = elf.get_section_data("partial")
    elf.write_data_to_file(fileout, fileout_hex)
