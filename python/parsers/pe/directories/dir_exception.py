from packer import Packer
import utils
from parsers.pe.directories.shared import Table


class ScopeTable:
    def __init__(self, startrva, endrva, handlerrva, jumptarget):
        self.StartRVA = startrva
        self.EndRVA = endrva
        self.HandlerRVA = handlerrva
        self.JumpTarget = jumptarget


class ExceptionHandler:
    def __init__(self, handlerrva, count,  scopetables):
        self.HandlerRVA = handlerrva
        self.ScopeTableCount = count
        self.ScopeTables = scopetables


class UnwindInfoObject:
    _flagtypes = {
        0: "UNW_FLAG_NO_HANDLER",
        1: "UNW_FLAG_EHANDLER",
        2: "UNW_FLAG_UHANDLER",
        3: "UNW_FLAG_FHANDLER",
        4: "UNW_FLAG_CHAININFO"
    }
    _registers = ["rax", "rcx", "rdx", "rbx", "rsp", "rbp", "rsi",
                  "rdi", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]
    _codes = {0: "UWOP_PUSH_NONVOL",
              1: "UWOP_ALLOC_LARGE",
              2: "UWOP_ALLOC_SMALL",
              3: "UWOP_SET_FPREG",
              4: "UWOP_SAVE_NONVOL",
              5: "UWOP_SAVE_NONVOL_FAR",
              8: "UWOP_SAVE_XMM128",
              9: "UWOP_SAVE_XMM128_FAR",
              10: "UWOP_PUSH_MACHFRAME"
              }

    def __init__(self, version, flags, sizeofprolog, countofcodes, frameregister, frameregisteroff, codes, handler):
        self.Version = version
        self.Flags = flags
        self.SizeofProlog = sizeofprolog
        self.CountofCodes = countofcodes
        self.FrameRegister = frameregister
        self.FrameOffset = frameregisteroff
        self.Codes = []
        for i in range(len(codes)):

            offset = (codes[i] & 0xFF)
            opcode = (codes[i] & 0xF000) >> 12
            opinfo = (codes[i] & 0xF00) >> 8
            out = self.decode(offset, opcode, opinfo)
            self.Codes.append(out)

        self.ExceptionHandler = handler

    def decode(self, offset, opcode, opinfo):
        out = "0x%x:" % (offset)
        out = out + " opcode: 0x%x" % (opcode)
        out = out + " opinfo: 0x%x" % (opinfo)

        return out

    def getFlags(self):
        return self._flagtypes[self.Flags]

    def getFrameRegister(self):
        return self._registers[self.FrameRegister]


class ExceptionObject:
    def __init__(self, data, offset):
        self.StartRVA = utils.unpack(data[0+offset:4+offset])
        self.EndRVA = utils.unpack(data[4+offset:8+offset])
        self.UnwindInfoPtr = utils.unpack(data[8+offset:12+offset])
        self.UnwindInfo = None
        self.isEmpty = False
        if self.StartRVA | self.EndRVA | self.UnwindInfoPtr == 0:
            self.isEmpty = True


class ExceptionTable(Table):
    def __init__(self):
        super().__init__({})
        self.exceptionObjects = []

    def unpack(self, buffer):
        sections = self.sections
        offset = self.offset
        idx = 0
        while True:
            object = ExceptionObject(buffer, offset+idx*24)
            if object.isEmpty:
                break

            unwindinfooff = utils.convert_rva_to_offset(object.UnwindInfoPtr, sections)

            t = utils.unpack(buffer[unwindinfooff:unwindinfooff+1])

            version = t & 0b00000111
            flags = (t & 0b11111000) >> 3

            szprolog = utils.unpack(buffer[unwindinfooff+1:unwindinfooff+2])
            countofcodes = utils.unpack(buffer[unwindinfooff+2:unwindinfooff+3])
            t = utils.unpack(buffer[unwindinfooff+3:unwindinfooff+4])

            frameregister = t & 0b00001111
            frameregisteroff = (t & 0b11110000) >> 4

            # codes and exception handler
            codes = []
            codesoffset = unwindinfooff+4
            for j in range(countofcodes):
                codes.append(utils.unpack(buffer[codesoffset+j*2:codesoffset+2+j*2]))

            handler = None

            if flags & 0x3:  # 1 - 3 we have a handler
                # the rva of the handler must be aligned after the code
                handlerreloffset = (countofcodes % 2+countofcodes)*2
                handlerinfooffset = codesoffset+handlerreloffset
                exceptharva = utils.unpack(buffer[handlerinfooffset:handlerinfooffset+4])

                count = utils.unpack(buffer[handlerinfooffset+4:handlerinfooffset+8])
                scoptableoffset = handlerinfooffset+8
                scopetables = []

                if count < 5:

                    scopes = 0

                    for i in range(count):
                        scopes = i*16

                        startrva = utils.unpack(buffer[scoptableoffset+scopes:scoptableoffset+scopes+4])
                        endrva = utils.unpack(buffer[scoptableoffset+4+scopes:scoptableoffset+8+scopes])
                        handlerrva = utils.unpack(buffer[scoptableoffset+8+scopes:scoptableoffset+12+scopes])
                        jumptarget = utils.unpack(buffer[scoptableoffset+12+scopes:scoptableoffset+16+scopes])
                        scopetables.append(ScopeTable(startrva, endrva, handlerrva, jumptarget))

                handler = ExceptionHandler(exceptharva, count, scopetables)

            object.UnwindInfo = UnwindInfoObject(
                version, flags, szprolog, countofcodes, frameregister, frameregisteroff, codes, handler)

            idx = idx+1
            self.exceptionObjects.append(object)

    def __str__(self):
        out = ""
        NumberOfExceptions = len(self.exceptionObjects)
        for i in range(NumberOfExceptions):
            out2 = ""
            out3 = ""
            out4 = ""

            entry = self.exceptionObjects[i]

            startva = "0x%x" % (entry.StartRVA)
            endva = "0x%x" % (entry.EndRVA)

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
