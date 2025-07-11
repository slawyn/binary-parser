from packer import Packer
import utils
from parsers.pe.directories.shared import Table


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
        out += utils.formatter2("%-20s", self.name)
        out += utils.formatter2("%-20x", self.ordinal)
        out += utils.formatter2("%-20s", self.hint)
        out += utils.formatter2("%-20s", self.function_rva)
        out += utils.formatter2("%-20s", self.name)
        return out

    def get_function_rva(self):
        return self.function_rva


class ExportTable(Table):

    def __init__(self):
        super().__init__(
            {
                "et_export_flags": 4,
                "et_timestamp": 4,
                "et_major_version": 2,
                "et_minor_version": 2,
                "et_name_rva": 4,
                "et_ordinal_base": 4,
                "et_number_of_functions": 4,
                "et_number_of_names": 4,
                "et_functions_rva": 4,
                "et_names_rva": 4,
                "et_ordinals_rva": 4,
            },
            always_32bit=True,
        )
        self.exportObjects = []

    def get_function_rva(self):
        return self.get_value("et_functions_rva")

    def unpack(self, buffer):
        super().unpack(buffer)

        # read offsets
        FunctionsFileOffset = utils.convert_rva_to_offset(self.get_value("et_functions_rva"), self.sections)
        NamesFileOffset = utils.convert_rva_to_offset(self.get_value("et_names_rva"), self.sections)
        OrdinalsFileOffset = utils.convert_rva_to_offset(self.get_value("et_ordinals_rva"), self.sections)
        NamesAndOrdinals = {}

        # read names and corresponding indexes
        for i in range(self.get_value("et_number_of_names")):
            NamesAndOrdinals[utils.unpack(buffer[OrdinalsFileOffset + i * 2: OrdinalsFileOffset + i * 2 + 2])
                             ] = utils.unpack(buffer[NamesFileOffset + i * 4: NamesFileOffset + i * 4 + 4])

        # create export table
        for i in range(self.get_value("et_number_of_functions")):
            FunctionAddress = utils.unpack(buffer[FunctionsFileOffset + i * 4: FunctionsFileOffset + i * 4 + 4])
            if FunctionAddress == 0:
                continue
            # if exported by name
            if i in NamesAndOrdinals.keys():
                namesoffset = utils.convert_rva_to_offset(NamesAndOrdinals[i], self.sections)
                symbol = utils.readstring(buffer, namesoffset)
                self.exportObjects.append(ExportObject(
                    i + self.get_value("et_ordinal_base"), FunctionAddress, i, NamesAndOrdinals[i], symbol))
            # if exported only by ordinal or is forwarded to imported function from another dll
            else:
                # forwarded to another .dll
                namesoffset = utils.convert_rva_to_offset(FunctionAddress, self.sections)
                symbol = utils.readstring(buffer, namesoffset)
                # Zeroes because either exported by Ordinal or has forwarder RVA
                self.exportObjects.append(ExportObject(
                    i + self.get_value("et_ordinal_base"), FunctionAddress, 0, 0, symbol))

    def __str__(self):
        out = f"\n[Exports]({len(self.exportObjects)})\n"
        out += f"{ExportObject.get_column_titles()}\n"
        for object in self.exportObjects:
            out += str(object)
            out += "\n"
        return out
