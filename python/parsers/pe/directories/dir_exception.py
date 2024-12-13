from packer import Packer
import utils


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


class ExceptionTable:
    def __init__(self, data, tables_fileoffset, sections):
        self.ExceptionObjects = []
        offset = 24
        idx = 0
        exceptionbjectsappend = self.ExceptionObjects.append
        while True:
            object = ExceptionObject(data, tables_fileoffset+idx*offset)
            if object.isEmpty:
                break

            unwindinfooff = utils.convert_rva_to_offset(object.UnwindInfoPtr, sections)

            t = utils.unpack(data[unwindinfooff:unwindinfooff+1])

            version = t & 0b00000111
            flags = (t & 0b11111000) >> 3

            szprolog = utils.unpack(data[unwindinfooff+1:unwindinfooff+2])
            countofcodes = utils.unpack(data[unwindinfooff+2:unwindinfooff+3])
            t = utils.unpack(data[unwindinfooff+3:unwindinfooff+4])

            frameregister = t & 0b00001111
            frameregisteroff = (t & 0b11110000) >> 4

            # codes and exception handler
            codes = []
            codesoffset = unwindinfooff+4
            for j in range(countofcodes):
                codes.append(utils.unpack(
                    data[codesoffset+j*2:codesoffset+2+j*2]))

            handler = None

            if flags & 0x3:  # 1 - 3 we have a handler
                # the rva of the handler must be aligned after the code
                handlerreloffset = (countofcodes % 2+countofcodes)*2
                handlerinfooffset = codesoffset+handlerreloffset
                exceptharva = utils.unpack(
                    data[handlerinfooffset:handlerinfooffset+4])

                count = utils.unpack(
                    data[handlerinfooffset+4:handlerinfooffset+8])
                scoptableoffset = handlerinfooffset+8
                scopetables = []

                if count < 5:

                    scopes = 0

                    for i in range(count):
                        scopes = i*16

                        startrva = utils.unpack(
                            data[scoptableoffset+scopes:scoptableoffset+scopes+4])
                        endrva = utils.unpack(
                            data[scoptableoffset+4+scopes:scoptableoffset+8+scopes])
                        handlerrva = utils.unpack(
                            data[scoptableoffset+8+scopes:scoptableoffset+12+scopes])
                        jumptarget = utils.unpack(
                            data[scoptableoffset+12+scopes:scoptableoffset+16+scopes])
                        scopetables.append(ScopeTable(
                            startrva, endrva, handlerrva, jumptarget))

                handler = ExceptionHandler(exceptharva, count, scopetables)

            object.UnwindInfo = UnwindInfoObject(
                version, flags, szprolog, countofcodes, frameregister, frameregisteroff, codes, handler)

            idx = idx+1
            exceptionbjectsappend(object)
