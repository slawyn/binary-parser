
import sys
from intelhex import IntelHex
import utils
from parsers.elf.dwarf import Dwarf
from parsers.elf.segment import Segment
from parsers.elf.table import StringTable
from parsers.elf.symbol import SymTable
from parsers.elf.dynamic import Dynamic
from parsers.elf.program import ProgramHeader
from parsers.elf.section import SectionHeader, SectionData
from parsers.elf.ident import ElfIdent
from parsers.elf.header import ElfHeader
from crc import Crc32


class Writer:
    FILL = 0x00

    def __init__(self):
        self.binary = []

    def write_aligned(self, objs):
        for obj in objs:
            alignment_padding = obj.get_offset() - len(self.binary)
            self.binary.extend([Writer.FILL] * alignment_padding)
            if section_data := obj.get_section_data():
                self.binary.extend(section_data.get_data())

    def write_array(self, objs):
        for obj in objs:
            self.binary.extend(obj.pack())

    def write_single(self, obj):
        self.binary.extend(obj.pack())

    def get_binary(self):
        return self.binary


class ElfParser:
    """Elf Parser
       https://en.wikipedia.org/wiki/Executable_and_Linkable_Format
       https://docs.oracle.com/cd/E19683-01/816-1386/chapter6-83432/index.html
       https://www.uclibc.org/docs/elf-64-gen.pdf
    """

    def __init__(self, binary):
        self.shstrtab = None
        self.symtab = None
        self.dynsymtab = None
        self.dynamic = None
        self.dwarf = Dwarf()
        self.strtab = {}

        self.elf_ident = self._load_elf_ident(binary)
        self.elf_header = self._load_elf_header(binary)
        self.program_headers = self._load_program_headers(binary)
        self.section_headers = self._load_section_headers(binary)
        self._load_section_data(binary)

        self._map_sections_to_segments()
        self._load_symbols()
        self._load_debug_info()

        self.crc32 = Crc32()

    def _load_elf_ident(self, binary):
        elf_ident = ElfIdent()
        elf_ident.unpack(binary)
        return elf_ident

    def _load_elf_header(self, binary):
        elf_header = ElfHeader()
        elf_header.unpack(binary)
        return elf_header

    def _load_symbols(self):
        if self.dynsymtab:
            strtab = self.strtab[self.dynsymtab.get_strtab_idx()]
            for symbol in self.dynsymtab.get_entries():
                symbol.set_resolved_name(strtab.find_string(symbol.get_name_idx()))

        if self.symtab:
            strtab = self.strtab[self.symtab.get_strtab_idx()]
            for symbol in self.symtab.get_entries():
                symbol.set_resolved_name(strtab.find_string(symbol.get_name_idx()))

    def _load_debug_info(self):
        self.dwarf.parse_debug_info()

    def _load_program_headers(self, binary):
        program_headers = []
        for pidx in range(self.elf_header.get_ph_count()):
            ph_start = self.elf_header.get_ph_off() + pidx * self.elf_header.get_ph_ent_sz()
            ph_end = ph_start + self.elf_header.get_ph_ent_sz()
            ph = ProgramHeader()
            ph.unpack(binary[ph_start:ph_end])
            program_headers.append(ph)
        return program_headers

    def _load_section_headers(self, binary):
        section_headers = []
        for sidx in range(self.elf_header.get_sh_count()):
            sh_start = self.elf_header.get_sh_off() + sidx * self.elf_header.get_sh_ent_sz()
            sh_end = sh_start + self.elf_header.get_sh_ent_sz()
            sh = SectionHeader()
            sh.unpack(binary[sh_start:sh_end])
            section_headers.append(sh)
        return section_headers

    def _load_section_data(self, binary):
        for idx, sh in enumerate(self.section_headers):
            sd_start = sh.get_offset()
            sd_end = sd_start + sh.get_size()
            type = sh.get_type()
            if type not in [SectionHeader.TYPE_SHT_NULL, SectionHeader.TYPE_SHT_NOBITS]:
                sd = SectionData(binary[sd_start:sd_end])
                sh.set_section_data(sd)

                # strtab
                if type == SectionHeader.TYPE_SHT_STRTAB:
                    self.strtab[idx] = StringTable(sh, sd)
                    if idx == self.elf_header.get_stridx():
                        self.shstrtab = self.strtab[idx]

                # symtab
                elif type == SectionHeader.TYPE_SHT_SYMTAB:
                    if self.symtab is not None:
                        print("WARNING: only one symtab is supported at the moment")
                    else:
                        self.symtab = SymTable(sh, sd, sh.get_link())

                elif type == SectionHeader.TYPE_SHT_DYNSYM:
                    if self.dynsymtab is not None:
                        print("WARNING: only one dynsymtab is supported at the moment")
                    else:
                        self.dynsymtab = SymTable(sh, sd, sh.get_link())

                elif type == SectionHeader.TYPE_SHT_DYNAMIC:
                    if self.dynamic is not None:
                        print("WARNING: only one dynamic is supported at the moment")
                    else:
                        self.dynamic = Dynamic(sh, sd)

                elif type == SectionHeader.TYPE_SHT_PROGBITS:
                    if not sh.is_allocatable():
                        self.dwarf.add_debug_section(sh, sd)

        if self.shstrtab is None:
            raise Exception("ERROR: Symbol or String table not found")
        else:
            # Resolve names of the section headers
            for idx, sh in enumerate(self.section_headers):
                sh.resolve_name(self.shstrtab.find_string(sh.get_name_off()))

    def _map_sections_to_segments(self):
        for idx, ph in enumerate(self.program_headers):
            ph_start = ph.get_offset()
            ph_end = ph_start + ph.get_filesz()

            if ph.get_type() not in [ProgramHeader.PT_PHDR]:
                sh_placed = []
                for sh in self.section_headers:
                    sh_start = sh.get_offset()
                    sh_end = sh_start + sh.get_size()
                    if ph_start <= sh_start <= sh_end <= ph_end:
                        sh_placed.append(sh)

                if len(sh_placed):
                    ph.set_included_sections(sorted(sh_placed, key=lambda x: x.get_offset()))
                elif ph_start != ph_end:
                    print(f"WARNING: couldn't place [{idx}] {ph.get_type()} {ph_start:x}-{ph_end:x}")

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
            utils.update(s2, destination, offset)

        return s1

    def _overwrite_data_backward_overlap(self, source, destination, can_overwrite, offset, split_idx):
        s1, s2 = source[:split_idx], source[split_idx:]
        if can_overwrite:
            utils.update(s1, destination, offset)

        return s2

    def _overwrite_data_overlap(self, source, destination, can_overwrite, offset):
        if can_overwrite:
            utils.update(source, destination, offset)

        return []

    def _update_describing_headers(self, ph_offset):
        ph_size = sum(len(ph.pack())for ph in self.program_headers)
        for ph in self.program_headers:
            if ph.get_type() == ProgramHeader.PT_PHDR:
                ph.set_filesize(ph_size)

        sd_offset = ph_offset + ph_size
        sd_offset_end = sd_offset

        first_section_found = False
        diff_offset = 0
        for sh in sorted(self.section_headers, key=lambda x: x.get_offset()):
            if sh.get_type() not in [SectionHeader.TYPE_SHT_NULL, SectionHeader.TYPE_SHT_NOBITS]:
                if not first_section_found:
                    first_section_found = True
                    diff_offset = sd_offset - sh.get_offset()

                sh.set_offset(sh.get_offset() + diff_offset)
            sd_offset_end = sh.get_offset() + sh.get_size()

        return sd_offset_end

    def _update_elf_header(self, sh_offset, ph_offset):
        self.elf_header.set_sh_count(len(self.section_headers))
        self.elf_header.set_ph_count(len(self.program_headers))
        self.elf_header.set_sh_offset(sh_offset)
        self.elf_header.set_ph_offset(ph_offset)

    def _get_size_elf_ident(self):
        return len(self.elf_ident.pack())

    def _get_size_elf_header(self):
        return len(self.elf_header.pack())

    def _update_headers(self):
        # Recalculate offsets
        ph_offset = self._get_size_elf_ident() + self._get_size_elf_header()
        sh_offset = self._update_describing_headers(ph_offset)
        self._update_elf_header(sh_offset, ph_offset)

    def write_data_to_file(self, file_out=""):
        self._update_headers()

        # at this point all offsets and size have been updated
        # no recalculation is needed
        if file_out != "":
            self._write_elf_file(file_out)
            self._write_hex_file(file_out+".hex")

    def _write_elf_file(self, elf_out):
        writer = Writer()
        writer.write_single(self.elf_ident)
        writer.write_single(self.elf_header)
        writer.write_array(self.program_headers)
        writer.write_aligned(sorted(self.section_headers, key=lambda x: x.get_offset()))
        writer.write_array(self.section_headers)
        with open(elf_out, 'wb') as f:
            f.write(bytes(writer.get_binary()))

    def _write_hex_file(self, hex_out):
        ihex = IntelHex()
        for ph in sorted(self.program_headers, key=lambda x: x.get_vaddr()):
            if ph.get_type() not in [ProgramHeader.PT_PHDR, ProgramHeader.PT_INTERP]:
                address = ph.get_vaddr()
                for sh in ph.get_included_sections():
                    print("HEX", hex(address))
                    if sd := sh.get_section_data():
                        ihex.frombytes(sd.get_data(), offset=address)
                    address += sh.get_size()

        ihex.write_hex_file(hex_out)

    def get_section_data_by_name(self, section_name):
        for sd in self.section_data:
            for sh in sd.get_section_headers():
                string = self.shstrtab.find_string(idx=sh.get_name_off())
                if section_name in string:
                    return sd.get_data()

        raise Exception(f"ERROR: section data was not found for name {section_name}")

    def fill(self, start_address, end_address, byte):
        ''' Fill section
        '''
        length = end_address - start_address
        new_data = []
        new_data.extend([byte]*length)
        self.add(start_address, new_data, can_overwrite=False)

    # REDO
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

    # REDO
    def get_segments(self):
        segments = []
        for data in sorted(self.section_data, key=lambda x: x.get_vaddr()):
            s_addr, e_addr = data.get_address_range()
            if s_addr < e_addr:
                segments.append(Segment(s_addr, data.get_data()))
        return segments

    # REDO
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
            if s_addr < e_addr:
                if s_addr <= start_address < e_addr:
                    _offset_start = start_address - s_addr
                    _offset_end = start_address - s_addr + size
                    o_data.extend(data.get_data()[_offset_start:_offset_end])
                    break
        return o_data

    # REDO
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

            if s_addr < e_addr:
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

    def __str__(self):
        name_fmt = "%-40s"
        out = ""
        out += str(self.elf_ident)
        out += str(self.elf_header)
        out += f"\n[Program Headers] ({len(self.program_headers)})\n"
        out += name_fmt % ("[Segment Name]") + ProgramHeader.get_column_titles() + "\n"
        for idx, ph in enumerate(self.program_headers):
            out += name_fmt % f"[{idx}][{ph.get_vaddr():x}-{ph.get_vaddr() +ph.get_memsz():x}]"
            out += str(ph)
            out += "\n"

        out += name_fmt % ("\n[Segment Inclusions]") + "\n"
        for idx, ph in enumerate(self.program_headers):
            out += f'[{idx}] ({" ".join(sh.get_name() for sh in ph.get_included_sections())} )'
            out += "\n"

        out += f"\n[Section Headers] ({len(self.section_headers)})\n"
        out += name_fmt % ("[Section Name]") + SectionHeader.get_column_titles() + "\n"
        for idx, sh in enumerate(self.section_headers):
            out += name_fmt % f"[{idx}] {sh.get_name()} [{sh.get_offset():x}-{sh.get_offset() + sh.get_size():x}]"
            out += str(sh)
            out += "\n"

        special_sections = {"Symtable": self.symtab,
                            "DynSymtable": self.dynsymtab,
                            "Dynamic": self.dynamic
                            }
        for key, tab in special_sections.items():
            if tab:
                out += f"\n[{key}] ({len(tab.get_entries())})\n"
                out += name_fmt % ("[Idx]") + tab.get_column_titles() + "\n"
                for idx, symbol in enumerate(tab.get_entries()):
                    out += name_fmt % f"[{idx}]"
                    out += str(symbol)
                    out += "\n"

        if self.dwarf:
            out += f"\n[Debug] ({len(self.dwarf.get_entries())})\n"
            for idx, tab in enumerate(self.dwarf.get_entries()):
                out += name_fmt % f"[{idx}]"
                out += "\n"
                out += str(tab)
                out += "\n"

        return out


if __name__ == "__main__":
    filein = sys.argv[1]
    fileout = sys.argv[2]
    fileout_hex = sys.argv[3]

    elf = ElfParser(filein)
    # print(elf)
    # elf.calculate_checksum(start_address=0x8004000, end_address=0x080040C8, target_address=0x080040C8)

    # elf.fill(start_address=0x8010000, end_address=0x8060000, byte=0xFF)
    # elf.calculate_checksum(start_address=0x801004C, end_address=0x8060000, target_address=0x8010048)

    # elf.fill(start_address=0x8060000, end_address=0x807fff8, byte=0xFF)
    # elf.fill(start_address=0x807fff8, end_address=0x807fffc, byte=0x5A)
    # elf.calculate_checksum(start_address=0x8060000, end_address=0x807fffc, target_address=0x807fffC)

    # d = elf.get_section_data_by_name("partial")
    elf.write_data_to_file(fileout, fileout_hex)
