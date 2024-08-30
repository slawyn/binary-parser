import utils
from packer import Packer


class DW_TAG_compile_unit(Packer):
    DW_AT_PRODUCER_SZ = 4
    DW_AT_LANGUAGE_SZ = 1
    DW_AT_NAME_SZ = 4
    DW_AT_COMP_DIR_SZ = 4
    DW_AT_LOW_PC_SZ = 8
    DW_AT_HIGH_PC_SZ = 8
    DW_AT_STMT_LIST_SZ = 4

    def __init__(self):
        super().__init__(
            {
                "DW_AT_producer": "",
                "DW_AT_language": "",
                "DW_AT_name": "",
                "DW_AT_comp_dir": "",
                "DW_AT_low_pc": "",
                "DW_AT_high_pc": "",
                "DW_AT_stmt_list": "",
            },
            always_bit32=True
        )

    def get_size(self):
        return DW_TAG_compile_unit.DW_AT_PRODUCER_SZ\
            + DW_TAG_compile_unit.DW_AT_LANGUAGE_SZ\
            + DW_TAG_compile_unit.DW_AT_NAME_SZ\
            + DW_TAG_compile_unit.DW_AT_COMP_DIR_SZ\
            + DW_TAG_compile_unit.DW_AT_LOW_PC_SZ\
            + DW_TAG_compile_unit.DW_AT_HIGH_PC_SZ\
            + DW_TAG_compile_unit.DW_AT_STMT_LIST_SZ

    def __str__(self):
        out = utils.formatter("", __class__.__name__)
        out += utils.formatter("DW_AT_producer", self.members["DW_AT_producer"], hex=True)
        out += utils.formatter("DW_AT_language", self.members["DW_AT_language"], hex=True)
        out += utils.formatter("DW_AT_name", self.members["DW_AT_name"], hex=True)
        out += utils.formatter("DW_AT_comp_dir", self.members["DW_AT_comp_dir"], hex=True)
        out += utils.formatter("DW_AT_low_pc", self.members["DW_AT_low_pc"], hex=True)
        out += utils.formatter("DW_AT_high_pc", self.members["DW_AT_high_pc"], hex=True)
        out += utils.formatter("DW_AT_stmt_list", self.members["DW_AT_stmt_list"], hex=True)
        return out


class DW_TAG_base_type(Packer):
    DW_AT_BYTE_SIZE_SZ = 1
    DW_AT_ENCODING_SZ = 1
    DW_AT_NAME_SZ = 4

    def __init__(self):
        super().__init__(
            {
                "DW_AT_byte_size": "",
                "DW_AT_encoding": "",
                "DW_AT_name": ""
            },
            always_bit32=True
        )

    def get_size(self):
        return DW_TAG_base_type.DW_AT_BYTE_SIZE_SZ\
            + DW_TAG_base_type.DW_AT_ENCODING_SZ\
            + DW_TAG_base_type.DW_AT_NAME_SZ

    def __str__(self):
        out = utils.formatter("", __class__.__name__)
        out += utils.formatter("DW_AT_byte_size", self.members["DW_AT_byte_size"], hex=True)
        out += utils.formatter("DW_AT_encoding", self.members["DW_AT_encoding"], hex=True)
        out += utils.formatter("DW_AT_name", self.members["DW_AT_name"], hex=True)
        return out


class DW_TAG_typedef(Packer):
    DW_AT_NAME_SZ = 4
    DW_AT_DECL_FILE_SZ = 1
    DW_AT_DECL_LINE_SZ = 1
    DW_AT_DECL_COLUMN_SZ = 1
    DW_AT_TYPE_SZ = 4

    def __init__(self):
        super().__init__(
            {
                "DW_AT_name": "",
                "DW_AT_decl_file": "",
                "DW_AT_decl_line": "",
                "DW_AT_decl_column": "",
                "DW_AT_type": "",
            },
            always_bit32=True
        )

    def get_size(self):
        return DW_TAG_typedef.DW_AT_NAME_SZ\
            + DW_TAG_typedef.DW_AT_DECL_FILE_SZ\
            + DW_TAG_typedef.DW_AT_DECL_LINE_SZ\
            + DW_TAG_typedef.DW_AT_DECL_COLUMN_SZ\
            + DW_TAG_typedef.DW_AT_TYPE_SZ

    def __str__(self):
        out = utils.formatter("", __class__.__name__)
        out += utils.formatter("DW_AT_name", self.members["DW_AT_name"], hex=True)
        out += utils.formatter("DW_AT_decl_file", self.members["DW_AT_decl_file"], hex=True)
        out += utils.formatter("DW_AT_decl_line", self.members["DW_AT_decl_line"], hex=True)
        out += utils.formatter("DW_AT_decl_column", self.members["DW_AT_decl_column"], hex=True)
        out += utils.formatter("DW_AT_type", self.members["DW_AT_type"], hex=True)
        return out


class DW_TAG_const_type(Packer):
    DW_AT_TYPE_SZ = 4

    def __init__(self):
        super().__init__(
            {
                "DW_AT_type": "",
            },
            always_bit32=True
        )

    def get_size(self):
        return DW_TAG_const_type.DW_AT_TYPE_SZ

    def __str__(self):
        out = utils.formatter("", __class__.__name__)
        out += utils.formatter("DW_AT_type", self.members["DW_AT_type"], hex=True)
        return out


class DW_TAG_formal_parameter(Packer):
    DW_AT_TYPE_SZ = 4

    def __init__(self):
        super().__init__(
            {
                "DW_AT_type": "",
            },
            always_bit32=True
        )

    def get_size(self):
        return DW_TAG_formal_parameter.DW_AT_TYPE_SZ

    def __str__(self):
        out = utils.formatter("", __class__.__name__)
        out += utils.formatter("DW_AT_type", self.members["DW_AT_type"], hex=True)
        return out


class DW_TAG_pointer_type(Packer):
    DW_AT_BYTE_SIZE_SZ = 1
    DW_AT_TYPE_SZ = 4

    def __init__(self):
        super().__init__(
            {
                "DW_AT_byte_size": "",
                "DW_AT_type": "",
            },
            always_bit32=True
        )

    def get_size(self):
        return DW_TAG_pointer_type.DW_AT_BYTE_SIZE_SZ\
            + DW_TAG_pointer_type.DW_AT_TYPE_SZ

    def __str__(self):
        out = utils.formatter("", __class__.__name__)
        out += utils.formatter("DW_AT_byte_size", self.members["DW_AT_byte_size"], hex=True)
        out += utils.formatter("DW_AT_type", self.members["DW_AT_type"], hex=True)
        return out


class DW_TAG_structure_type(Packer):
    DW_AT_BYTE_SIZE_SZ = 1
    DW_AT_DECL_FILE_SZ = 1
    DW_AT_DECL_LINE_SZ = 1
    DW_AT_DECL_COLUMN_SZ = 1
    DW_AT_SIBLING_SZ = 4

    def __init__(self):
        super().__init__(
            {
                "DW_AT_byte_size": "",
                "DW_AT_decl_file": "",
                "DW_AT_decl_line": "",
                "DW_AT_decl_column": "",
                "DW_AT_sibling": "",
            },
            always_bit32=True
        )

    def get_size(self):
        return DW_TAG_structure_type.DW_AT_BYTE_SIZE_SZ\
            + DW_TAG_structure_type.DW_AT_DECL_FILE_SZ\
            + DW_TAG_structure_type.DW_AT_DECL_LINE_SZ\
            + DW_TAG_structure_type.DW_AT_DECL_COLUMN_SZ\
            + DW_TAG_structure_type.DW_AT_SIBLING_SZ\


    def __str__(self):
        out = utils.formatter("", __class__.__name__)
        out += utils.formatter("DW_AT_byte_size", self.members["DW_AT_byte_size"], hex=True)
        out += utils.formatter("DW_AT_decl_file", self.members["DW_AT_decl_file"], hex=True)
        out += utils.formatter("DW_AT_decl_line", self.members["DW_AT_decl_line"], hex=True)
        out += utils.formatter("DW_AT_decl_column", self.members["DW_AT_decl_column"], hex=True)
        out += utils.formatter("DW_AT_sibling", self.members["DW_AT_sibling"], hex=True)
        return out


class DW_TAG_member(Packer):
    DW_AT_NAME_SZ = 4
    DW_AT_DECL_FILE_SZ = 1
    DW_AT_DECL_LINE_SZ = 1
    DW_AT_DECL_COLUMN_SZ = 1
    DW_AT_TYPE_SZ = 4
    DW_AT_DATA_MEMBER_LOCATION_SZ = 1

    def __init__(self):
        super().__init__(
            {
                "DW_AT_name": "",
                "DW_AT_decl_file": "",
                "DW_AT_decl_line": "",
                "DW_AT_decl_column": "",
                "DW_AT_type": "",
                "DW_AT_data_member_location": "",
            },
            always_bit32=True
        )

    def get_size(self):
        return DW_TAG_member.DW_AT_NAME_SZ\
            + DW_TAG_member.DW_AT_DECL_FILE_SZ\
            + DW_TAG_member.DW_AT_DECL_LINE_SZ\
            + DW_TAG_member.DW_AT_DECL_COLUMN_SZ\
            + DW_TAG_member.DW_AT_TYPE_SZ\
            + DW_TAG_member.DW_AT_DATA_MEMBER_LOCATION_SZ\


    def __str__(self):
        out = utils.formatter("", __class__.__name__)
        out += utils.formatter("DW_AT_name", self.members["DW_AT_name"], hex=True)
        out += utils.formatter("DW_AT_decl_file", self.members["DW_AT_decl_file"], hex=True)
        out += utils.formatter("DW_AT_decl_line", self.members["DW_AT_decl_line"], hex=True)
        out += utils.formatter("DW_AT_decl_column", self.members["DW_AT_decl_column"], hex=True)
        out += utils.formatter("DW_AT_type", self.members["DW_AT_type"], hex=True)
        out += utils.formatter("DW_AT_data_member_location", self.members["DW_AT_data_member_location"], hex=True)
        return out


class DW_TAG_variable_9(Packer):
    DW_AT_NAME_SZ = 4
    DW_AT_DECL_FILE_SZ = 1
    DW_AT_DECL_LINE_SZ = 1
    DW_AT_DECL_COLUMN_SZ = 1
    DW_AT_TYPE_SZ = 4
    DW_AT_EXTERNAL_SZ = 0
    DW_AT_LOCATION_SZ = 8

    def __init__(self):
        super().__init__(
            {
                "DW_AT_name": "",
                "DW_AT_decl_file": "",
                "DW_AT_decl_line": "",
                "DW_AT_decl_column": "",
                "DW_AT_type": "",
                "DW_AT_external": "",
                "DW_AT_location": "",
            },
            always_bit32=True
        )

    def get_size(self):
        return DW_TAG_variable_9.DW_AT_NAME_SZ\
            + DW_TAG_variable_9.DW_AT_DECL_FILE_SZ\
            + DW_TAG_variable_9.DW_AT_DECL_LINE_SZ\
            + DW_TAG_variable_9.DW_AT_DECL_COLUMN_SZ\
            + DW_TAG_variable_9.DW_AT_TYPE_SZ\
            + DW_TAG_variable_9.DW_AT_EXTERNAL_SZ\
            + DW_TAG_variable_9.DW_AT_LOCATION_SZ\


    def __str__(self):
        out = utils.formatter("", __class__.__name__)
        out += utils.formatter("DW_AT_name", self.members["DW_AT_name"], hex=True)
        out += utils.formatter("DW_AT_decl_file", self.members["DW_AT_decl_file"], hex=True)
        out += utils.formatter("DW_AT_decl_line", self.members["DW_AT_decl_line"], hex=True)
        out += utils.formatter("DW_AT_decl_column", self.members["DW_AT_decl_column"], hex=True)
        out += utils.formatter("DW_AT_type", self.members["DW_AT_type"], hex=True)
        out += utils.formatter("DW_AT_external", self.members["DW_AT_external"], hex=True)
        out += utils.formatter("DW_AT_location", self.members["DW_AT_location"], hex=True)
        return out


class DW_TAG_variable_15(Packer):
    DW_AT_NAME_OFFSET = 0
    DW_AT_NAME_SZ = 4
    DW_AT_DECL_FILE_SZ = 1
    DW_AT_DECL_LINE_SZ = 1
    DW_AT_DECL_COLUMN_SZ = 1
    DW_AT_TYPE_SZ = 4
    DW_AT_LOCATION_SZ = 8

    def __init__(self):
        super().__init__(
            {
                "DW_AT_name": "",
                "DW_AT_decl_file": "",
                "DW_AT_decl_line": "",
                "DW_AT_decl_column": "",
                "DW_AT_type": "",
                "DW_AT_location": "",
            },
            always_bit32=True
        )

    def get_size(self):
        return DW_TAG_variable_15.DW_AT_NAME_SZ\
            + DW_TAG_variable_15.DW_AT_DECL_FILE_SZ\
            + DW_TAG_variable_15.DW_AT_DECL_LINE_SZ\
            + DW_TAG_variable_15.DW_AT_DECL_COLUMN_SZ\
            + DW_TAG_variable_15.DW_AT_TYPE_SZ\
            + DW_TAG_variable_15.DW_AT_LOCATION_SZ\


    def __str__(self):
        out = utils.formatter("", __class__.__name__)
        out += utils.formatter("DW_AT_name", self.members["DW_AT_name"], hex=True)
        out += utils.formatter("DW_AT_decl_file", self.members["DW_AT_decl_file"], hex=True)
        out += utils.formatter("DW_AT_decl_line", self.members["DW_AT_decl_line"], hex=True)
        out += utils.formatter("DW_AT_decl_column", self.members["DW_AT_decl_column"], hex=True)
        out += utils.formatter("DW_AT_type", self.members["DW_AT_type"], hex=True)
        out += utils.formatter("DW_AT_location", self.members["DW_AT_location"], hex=True)
        return out


class DW_TAG_subprogram_10(Packer):
    DW_AT_EXTERNAL_SZ = 0
    DW_AT_NAME_SZ = 4
    DW_AT_DECL_FILE_SZ = 1
    DW_AT_DECL_LINE_SZ = 1
    DW_AT_DECL_COLUMN_SZ = 1
    DW_AT_DECLARATION_SZ = 1
    DW_AT_SIBLING_SZ = 4

    def __init__(self):
        super().__init__(
            {
                "DW_AT_external": "",
                "DW_AT_name": "",
                "DW_AT_decl_file": "",
                "DW_AT_decl_line": "",
                "DW_AT_decl_column": "",
                "DW_AT_declaration": "",
                "DW_AT_sibling": "",
            },
            always_bit32=True
        )

    def get_size(self):
        return DW_TAG_subprogram_10.DW_AT_EXTERNAL_SZ\
            + DW_TAG_subprogram_10.DW_AT_NAME_SZ\
            + DW_TAG_subprogram_10.DW_AT_DECL_FILE_SZ\
            + DW_TAG_subprogram_10.DW_AT_DECL_LINE_SZ\
            + DW_TAG_subprogram_10.DW_AT_DECL_COLUMN_SZ\
            + DW_TAG_subprogram_10.DW_AT_DECLARATION_SZ\
            + DW_TAG_subprogram_10.DW_AT_SIBLING_SZ\


    def __str__(self):
        out = utils.formatter("", __class__.__name__)
        out += utils.formatter("DW_AT_external", self.members["DW_AT_external"], hex=True)
        out += utils.formatter("DW_AT_name", self.members["DW_AT_name"], hex=True)
        out += utils.formatter("DW_AT_decl_file", self.members["DW_AT_decl_file"], hex=True)
        out += utils.formatter("DW_AT_decl_line", self.members["DW_AT_decl_line"], hex=True)
        out += utils.formatter("DW_AT_decl_column", self.members["DW_AT_decl_column"], hex=True)
        out += utils.formatter("DW_AT_declaration", self.members["DW_AT_declaration"], hex=True)
        out += utils.formatter("DW_AT_sibling", self.members["DW_AT_sibling"], hex=True)
        return out


class DW_TAG_subprogram_11(Packer):
    DW_AT_EXTERNAL_SZ = 0
    DW_AT_NAME_SZ = 4
    DW_AT_DECL_FILE_SZ = 1
    DW_AT_DECL_LINE_SZ = 1
    DW_AT_DECL_COLUMN_SZ = 1
    DW_AT_TYPE_SZ = 4
    DW_AT_DECLARATION_SZ = 1
    DW_AT_SIBLING_SZ = 4

    def __init__(self):
        super().__init__(
            {
                "DW_AT_external": "",
                "DW_AT_name": "",
                "DW_AT_decl_file": "",
                "DW_AT_decl_line": "",
                "DW_AT_decl_column": "",
                "DW_AT_type": "",
                "DW_AT_declaration": "",
                "DW_AT_sibling": "",
            },
            always_bit32=True
        )

    def get_size(self):
        return DW_TAG_subprogram_11.DW_AT_EXTERNAL_SZ\
            + DW_TAG_subprogram_11.DW_AT_NAME_SZ\
            + DW_TAG_subprogram_11.DW_AT_DECL_FILE_SZ\
            + DW_TAG_subprogram_11.DW_AT_DECL_LINE_SZ\
            + DW_TAG_subprogram_11.DW_AT_DECL_COLUMN_SZ\
            + DW_TAG_subprogram_11.DW_AT_TYPE_SZ\
            + DW_TAG_subprogram_11.DW_AT_DECLARATION_SZ\
            + DW_TAG_subprogram_11.DW_AT_SIBLING_SZ\


    def __str__(self):
        out = utils.formatter("", __class__.__name__)
        out += utils.formatter("DW_AT_external", self.members["DW_AT_external"], hex=True)
        out += utils.formatter("DW_AT_name", self.members["DW_AT_name"], hex=True)
        out += utils.formatter("DW_AT_decl_file", self.members["DW_AT_decl_file"], hex=True)
        out += utils.formatter("DW_AT_decl_line", self.members["DW_AT_decl_line"], hex=True)
        out += utils.formatter("DW_AT_decl_column", self.members["DW_AT_decl_column"], hex=True)
        out += utils.formatter("DW_AT_type", self.members["DW_AT_type"], hex=True)
        out += utils.formatter("DW_AT_declaration", self.members["DW_AT_declaration"], hex=True)
        out += utils.formatter("DW_AT_sibling", self.members["DW_AT_sibling"], hex=True)
        return out


class DW_TAG_subprogram_14(Packer):
    DW_AT_EXTERNAL_SZ = 0
    DW_AT_NAME_SZ = 4
    DW_AT_DECL_FILE_SZ = 1
    DW_AT_DECL_LINE_SZ = 1
    DW_AT_DECL_COLUMN_SZ = 1
    DW_AT_LOW_PC_SZ = 8
    DW_AT_HIGH_PC_SZ = 8
    DW_AT_FRAME_BASE_SZ = 2
    DW_AT_CALL_ALL_TAIL_CALLS_SZ = 0

    def __init__(self):
        super().__init__(
            {
                "DW_AT_external": "",
                "DW_AT_name": "",
                "DW_AT_decl_file": "",
                "DW_AT_decl_line": "",
                "DW_AT_decl_column": "",
                "DW_AT_low_pc": "",
                "DW_AT_high_pc": "",
                "DW_AT_frame_base": "",
                "DW_AT_call_all_tail_calls": "",
            },
            always_bit32=True
        )

    def get_size(self):
        return DW_TAG_subprogram_14.DW_AT_EXTERNAL_SZ\
            + DW_TAG_subprogram_14.DW_AT_NAME_SZ\
            + DW_TAG_subprogram_14.DW_AT_DECL_FILE_SZ\
            + DW_TAG_subprogram_14.DW_AT_DECL_LINE_SZ\
            + DW_TAG_subprogram_14.DW_AT_DECL_COLUMN_SZ\
            + DW_TAG_subprogram_14.DW_AT_LOW_PC_SZ\
            + DW_TAG_subprogram_14.DW_AT_HIGH_PC_SZ\
            + DW_TAG_subprogram_14.DW_AT_FRAME_BASE_SZ\
            + DW_TAG_subprogram_14.DW_AT_CALL_ALL_TAIL_CALLS_SZ\


    def __str__(self):
        out = utils.formatter("", __class__.__name__)
        out += utils.formatter("DW_AT_external", self.members["DW_AT_external"], hex=True)
        out += utils.formatter("DW_AT_name", self.members["DW_AT_name"], hex=True)
        out += utils.formatter("DW_AT_decl_file", self.members["DW_AT_decl_file"], hex=True)
        out += utils.formatter("DW_AT_decl_line", self.members["DW_AT_decl_line"], hex=True)
        out += utils.formatter("DW_AT_decl_column", self.members["DW_AT_decl_column"], hex=True)
        out += utils.formatter("DW_AT_low_pc", self.members["DW_AT_low_pc"], hex=True)
        out += utils.formatter("DW_AT_high_pc", self.members["DW_AT_high_pc"], hex=True)
        out += utils.formatter("DW_AT_frame_base", self.members["DW_AT_frame_base"], hex=True)
        out += utils.formatter("DW_AT_call_all_tail_calls", self.members["DW_AT_call_all_tail_calls"], hex=True)
        return out


class CompilationUnitHeader(Packer):
    CU_POINTER_SIZE_SZ = 1
    CU_ABBREV_OFFSET_SZ = 4

    CU_POINTER_SIZE_64SZ = 1
    CU_ABBREV_OFFSET_64SZ = 4

    def __init__(self):
        super().__init__(
            {
                "cu_pointer_size": 0,
                "cu_abbrev_offset": 0
            },
            always_bit32=True
        )

    def get_abbrev_offset(self):
        return self.members["cu_abbrev_offset"]

    def get_header_size(self):
        return CompilationUnitHeader.CU_POINTER_SIZE_SZ + CompilationUnitHeader.CU_ABBREV_OFFSET_SZ

    def __str__(self):
        out = utils.formatter("", __class__.__name__)
        out += utils.formatter("Pointer Size", self.members["cu_pointer_size"])
        out += utils.formatter("Abbrev. Offset", self.members["cu_abbrev_offset"])
        return out


class CompilationUnit(Packer):
    CU_LENGTH_SZ = 4
    CU_VERSION_SZ = 2
    CU_UNIT_TYPE_SZ = 1

    DW_UNIT_TYPES = {
        1: "DW_UT_COMPILE"
    }

    SUPPORTED_VERSIONS = [5]
    COMPILATION_UNITS = {
        4: DW_TAG_compile_unit,
        1: DW_TAG_base_type,
        2: DW_TAG_typedef,
        5: DW_TAG_base_type,
        6: DW_TAG_const_type,
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
        self.abbreviations = []
        super().__init__(
            {
                "cu_length": 0,
                "cu_version": 0,
                "cu_unit_type": 0
            },  always_bit32=True
        )

        self.cu_header = CompilationUnitHeader()
        self.compilation_units = []

    def unpack(self, buffer):
        offset = super().unpack(buffer)

        if self.members["cu_version"] in CompilationUnit.SUPPORTED_VERSIONS and self.members["cu_unit_type"] in CompilationUnit.DW_UNIT_TYPES:
            self.cu_header.unpack(buffer[offset:])

            # Init values before parsing abbreviations
            header_size = self.cu_header.get_header_size()
            abbrev_offset = self.cu_header.get_abbrev_offset()
            offset += abbrev_offset + header_size
            length = self.members["cu_length"]

            # Compilation units
            end_offset = offset + length
            while offset < end_offset:
                # print(f"[{offset:x}] ", utils.format_array(buffer[offset:end_offset]))
                type = buffer[offset]
                offset += 1
                if type in CompilationUnit.COMPILATION_UNITS:
                    cu = CompilationUnit.COMPILATION_UNITS[type]()
                    cu.unpack(buffer[offset:])
                    self.compilation_units.append(cu)
                    offset += cu.get_size()
                elif type != CompilationUnit.DW_TAG_termination_zero and type != CompilationUnit.DW_TAG_unspecified_parameters:
                    raise Exception(f"ERROR: unknown compilation unit {type}")

        else:
            raise Exception(f'ERROR: unsupported Compilation Unit version:{self.members["cu_version"]} unit:{self.members["cu_unit_type"]}')

    def pack(self):
        buffer = self.pack()
        buffer.extend(self.cu_header.pack())
        return buffer

    def __str__(self):
        out = ""
        out += utils.formatter("Length", self.members["cu_length"], hex=True)
        out += utils.formatter("Version", self.members["cu_version"])
        out += utils.formatter("Unit Type", self.members["cu_unit_type"], table=CompilationUnit.DW_UNIT_TYPES)
        out += str(self.cu_header)
        for cu in self.compilation_units:
            out += str(cu)
        return out
