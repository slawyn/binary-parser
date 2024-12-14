import traceback
import utils
from packer import Packer
from parsers.pe.dosheader import DosHeader
from parsers.pe.sectionheader import SectionHeader
from parsers.pe.ntheader import NtHeader
from parsers.pe.fileheader import FileHeader
from parsers.pe.optionalheader import OptionalHeader
from parsers.pe.directory import Directory
from parsers.pe.directories.dir_import import ImportTable
from parsers.pe.directories.dir_delayimport import DelayImportTable
from parsers.pe.directories.dir_exception import ExceptionTable
from parsers.pe.directories.dir_export import ExportTable
from parsers.pe.directories.dir_tls import TlsTable


class PeParser:
    import_dic = {}
    delayimport_dic = {}
    delayimport_stubs_dic = {}
    tls_dic = {}
    exception_dic = {}
    section_files_to_disassemble = []

    def __init__(self, binary):
        try:
            self.dos_header = DosHeader()
            self.dos_header.unpack(binary)

            self.nt_header = NtHeader()
            self.nt_header.unpack(binary[self.dos_header.get_lfanew():])

            self.file_header = FileHeader()
            self.file_header.unpack(binary[self.dos_header.get_lfanew()
                                           + self.nt_header.get_members_size():])

            self.optional_header = OptionalHeader()
            self.optional_header.unpack(binary[self.dos_header.get_lfanew()
                                               + self.nt_header.get_members_size()
                                               + self.file_header.get_members_size():])

            self.directory = Directory()
            if self.optional_header.is64Bit:
                self.directory.unpack(binary[self.dos_header.get_lfanew()
                                             + self.nt_header.get_members_size()
                                             + self.file_header.get_members_size()
                                             + 112:])

            else:
                self.directory.unpack(binary[self.dos_header.get_lfanew()
                                             + self.nt_header.get_members_size()
                                             + self.file_header.get_members_size()
                                             + 96:])

            self.section_headers = []
            self.export_table = None
            self.import_table = None
            self.delay_import_table = None
            self.exception_table = None
            self.tls_table = None

            # FL offset + FL_SIZE+ PESignature_SIZE+PEHeader_SIZE
            offset = self.dos_header.get_lfanew()+20+4+224
            if self.optional_header.is64Bit:
                offset = self.dos_header.get_lfanew()+20+4+240  # peheader is bigger in pe32+

            # collect all section information
            for i in range(self.file_header.get_number_of_sections()):
                sh = SectionHeader()
                sh.unpack(binary[offset+40*i:])
                self.section_headers.append(sh)

            self.directory.assign_section_headers(self.section_headers)
            if td := self.directory.get_table_directory("EXPORT"):
                self.export_table = ExportTable(binary, td.get_table_offset(), self.section_headers)

            if td := self.directory.get_table_directory("IMPORT"):
                self.import_table = ImportTable(binary, td.get_table_offset(), self.section_headers, self.optional_header.is64Bit)

            if td := self.directory.get_table_directory("DELAYIMPORT"):
                self.delay_import_table = DelayImportTable(binary, td.get_table_offset(), self.section_headers, self.optional_header.is64Bit)

            if td := self.directory.get_table_directory("TLS"):
                self.tls_table = TlsTable(binary, td.get_table_offset(), self.optional_header.is64Bit)

            if td := self.directory.get_table_directory("EXCEPTION"):
                self.exception_table = ExceptionTable(binary,  td.get_table_offset(), self.section_headers)

        except Exception as e:
            traceback.print_exc()

    def __str__(self):
        out = str(self.dos_header)
        out += str(self.nt_header)
        out += str(self.file_header)
        out += str(self.optional_header)
        out += str(self.directory)
        out += f"\n[Sections]({len(self.section_headers)})\n"
        out += SectionHeader.get_column_titles() + "\n"
        for sh in self.section_headers:
            out += str(sh)
            out += "\n"

        if self.delay_import_table:
            out += self.GetDelayImports()

        if self.import_table:
            out += self.GetImports()

        if self.export_table:
            out += self.GetExports()

        if self.tls_table:
            out += self.GetTLSCallbacks()

        if self.exception_table:
            out += self.GetExceptions()

        return out

    def dump_code_sections(self, binary):
        codesections = self.GetCodeSections()
        section_files_to_disassemble = self.section_files_to_disassemble
        for i in range(len(codesections)):

            section_files_to_disassemble.append("code"+str(i))
            utils.log(section_files_to_disassemble[i]+".bin")

            # need to investigate which limits are good
            with open(section_files_to_disassemble[i]+".bin", "wb") as fd:
                lowerlimit = codesections[i].PointerToRawData
                upperlimit = codesections[i].PointerToRawData + codesections[i].VirtualSize

                if upperlimit > codesections[i].PointerToRawData+codesections[i].SizeOfRawData:
                    fd.write(binary[lowerlimit:upperlimit])
                    padding = upperlimit - codesections[i].PointerToRawData + codesections[i].SizeOfRawData
                    for i in range(padding):
                        fd.write("\x00")
                else:
                    fd.write(binary[lowerlimit:upperlimit])
            fd.close()

    def getSectionFilesToDisassemble(self):
        return self.section_files_to_disassemble

    def GetExports(self):
        NumberOfExports = len(self.export_table.exportTable)
        table = self.export_table.exportTable
        base = self.optional_header.get_image_base()
        out = ""
        exports = {}
        for i in range(NumberOfExports):
            address = "0x%x" % (table[i].FunctionRVA+base)
            name = ""
            if table[i].Name != "":
                name = table[i].Name
            else:
                name = "__exportedByOrdinal_%x" % (table[i].Ordinal)
            exports[table[i].FunctionRVA+base] = name
            out = out+address+"\t"+name+"\n"
        return out

    def GetTLSCallbacks(self):
        NumberOfCallbacks = len(self.tls_table.TLSObjects)
        table = self.tls_table.TLSObjects
        out = ""
        tls_dic = self.tls_dic
        for i in range(NumberOfCallbacks):
            address = "0x%x" % (table[i].AddressOfCallbacks)
            name = "__TLS_Callback_%x" % (table[i].AddressOfCallbacks)
            tls_dic[table[i].AddressOfCallbacks] = name
            out = out+address+"\t"+name+"\n"
        return out

    def GetDelayImports(self):
        out = ""
        base = self.optional_header.ImageBase
        delayimport_dic = self.delayimport_dic
        delayimport_stubs_dic = self.delayimport_stubs_dic
        for table in self.import_table.get_import_directory_tables():
            dlladdress = "0x%x" % (table.NameRVA+base)
            dllname = "#"+table.nameOfDLL
            out1 = dlladdress+"\t"+dllname+"\n"
            out = out+out1
            numberofobjects = table.numberOfImportObjects

            for j in range(numberofobjects):
                out2 = ""
                address = "0x%x" % (table.importObjects[j].IATAddressRVA+base)
                value = "0x%x" % (table.importObjects[j].value)
                name = ""
                if table.importObjects[j].Ordinal:
                    name = "__importedByOrdinal_%x" % (
                        table.importObjects[j].Ordinal)
                else:
                    name = "%s" % (table.importObjects[j].Name)

                delayimport_dic[table.importObjects[j].IATAddressRVA +
                                base] = table.nameOfDLL+"!"+name
                delayimport_stubs_dic[table.importObjects[j]
                                      .value] = table.nameOfDLL+"!"+name+"__stub"
                out = out+address+"\t"+value+"\t"+name+"\n"

        return out

    def GetCodeSections(self):
        sections = []
        for sh in self.section_headers:
            if (sh.Characteristics & 0x20000020) > 0:
                if sh.PointerToRawData != 0:
                    sections.append(sh)
        return sections

    def GetImports(self):
        base = self.optional_header.get_image_base()
        out = "\n[Imports]\n"
        import_dic = self.import_dic
        for table in self.import_table.get_import_directory_tables():
            dlladdress = f"{table.get_name_rva()+base:x}"
            dllname = table.get_dll_name()
            out1 = dlladdress+"\t"+dllname+"\n"
            out = out+out1

            for io in table.get_import_objects():
                address = f"  {io.IATAddressRVA + base:x}"
                name = ""
                if io.Forwarder:
                    name = "__forwarded__%s" % (io.Name)
                elif io.Ordinal:
                    name = "__importedByOrdinal_%x" % (
                        io.Ordinal)
                else:
                    name = "%s" % (io.Name)
                import_dic[io.IATAddressRVA +
                           base] = table.nameOfDLL+"!"+name
                out = out+address+"\t"+name+"\n"

        return out

    def GetExceptions(self):
        NumberOfExceptions = len(self.exception_table.ExceptionObjects)
        base = self.optional_header.get_image_base()
        out = ""
        exception_dic = self.exception_dic
        exceptionobjects = self.exception_table.ExceptionObjects

        for i in range(NumberOfExceptions):
            out2 = ""
            out3 = ""
            out4 = ""

            entry = exceptionobjects[i]

            startva = "0x%x" % (entry.StartRVA+base)
            endva = "0x%x" % (entry.EndRVA+base)

            exception_dic[entry.StartRVA+base] = entry.EndRVA+base
            unwindinfo = entry.UnwindInfo

            '''
			# information about stackunwinding
			out2="\tVersion:%x \tFlags:%s \tCountOfCodes:%d \tFrameRegister:%s \tFrameOffset:0x%x"%(
			    unwindinfo.Version, unwindinfo.getFlags(),unwindinfo.CountofCodes, unwindinfo.getFrameRegister(), unwindinfo.FrameOffset)


			countofcodes=unwindinfo.CountofCodes


			for i in range(countofcodes):
				out3=out3+"\t"+unwindinfo.Codes[i]+"\n"


			flags = entry.UnwindInfo.Flags


			if flags == 0x4:	#chained
				pass

			elif flags & 0x3:	#e-/uhandler
				rva = "Handler Address:0x%x"%(
				    entry.UnwindInfo.ExceptionHandler.HandlerRVA+base)
				nmofscopetables = entry.UnwindInfo.ExceptionHandler.ScopeTableCount
				if nmofscopetables <5: #dunno how to recognize if it's data or scopetables
					count= "Count: 0x%x"%(nmofscopetables)
					out4="\t\t"+rva+"\t"+count+"\n"
					for i in range(nmofscopetables):
						table = entry.UnwindInfo.ExceptionHandler.ScopeTables[i]
						out4=out4+"\t\tScope Table:\n\t\t\tStart:0x%x\n\t\t\tEnd:0x%x\n\t\t\tHandler Address:0x%x\n\t\t\tJump Target:0x%x"%(
						    table.StartRVA+base,table.EndRVA+base,table.HandlerRVA+base, table.JumpTarget+base)
				else:
					data= "Data: 0x%x"%(nmofscopetables)
					out4="\t\t"+rva+"\t"+data+"\n"
			'''
            out = out+"".join([startva, "\t", endva, "\n"])

        return out
