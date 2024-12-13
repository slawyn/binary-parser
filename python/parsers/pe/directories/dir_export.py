from packer import Packer
import utils


class ExportTable:
    def __init__(self, data, tables_fileoffset, sections):
        self.exportTable = []
        self.ExportFlags = utils.unpack(
            data[tables_fileoffset+0:tables_fileoffset+4])
        self.TimeStamp = utils.unpack(
            data[tables_fileoffset+4:tables_fileoffset+8])
        self.MajorVersion = utils.unpack(
            data[tables_fileoffset+8:tables_fileoffset+10])
        self.MinorVersion = utils.unpack(
            data[tables_fileoffset+10:tables_fileoffset+12])
        self.NameRVA = utils.unpack(
            data[tables_fileoffset+12:tables_fileoffset+16])
        self.OrdinalBase = utils.unpack(
            data[tables_fileoffset+16:tables_fileoffset+20])
        self.NumberOfFunctions = utils.unpack(
            data[tables_fileoffset+20:tables_fileoffset+24])
        self.NumberOfNames = utils.unpack(
            data[tables_fileoffset+24:tables_fileoffset+28])
        self.FunctionsRVA = utils.unpack(
            data[tables_fileoffset+28:tables_fileoffset+32])
        self.NamesRVA = utils.unpack(
            data[tables_fileoffset+32:tables_fileoffset+36])
        self.OrdinalsRVA = utils.unpack(
            data[tables_fileoffset+36:tables_fileoffset+40])

        # read offsets
        FunctionsFileOffset = utils.convert_rva_to_offset(self.FunctionsRVA, sections)
        NamesFileOffset = utils.convert_rva_to_offset(self.NamesRVA, sections)
        OrdinalsFileOffset = utils.convert_rva_to_offset(self.OrdinalsRVA, sections)
        NamesAndOrdinals = {}

        # read names and corresponding indexes
        numberofnames = self.NumberOfNames
        for i in range(self.NumberOfNames):
            NamesAndOrdinals[utils.unpack(data[OrdinalsFileOffset+i*2:OrdinalsFileOffset+i*2+2])
                             ] = utils.unpack(data[NamesFileOffset+i*4:NamesFileOffset+i*4+4])

        # create export table
        for i in range(self.NumberOfFunctions):
            FunctionAddress = utils.unpack(
                data[FunctionsFileOffset+i*4:FunctionsFileOffset+i*4+4])
            if FunctionAddress == 0:  # there are sometimes zero reserved entries for future use, which are currently not in use
                continue
            # if exported by name
            if i in NamesAndOrdinals.keys():
                namesoffset = utils.convert_rva_to_offset(NamesAndOrdinals[i], sections)
                symbol = utils.readstring(data, namesoffset)
                # Ordinal,address,hintg,string address, string
                self.exportTable.append(ExportObject(
                    i+self.OrdinalBase, FunctionAddress, i, NamesAndOrdinals[i], symbol))

            # if exported only by ordinal or is forwarded to imported function from another dll
            else:

                namesoffset = utils.convert_rva_to_offset(FunctionAddress, sections)
                symbol = ""
                # forwarded to another .dll
                if namesoffset > tables_fileoffset:
                    symbol = utils.readstring(data, namesoffset)
                # Zeroes because either exported by Ordinal or has forwarder RVA
                self.exportTable.append(ExportObject(
                    i+self.OrdinalBase, FunctionAddress, 0, 0, symbol))

# not part of the documentation: for internal use only


class ExportObject:
    def __init__(self, ordinal, functionrva, hint, namerva, name):
        self.Ordinal = ordinal
        self.Hint = hint
        self.FunctionRVA = functionrva
        self.NameRVA = namerva
        self.Name = name
