from packer import Packer
import utils
from parsers.pe.directories.shared import Table


class ExportTable(Table):
    ET_EXPORT_FLAGS_SZ = 4
    ET_TIMESTAMP_SZ = 4
    ET_MAJOR_VERSION_SZ = 2
    ET_MINOR_VERSION_SZ = 2
    ET_NAME_RVA_SZ = 4
    ET_ORDINAL_BASE_SZ = 4
    ET_NUMBER_OF_FUNCTIONS_SZ = 4
    ET_NUMBER_OF_NAMES_SZ = 4
    ET_FUNCTIONS_RVA_SZ = 4
    ET_NAMES_RVA_SZ = 4
    ET_ORDINALS_RVA_SZ = 4

    def __init__(self, export_flags=0, timestamp=0, major_version=0, minor_version=0, name_rva=0, ordinal_base=0, number_of_functions=0, number_of_names=0, functions_rva=0, names_rva=0, ordinals_rva=0):
        super().__init__(
            {
                "et_export_flags": export_flags,
                "et_timestamp": timestamp,
                "et_major_version": major_version,
                "et_minor_version": minor_version,
                "et_name_rva": name_rva,
                "et_ordinal_base": ordinal_base,
                "et_number_of_functions": number_of_functions,
                "et_number_of_names": number_of_names,
                "et_functions_rva": functions_rva,
                "et_names_rva": names_rva,
                "et_ordinals_rva": ordinals_rva
            },
            always_32bit=True
        )
        self.exportTable = []

    def get_function_rva(self):
        return self.members["et_functions_rva"]

    def unpack(self, buffer):
        super().unpack(buffer)

        # read offsets
        FunctionsFileOffset = utils.convert_rva_to_offset(self.members["et_functions_rva"], self.sections)
        NamesFileOffset = utils.convert_rva_to_offset(self.members["et_names_rva"], self.sections)
        OrdinalsFileOffset = utils.convert_rva_to_offset(self.members["et_ordinals_rva"], self.sections)
        NamesAndOrdinals = {}

        # read names and corresponding indexes
        for i in range(self.members["et_number_of_names"]):
            NamesAndOrdinals[utils.unpack(buffer[OrdinalsFileOffset+i*2:OrdinalsFileOffset+i*2+2])] = utils.unpack(buffer[NamesFileOffset+i*4:NamesFileOffset+i*4+4])

        # create export table
        for i in range(self.members["et_number_of_functions"]):
            FunctionAddress = utils.unpack(buffer[FunctionsFileOffset+i*4:FunctionsFileOffset+i*4+4])
            if FunctionAddress == 0:  # there are sometimes zero reserved entries for future use, which are currently not in use
                continue
            # if exported by name
            if i in NamesAndOrdinals.keys():
                namesoffset = utils.convert_rva_to_offset(NamesAndOrdinals[i], self.sections)
                symbol = utils.readstring(buffer, namesoffset)
                # Ordinal, address, hint, string address, string
                self.exportTable.append(ExportObject(i+self.members["et_ordinal_base"], FunctionAddress, i, NamesAndOrdinals[i], symbol))
            # if exported only by ordinal or is forwarded to imported function from another dll
            else:
                # forwarded to another .dll
                namesoffset = utils.convert_rva_to_offset(FunctionAddress, self.sections)
                symbol = utils.readstring(buffer, namesoffset)
                # Zeroes because either exported by Ordinal or has forwarder RVA
                self.exportTable.append(ExportObject(i+self.members["et_ordinal_base"], FunctionAddress, 0, 0, symbol))

    def __str__(self):
        out = f"\n[Exports]({len(self.exportTable)})\n"
        out += f"{ExportObject.get_column_titles()}\n"
        for object in self.exportTable:
            out += str(object)
            out += "\n"
        return out


class ExportObject:
    def __init__(self, ordinal, function_rva, hint, name_rva, name):
        self.ordinal = ordinal
        self.hint = hint
        self.function_rva = function_rva
        self.name_rva = name_rva
        self.name = name

    @staticmethod
    def get_column_titles():
        out = ""
        out += utils.formatter2("%-20s", "[Name]")
        out += utils.formatter2("%-20s", "[Ordinal]")
        out += utils.formatter2("%-20s", "[Hint]")
        out += utils.formatter2("%-20s", "[Function RVA]")
        out += utils.formatter2("%-20s", "[Name RVA]")
        return out

    def __str__(self):
        out = ""
        out += utils.formatter2("%-20s",  self.name)
        out += utils.formatter2("%-20x",  self.ordinal)
        out += utils.formatter2("%-20s",  self.hint)
        out += utils.formatter2("%-20s",  self.function_rva)
        out += utils.formatter2("%-20s",  self.name)
        return out

    def get_function_rva(self):
        return self.function_rva
