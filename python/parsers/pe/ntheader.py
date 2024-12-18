import utils
from packer import Packer
from parsers.pe.fileheader import FileHeader
from parsers.pe.optionalheader import OptionalHeader


class NtHeader(Packer):
    NT_SIGNATURE_SZ = 4

    def __init__(self, nt_signature=0):
        super().__init__(
            {
                "nt_signature": nt_signature
            },
            always_32bit=True,
            always_little_endian=True
        )

    def __str__(self):
        out = "\n[NtHeader]\n"
        out += utils.formatter("Signature:", self.members['nt_signature'], hex=True)
        return out
