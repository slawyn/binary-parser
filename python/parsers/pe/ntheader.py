import utils
from packer import Packer


class NtHeader(Packer):
    def __init__(self):
        super().__init__({"nt_signature": 4})

    def __str__(self):
        out = "\n[NtHeader]\n"
        out += utils.formatter("Signature:", self.get_value("nt_signature"), hex=True)
        return out
