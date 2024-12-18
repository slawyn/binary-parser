import traceback
import utils
from parsers.pe.dosheader import DosHeader
from parsers.pe.sectionheader import SectionTable
from parsers.pe.ntheader import NtHeader
from parsers.pe.fileheader import FileHeader
from parsers.pe.optionalheader import OptionalHeader
from parsers.pe.directory import Directory


class PeParser:
    def __init__(self, binary):
        try:
            self.dos_header = DosHeader()
            self.dos_header.unpack(binary)
            offset = self.dos_header.get_lfanew()

            self.nt_header = NtHeader()
            self.nt_header.set_offset(offset)
            offset = self.nt_header.unpack(binary)

            self.file_header = FileHeader()
            self.file_header.set_offset(offset)
            offset = self.file_header.unpack(binary)

            self.optional_header = OptionalHeader()
            self.optional_header.set_offset(offset)
            offset = self.optional_header.unpack(binary)

            self.directory = Directory()
            self.directory.set_offset(offset)
            offset = self.directory.unpack(binary)

            self.section_table = SectionTable(self.file_header.get_number_of_sections())
            self.section_table.set_offset(offset)
            self.section_table.unpack(binary)

            self.directory.assign_section_headers(binary, self.section_table.get_section_headers())
        except Exception as e:
            traceback.print_exc()

    def __str__(self):
        out = str(self.dos_header)
        out += str(self.nt_header)
        out += str(self.file_header)
        out += str(self.optional_header)
        out += str(self.section_table)
        out += str(self.directory)
        return out

    def dump_code_sections(self, binary):
        section_files_to_disassemble = []
        for i, code in enumerate(self.section_table.get_code_sections()):

            section_files_to_disassemble.append("code" + str(i) + ".bin")
            with open(section_files_to_disassemble[i], "wb") as fd:
                utils.log(section_files_to_disassemble[i])

                lowerlimit = code.get_pointer_to_raw_data()
                upperlimit = code.get_pointer_to_raw_data() + code.get_virtual_size()

                if upperlimit > code.get_pointer_to_raw_data() + code.get_size_of_raw_data():
                    fd.write(binary[lowerlimit:upperlimit])
                    padding = upperlimit - code.get_pointer_to_raw_data() + code.get_size_of_raw_data()
                    for i in range(padding):
                        fd.write("\x00")
                else:
                    fd.write(binary[lowerlimit:upperlimit])
            fd.close()

        return section_files_to_disassemble
