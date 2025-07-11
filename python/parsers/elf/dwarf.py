import utils
from packer import Packer


class Tag(Packer):

    def __init__(self, tag_offset, members, members64={}, always_32bit=False, start_offset=0):
        self.tag_offset = tag_offset
        super().__init__(members, members_64bit=members64, always_32bit=always_32bit, start_offset=start_offset)


class DW_TAG_compile_unit(Tag):

    def __init__(self, tag_offset):
        super().__init__(
            tag_offset,
            {
                "DW_AT_producer": 4,
                "DW_AT_language": 1,
                "DW_AT_name": 4,
                "DW_AT_comp_dir": 4,
                "DW_AT_low_pc": 8,
                "DW_AT_high_pc": 8,
                "DW_AT_stmt_list": 4,
            },
            always_32bit=True
        )

    def __str__(self):
        out = utils.formatter("", f"<{self.tag_offset:x}> {__class__.__name__}")
        out += utils.formatter("DW_AT_producer", self.get_value("DW_AT_producer"), hex=True, pad=10)
        out += utils.formatter("DW_AT_language", self.get_value("DW_AT_language"), hex=True, pad=10)
        out += utils.formatter("DW_AT_name", self.get_value("DW_AT_name"), hex=True, pad=10)
        out += utils.formatter("DW_AT_comp_dir", self.get_value("DW_AT_comp_dir"), hex=True, pad=10)
        out += utils.formatter("DW_AT_low_pc", self.get_value("DW_AT_low_pc"), hex=True, pad=10)
        out += utils.formatter("DW_AT_high_pc", self.get_value("DW_AT_high_pc"), hex=True, pad=10)
        out += utils.formatter("DW_AT_stmt_list", self.get_value("DW_AT_stmt_list"), hex=True, pad=10)
        return out


class DW_TAG_base_type(Tag):

    def __init__(self, tag_offset):
        super().__init__(
            tag_offset,
            {
                "DW_AT_byte_size": 1,
                "DW_AT_encoding": 1,
                "DW_AT_name": 4
            },
            always_32bit=True
        )

    def __str__(self):
        out = utils.formatter("", f"<{self.tag_offset:x}> {__class__.__name__}")
        out += utils.formatter("DW_AT_byte_size", self.get_value("DW_AT_byte_size"), hex=True, pad=10)
        out += utils.formatter("DW_AT_encoding", self.get_value("DW_AT_encoding"), hex=True, pad=10)
        out += utils.formatter("DW_AT_name", self.get_value("DW_AT_name"), hex=True, pad=10)
        return out


class DW_TAG_typedef(Tag):

    def __init__(self, tag_offset):
        super().__init__(
            tag_offset,
            {
                "DW_AT_name": 4,
                "DW_AT_decl_file": 1,
                "DW_AT_decl_line": 1,
                "DW_AT_decl_column": 1,
                "DW_AT_type": 4,
            },
            always_32bit=True
        )

    def __str__(self):
        out = utils.formatter("", f"<{self.tag_offset:x}> {__class__.__name__}")
        out += utils.formatter("DW_AT_name", self.get_value("DW_AT_name"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_file", self.get_value("DW_AT_decl_file"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_line", self.get_value("DW_AT_decl_line"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_column", self.get_value("DW_AT_decl_column"), hex=True, pad=10)
        out += utils.formatter("DW_AT_type", self.get_value("DW_AT_type"), hex=True, pad=10)
        return out


class DW_TAG_const_type(Tag):

    def __init__(self, tag_offset):
        super().__init__(
            tag_offset,
            {
                "DW_AT_type": 4,
            },
            always_32bit=True
        )

    def __str__(self):
        out = utils.formatter("", f"<{self.tag_offset:x}> {__class__.__name__}")
        out += utils.formatter("DW_AT_type", self.get_value("DW_AT_type"), hex=True, pad=10)
        return out


class DW_TAG_formal_parameter(Tag):

    def __init__(self, tag_offset):
        super().__init__(
            tag_offset,
            {
                "DW_AT_type": 4,
            },
            always_32bit=True
        )

    def __str__(self):
        out = utils.formatter("", f"<{self.tag_offset:x}> {__class__.__name__}")
        out += utils.formatter("DW_AT_type", self.get_value("DW_AT_type"), hex=True, pad=10)
        return out


class DW_TAG_pointer_type(Tag):

    def __init__(self, tag_offset):
        super().__init__(
            tag_offset,
            {
                "DW_AT_byte_size": 1,
                "DW_AT_type": 4,
            },
            always_32bit=True
        )

    def __str__(self):
        out = utils.formatter("", f"<{self.tag_offset:x}> {__class__.__name__}")
        out += utils.formatter("DW_AT_byte_size", self.get_value("DW_AT_byte_size"), hex=True, pad=10)
        out += utils.formatter("DW_AT_type", self.get_value("DW_AT_type"), hex=True, pad=10)
        return out


class DW_TAG_structure_type(Tag):

    def __init__(self, tag_offset):
        super().__init__(
            tag_offset,
            {
                "DW_AT_byte_size": 1,
                "DW_AT_decl_file": 1,
                "DW_AT_decl_line": 1,
                "DW_AT_decl_column": 1,
                "DW_AT_sibling": 4,
            },
            always_32bit=True
        )

    def __str__(self):
        out = utils.formatter("", f"<{self.tag_offset:x}> {__class__.__name__}")
        out += utils.formatter("DW_AT_byte_size", self.get_value("DW_AT_byte_size"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_file", self.get_value("DW_AT_decl_file"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_line", self.get_value("DW_AT_decl_line"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_column", self.get_value("DW_AT_decl_column"), hex=True, pad=10)
        out += utils.formatter("DW_AT_sibling", self.get_value("DW_AT_sibling"), hex=True, pad=10)
        return out


class DW_TAG_member(Tag):

    def __init__(self, tag_offset):
        super().__init__(
            tag_offset,
            {
                "DW_AT_name": 4,
                "DW_AT_decl_file": 1,
                "DW_AT_decl_line": 1,
                "DW_AT_decl_column": 1,
                "DW_AT_type": 4,
                "DW_AT_data_member_location": 1,
            },
            always_32bit=True
        )

    def __str__(self):
        out = utils.formatter("", f"<{self.tag_offset:x}> {__class__.__name__}")
        out += utils.formatter("DW_AT_name", self.get_value("DW_AT_name"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_file", self.get_value("DW_AT_decl_file"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_line", self.get_value("DW_AT_decl_line"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_column", self.get_value("DW_AT_decl_column"), hex=True, pad=10)
        out += utils.formatter("DW_AT_type", self.get_value("DW_AT_type"), hex=True, pad=10)
        out += utils.formatter("DW_AT_data_member_location", self.get_value("DW_AT_data_member_location"), hex=True, pad=10)
        return out


class DW_TAG_variable_9(Tag):

    def __init__(self, tag_offset):
        super().__init__(
            tag_offset,
            {
                "DW_AT_name": 4,
                "DW_AT_decl_file": 1,
                "DW_AT_decl_line": 1,
                "DW_AT_decl_column": 1,
                "DW_AT_type": 4,
                "DW_AT_location": 0,
            },
            always_32bit=True
        )
        self.DW_AT_external = False

    def __str__(self):
        out = utils.formatter("", f"<{self.tag_offset:x}> {__class__.__name__}")
        out += utils.formatter("DW_AT_name", self.get_value("DW_AT_name"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_file", self.get_value("DW_AT_decl_file"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_line", self.get_value("DW_AT_decl_line"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_column", self.get_value("DW_AT_decl_column"), hex=True, pad=10)
        out += utils.formatter("DW_AT_type", self.get_value("DW_AT_type"), hex=True, pad=10)
        out += utils.formatter("DW_AT_external", self.DW_AT_external, hex=True, pad=10)
        out += utils.formatter("DW_AT_location", self.get_value("DW_AT_location"), hex=True, pad=10)
        return out


class DW_TAG_variable_15(Tag):

    def __init__(self, tag_offset):
        super().__init__(
            tag_offset,
            {
                "DW_AT_name": 4,
                "DW_AT_decl_file": 1,
                "DW_AT_decl_line": 1,
                "DW_AT_decl_column": 1,
                "DW_AT_type": 4,
                "DW_AT_location": 1,
            },
            always_32bit=True
        )

    def __str__(self):
        out = utils.formatter("", f"<{self.tag_offset:x}> {__class__.__name__}")
        out += utils.formatter("DW_AT_name", self.get_value("DW_AT_name"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_file", self.get_value("DW_AT_decl_file"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_line", self.get_value("DW_AT_decl_line"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_column", self.get_value("DW_AT_decl_column"), hex=True, pad=10)
        out += utils.formatter("DW_AT_type", self.get_value("DW_AT_type"), hex=True, pad=10)
        out += utils.formatter("DW_AT_location", self.get_value("DW_AT_location"), pad=10)
        return out


class DW_TAG_subprogram_10(Tag):

    def __init__(self, tag_offset):
        super().__init__(
            tag_offset,
            {
                "DW_AT_name": 4,
                "DW_AT_decl_file": 1,
                "DW_AT_decl_line": 1,
                "DW_AT_decl_column": 1,
                "DW_AT_declaration": 1,
                "DW_AT_sibling": 4,
            },
            always_32bit=True
        )
        self.DW_AT_external = False

    def __str__(self):
        out = utils.formatter("", f"<{self.tag_offset:x}> {__class__.__name__}")
        out += utils.formatter("DW_AT_external", self.DW_AT_external, hex=True, pad=10)
        out += utils.formatter("DW_AT_name", self.get_value("DW_AT_name"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_file", self.get_value("DW_AT_decl_file"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_line", self.get_value("DW_AT_decl_line"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_column", self.get_value("DW_AT_decl_column"), hex=True, pad=10)
        out += utils.formatter("DW_AT_declaration", self.get_value("DW_AT_declaration"), hex=True, pad=10)
        out += utils.formatter("DW_AT_sibling", self.get_value("DW_AT_sibling"), hex=True, pad=10)
        return out


class DW_TAG_subprogram_11(Tag):

    def __init__(self, tag_offset):
        super().__init__(
            tag_offset,
            {
                "DW_AT_name": 4,
                "DW_AT_decl_file": 1,
                "DW_AT_decl_line": 1,
                "DW_AT_decl_column": 1,
                "DW_AT_type": 4,
                "DW_AT_declaration": 1,
                "DW_AT_sibling": 4,
            },
            always_32bit=True
        )
        self.DW_AT_external = False

    def __str__(self):
        out = utils.formatter("", f"<{self.tag_offset:x}> {__class__.__name__}")
        out += utils.formatter("DW_AT_external", self.DW_AT_external, hex=True, pad=10)
        out += utils.formatter("DW_AT_name", self.get_value("DW_AT_name"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_file", self.get_value("DW_AT_decl_file"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_line", self.get_value("DW_AT_decl_line"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_column", self.get_value("DW_AT_decl_column"), hex=True, pad=10)
        out += utils.formatter("DW_AT_type", self.get_value("DW_AT_type"), hex=True, pad=10)
        out += utils.formatter("DW_AT_declaration", self.get_value("DW_AT_declaration"), hex=True, pad=10)
        out += utils.formatter("DW_AT_sibling", self.get_value("DW_AT_sibling"), hex=True, pad=10)
        return out


class DW_TAG_subprogram_14(Tag):

    def __init__(self, tag_offset):
        super().__init__(
            tag_offset,
            {
                "DW_AT_name": 4,
                "DW_AT_decl_file": 1,
                "DW_AT_decl_line": 1,
                "DW_AT_decl_column": 1,
                "DW_AT_low_pc": 8,
                "DW_AT_high_pc": 8,
                "DW_AT_frame_base": 2,
                "DW_AT_call_all_tail_calls": 0,
            },
            always_32bit=True
        )
        self.DW_AT_external = False

    def __str__(self):
        out = utils.formatter("", f"<{self.tag_offset:x}> {__class__.__name__}")
        out += utils.formatter("DW_AT_external", self.DW_AT_external, hex=True, pad=10)
        out += utils.formatter("DW_AT_name", self.get_value("DW_AT_name"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_file", self.get_value("DW_AT_decl_file"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_line", self.get_value("DW_AT_decl_line"), hex=True, pad=10)
        out += utils.formatter("DW_AT_decl_column", self.get_value("DW_AT_decl_column"), hex=True, pad=10)
        out += utils.formatter("DW_AT_low_pc", self.get_value("DW_AT_low_pc"), hex=True, pad=10)
        out += utils.formatter("DW_AT_high_pc", self.get_value("DW_AT_high_pc"), hex=True, pad=10)
        out += utils.formatter("DW_AT_frame_base", self.get_value("DW_AT_frame_base"), hex=True, pad=10)
        out += utils.formatter("DW_AT_call_all_tail_calls", self.get_value("DW_AT_call_all_tail_calls"), hex=True, pad=10)
        return out


class CompilationUnitHeader(Tag):

    def __init__(self, tag_offset):
        super().__init__(
            tag_offset,
            {
                "cu_pointer_size": 1,
                "cu_abbrev_offset": 4
            },
            always_32bit=True
        )

    def get_abbrev_offset(self):
        return self.get_value("cu_abbrev_offset")

    def __str__(self):
        out = utils.formatter("", f"<{self.tag_offset:x}> {__class__.__name__}")
        out += utils.formatter("Pointer Size", self.get_value("cu_pointer_size"), pad=10)
        out += utils.formatter("Abbrev. Offset", self.get_value("cu_abbrev_offset"), pad=10)
        return out


class CompilationUnit(Packer):
    DW_UNIT_TYPES = {
        1: "DW_UT_COMPILE"
    }

    SUPPORTED_VERSIONS = [5]
    COMPILATION_UNITS = {
        1: DW_TAG_base_type,
        2: DW_TAG_typedef,
        4: DW_TAG_compile_unit,
        5: DW_TAG_base_type,
        6: DW_TAG_compile_unit,
        7: DW_TAG_structure_type,
        8: DW_TAG_member,
        9: DW_TAG_variable_9,
        10: DW_TAG_subprogram_10,
        11: DW_TAG_subprogram_11,
        12: DW_TAG_formal_parameter,
        13: DW_TAG_pointer_type,
        14: DW_TAG_subprogram_14,
        15: DW_TAG_variable_15,
    }

    DW_TAG_unspecified_parameters = 3
    DW_TAG_termination_zero = 0

    def __init__(self):
        super().__init__(
            {
                "cu_length": 4,
                "cu_version": 2,
                "cu_unit_type": 1
            },  always_32bit=True
        )

        self.abbreviations = []
        self.compile_units = []

    def unpack(self, buffer):
        offset = super().unpack(buffer)

        if self.get_value("cu_version") not in CompilationUnit.SUPPORTED_VERSIONS or self.get_value("cu_unit_type") not in CompilationUnit.DW_UNIT_TYPES:
            raise Exception(
                f'ERROR: unsupported Compilation Unit version:{self.get_value("cu_version")} unit:{self.get_value("cu_unit_type")}')

        self.cu_header = CompilationUnitHeader(offset)
        offset += self.cu_header.unpack(buffer[offset:])
        offset += self.cu_header.get_abbrev_offset()

        self._parse_compile_unit(buffer, offset, self.get_value("cu_length"))

    def pack(self):
        buffer = super().pack()
        buffer.extend(self.cu_header.pack())
        return buffer

    def _parse_compile_unit(self, buffer, offset, end_offset):
        while offset < end_offset:
            type = buffer[offset]
            offset += 1
            if type in CompilationUnit.COMPILATION_UNITS:
                cu = CompilationUnit.COMPILATION_UNITS[type](offset)
                offset += cu.unpack(buffer[offset:])
                self.compile_units.append(cu)
            elif type != CompilationUnit.DW_TAG_termination_zero and type != CompilationUnit.DW_TAG_unspecified_parameters:
                pass
               # raise Exception(f"ERROR: unknown compilation unit {type:x} at [{offset:x}]  {utils.format_array(buffer[offset:end_offset])}")

    def __str__(self):
        out = utils.formatter("", __class__.__name__)
        out += utils.formatter("Length", self.get_value("cu_length"), hex=True, pad=10)
        out += utils.formatter("Version", self.get_value("cu_version"), pad=10)
        out += utils.formatter("Unit Type", self.get_value("cu_unit_type"), table=CompilationUnit.DW_UNIT_TYPES, pad=10)
        out += str(self.cu_header)
        for cu in self.compile_units:
            out += str(cu)
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
                unit = CompilationUnit()
                unit.unpack(sh_data.get_data())
                self.entries.append(unit)
