from packer import Packer
import utils


class DosHeader(Packer):
    def __init__(self):
        super().__init__(
            {
                "dos_signature":    2,
                "dos_cblp":         2,
                "dos_cp":           2,
                "dos_crlc":         2,
                "dos_cparhdr":      2,
                "dos_minalloc":     2,
                "dos_maxalloc":     2,
                "dos_ss":           2,
                "dos_sp":           2,
                "dos_checksum":     2,
                "dos_ip":           2,
                "dos_cs":           2,
                "dos_lfarlc":       2,
                "dos_noverlay":     2,
                "dos_reserved1":    8,
                "dos_oemid":        2,
                "dos_oeminfo":      2,
                "dos_reserved2":    20,
                "dos_lfanew":       4
            }
        )

    def get_lfanew(self):
        return self.get_value('dos_lfanew')

    def __str__(self):
        out = "\n[DosHeader]\n"
        out += utils.formatter("Signature:", self.get_value('dos_signature'), hex=True)
        out += utils.formatter("LfAnew:", self.get_value('dos_lfanew'), hex=True)
        return out
