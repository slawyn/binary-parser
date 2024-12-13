import utils
from packer import Packer
from parsers.pe.fileheader import FileHeader
from parsers.pe.optionalheader import OptionalHeader


class NtHeader:
    def __init__(self, data):
        self.Signature = utils.unpack(data[0:4])
        self.FileHeader_ = FileHeader()
        self.FileHeader_.unpack(data[4:])
        self.OptionalHeader_ = OptionalHeader(data[24:])
