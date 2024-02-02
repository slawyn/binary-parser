
import struct
import sys
from intelhex import IntelHex
from utils import log, convert_int_to_list

STRUCT_FORMAT = {1: "B", 2: "H", 4: "I", 8: "Q"}


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


def read_string(data, offset):
    i = 0
    string = ""

    while data[offset + i] != 0:
        if 32 <= data[offset + i] <= 126:
            string += chr(data[offset + i])
        else:
            string += str(data[offset + i])
        i += 1

    return string


def read_binary(file_path):
    with open(file_path, 'rb') as f:
        return bytearray(f.read())


def compare(first, second):
    if len(first) != len(second):
        return False
    else:
        for fidx in range(len(first)):
            if first[fidx] != second[fidx]:
                return False

    return True


def update(source, destination, offset):
    for idx in range(len(source)):
        if (offset + idx) >= len(destination):
            destination.extend(source[idx:])
        else:
            destination[offset + idx] = source[idx]


def unpack(buffer):
    '''Unpack buffer
    '''
    idx = len(buffer)
    if idx in STRUCT_FORMAT:
        return struct.unpack("<" + STRUCT_FORMAT[idx], buffer)[0]
    return buffer


def pack(data, size):
    '''Pack data into buffer
    '''
    if size in STRUCT_FORMAT:
        return struct.pack("<" + STRUCT_FORMAT[size], data)
    return data


class SectionHeader:
    '''Section Header
    '''
    SH_NAME = 0x00
    SH_NAME_OFF_SZ = 4  # .shstrab offset
    SH_TYPE = 0x04
    SH_TYPE_SZ = 4

    SH_FLAGS = 0x08
    SH_FLAGS_SZ = 4

    SH_ADDR = 0x0C
    SH_ADDR_SZ = 4
    SH_OFFSET = 0x10
    SH_OFFSET_SZ = 4
    SH_SIZE = 0x14
    SH_SIZE_SZ = 4
    SH_LINK = 0x18
    SH_LINK_SZ = 4
    SH_INFO = 0x1C
    SH_INFO_SZ = 4
    SH_ADDRALIGN = 0x20
    SH_ADDRALIGN_SZ = 4
    SH_ENTSIZE = 0x24
    SH_ENTSIZE_SZ = 4

    TYPE_SHT_NULL = 0x00
    TYPE_SHT_PROGBITS = 0x01
    TYPE_SHT_STRTAB = 0x03
    TYPE_SHT_NOBITS = 0x08
    FLAGS_SHF_ALLOC = 0x02
    FLAGS_SHF_EXECINSTR = 0x04

    def __init__(self, sh_name_off=0, sh_type=0, sh_flags=0, sh_size=0, sh_offset=0, sh_addr=0):
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
            self.members[key] = unpack(buffer[offset:offset + getattr(SectionHeader, f"{key.upper()}_SZ")])
            offset += getattr(SectionHeader, f"{key.upper()}_SZ")

    def pack(self):
        buffer = []
        for key in self.members:
            buffer.extend(pack(self.members[key], getattr(SectionHeader, f"{key.upper()}_SZ")))
        return buffer

    def get_size(self):
        return self.members["sh_size"]

    def get_offset(self):
        return self.members["sh_offset"]

    def get_type(self):
        return self.members["sh_type"]

    def get_align(self):
        return self.members["sh_addralign"]

    def get_addr(self):
        return self.members["sh_addr"]

    def set_offset(self, offset):
        self.members["sh_offset"] = offset

    def get_name_off(self):
        return self.members["sh_name_off"]

    def set_size(self, size):
        self.members["sh_size"] = size


class ProgramHeader:
    '''Program header0x04
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

    PT_LOAD = 0x00000001

    def __init__(self, ph_type=0, ph_flags=0, ph_offset=0, ph_vaddr=0, ph_paddr=0, ph_filesz=0, ph_memsz=0, ph_align=0):
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
            self.members[key] = unpack(buffer[offset:offset + getattr(ProgramHeader, f"{key.upper()}_SZ")])
            offset += getattr(ProgramHeader, f"{key.upper()}_SZ")

    def pack(self):
        buffer = []
        for key in self.members:
            buffer.extend(pack(self.members[key], getattr(ProgramHeader, f"{key.upper()}_SZ")))
        return buffer

    def get_offset(self):
        return self.members["ph_offset"]

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


class ElfHeader:
    ELF_MAGIC = 0x464C457F
    EI_MAGIC = 0x0
    EI_MAGIC_SZ = 4
    EI_CLASS = EI_MAGIC + EI_MAGIC_SZ
    EI_CLASS_SZ = 1
    EI_DATA = EI_CLASS + EI_CLASS_SZ
    EI_DATA_SZ = 1
    EI_VERSION = EI_DATA + EI_DATA_SZ
    EI_VERSION_SZ = 1
    EI_OSABI = EI_VERSION + EI_VERSION_SZ
    EI_OSABI_SZ = 1
    EI_ABIVERSION = EI_OSABI + EI_OSABI_SZ
    EI_ABIVERSION_SZ = 1
    EI_PAD = EI_ABIVERSION + EI_ABIVERSION_SZ
    EI_PAD_SZ = 7
    E_TYPE = EI_PAD + EI_PAD_SZ
    E_TYPE_SZ = 2
    E_MACHINE = E_TYPE + E_TYPE_SZ
    E_MACHINE_SZ = 2
    E_VERSION = E_MACHINE + E_MACHINE_SZ
    E_VERSION_SZ = 4
    E_ENTRY = E_VERSION + E_VERSION_SZ
    E_ENTRY_SZ = 4
    E_PH_OFF = E_ENTRY + E_ENTRY_SZ
    E_PH_OFF_SZ = 4
    E_SH_OFF = E_PH_OFF + E_PH_OFF_SZ
    E_SH_OFF_SZ = 4
    E_FLAGS = E_SH_OFF + E_SH_OFF_SZ
    E_FLAGS_SZ = 4
    E_EH_SIZE = E_FLAGS + E_FLAGS_SZ
    E_EH_SIZE_SZ = 2
    E_PH_ENT_SIZE = E_EH_SIZE + E_EH_SIZE_SZ
    E_PH_ENT_SIZE_SZ = 2
    E_PH_COUNT = E_PH_ENT_SIZE + E_PH_ENT_SIZE_SZ
    E_PH_COUNT_SZ = 2
    E_SH_ENT_SIZE = E_PH_COUNT + E_PH_COUNT_SZ
    E_SH_ENT_SIZE_SZ = 2
    E_SH_COUNT = E_SH_ENT_SIZE + E_SH_ENT_SIZE_SZ
    E_SH_COUNT_SZ = 2
    E_SH_STRNDX = E_SH_COUNT + E_SH_COUNT_SZ
    E_SH_STRNDX_SZ = 2

    def __init__(self):
        self.members = {
            "ei_magic": 0,
            "ei_class": 0,
            "ei_data": 0,
            "ei_version": 0,
            "ei_osabi": 0,
            "ei_abiversion": 0,
            "ei_pad": 0,
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
        offset = ElfHeader.EI_MAGIC
        for key in self.members:
            self.members[key] = unpack(buffer[offset:offset + getattr(ElfHeader, f"{key.upper()}_SZ")])
            offset += getattr(ElfHeader, f"{key.upper()}_SZ")

        if self.members["ei_magic"] != ElfHeader.ELF_MAGIC:
            raise Exception("Not an Elf file")

    def pack(self):
        buffer = []
        for key in self.members:
            buffer.extend(pack(self.members[key], getattr(ElfHeader, f"{key.upper()}_SZ")))
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
        return str(self.members)


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


class Elf:
    '''Elf file
    '''

    def __init__(self, filein):
        self.binary = read_binary(filein)
        self.elf_header = ElfHeader()
        self.elf_header.unpack(self.binary)
        self.section_data = []

        self.strtab = None
        self.strtab_data = None

        self.program_headers = self.load_program_headers()
        self.section_headers = self.load_section_headers()

        self.load_section_data()

        self.crc32 = Crc32()

    def load_program_headers(self):
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

    def load_section_headers(self):
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

    def load_section_data(self):
        '''Loads section data from .elf
        '''
        strtab_data = []
        strtab = []

        for sh in self.section_headers:
            _start = sh.get_offset()
            _end = _start + sh.get_size()
            type = sh.get_type()
            if type not in [SectionHeader.TYPE_SHT_NOBITS, SectionHeader.TYPE_SHT_NULL]:
                sh_data = SectionData(self.binary[_start:_end])
                sh_data.add_section_header(sh)
                self.section_data.append(sh_data)
                if type== SectionHeader.TYPE_SHT_STRTAB:
                    strtab.append(sh)
                    strtab_data.append(sh_data)
                    if len(strtab) == self.elf_header.get_stridx():
                        self.strtab = sh
                        self.strtab_data = sh_data

        if self.strtab is None:
            raise Exception("ERROR: Symbol or String table not found")

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
                raise Exception(f"ERROR: couldn't place {_start:x}-{_end:x}")

    def _create_data(self, address, new_data):
        '''Create data
        '''
        section_data = self._create_section_data(new_data)
        strindex = self._update_string_table()

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

    def _update_string_table(self):
        strindex = self.strtab.get_size()
        update(f".partial_{strindex:x}\0".encode(), self.strtab_data.get_data(), strindex)
        self.strtab.set_size(self.strtab_data.get_size())
        return strindex

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
        ''' Fill range
            -> start_address: start address of the range
            -> end_address: end address of the range
            -> byte: filling byte
        '''
        length = end_address - start_address
        new_data = []
        new_data.extend([byte]*length)
        self.add(start_address, new_data, can_overwrite=False)

    def calculate_checksum(self, start_address, end_address, crc_address):
        ''' Calculates checksum for range and places at an address
            -> start_address: starting address of the range
            -> end_address: ending address of the range, excluded
            -> crc_address: address to which the crc should be written to 
        '''
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
        self.add(crc_address, convert_int_to_list(checksum))
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

        self._write_program_headers(binary)
        self._write_section_headers(binary)
        self._update_elf_header(binary)

        # .elf
        if elf_out != "":
            with open(elf_out, 'wb') as f:
                f.write(bytes(binary))

        # .hex and .bin
        ihex = IntelHex()
        for data in sorted(self.section_data, key=lambda x: x.get_vaddr()):
            address = data.get_vaddr()
            if address != 0:
                ihex.frombytes(data.get_data(), offset=address)
                
        if hex_out != "":
            ihex.write_hex_file(hex_out)
        
        if bin_out != "":
             ihex.tobinfile(bin_out)

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
        update(self.elf_header.pack(), binary, 0)

    def get_section_data(self, section_name):
        for sd in self.section_data:
            for sh in sd.get_section_headers():
                idx = sh.get_name_off()
                string = read_string(self.strtab_data.get_data(), idx)
                if section_name in string:
                    return sd.get_data()

        raise Exception(f"ERROR: section data was not found for name {section_name}")


if __name__ == "__main__":
    filein = sys.argv[1]
    fileout = sys.argv[2]
    fileout_hex = sys.argv[3]

    elf = Elf(filein)
    elf.calculate_checksum(start_address=0x8004000, end_address=0x080040C8, target_address=0x080040C8)

    elf.fill(start_address=0x8010000, end_address=0x8060000, byte=0xFF)
    elf.calculate_checksum(start_address=0x801004C, end_address=0x8060000, target_address=0x8010048)

    elf.fill(start_address=0x8060000, end_address=0x807fff8, byte=0xFF)
    elf.fill(start_address=0x807fff8, end_address=0x807fffc, byte=0x5A)
    elf.calculate_checksum(start_address=0x8060000, end_address=0x807fffc, target_address=0x807fffC)

    # d = elf.get_section_data("partial")

    elf.write_data_to_file(fileout, fileout_hex)