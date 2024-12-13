from packer import Packer
import utils


class TLSObject:
    def __init__(self, data, offset,  mode):
        idx = 16
        if mode:
            self.RawDataStartVA = utils.unpack(data[0+offset:8+offset])
            self.RawDataEndVA = utils.unpack(data[8+offset:16+offset])
            self.AddressOfIndex = utils.unpack(data[16+offset:24+offset])
            self.AddressOfCallbacks = utils.unpack(data[24+offset:32+offset])
            idx = 32

        else:

            self.RawDataStartVA = utils.unpack(data[offset:offset+4])
            self.RawDataEndVA = utils.unpack(data[4+offset:8+offset])
            self.AddressOfIndex = utils.unpack(data[8+offset:12+offset])
            self.AddressOfCallbacks = utils.unpack(data[12+offset:16+offset])

        self.SizeOfZeroFill = utils.unpack(data[offset+idx:offset+idx+4])
        self.Characteristics = utils.unpack(data[offset+idx+4:offset+idx+8])
        if (self.RawDataStartVA | self.RawDataEndVA | self.AddressOfIndex | self.AddressOfCallbacks | self.SizeOfZeroFill | self.Characteristics) == 0:
            self.isEmpty = True
        else:
            self.isEmpty = False


class TlsTable:
    def __init__(self, data, tables_fileoffset, mode):
        self.TLSObjects = []
        i = 0

        offset = 24
        if mode:
            offset = 40

        #
        while True:
            object = TLSObject(data, tables_fileoffset+offset*i, mode)

            i = i+1
            if object.isEmpty:
                break
            self.TLSObjects.append(object)
