from packer import Packer
import utils


class DosHeader(Packer):
    DOS_SIGNATURE_SZ = 2
    DOS_CBLP_SZ = 2
    DOS_CP_SZ = 2
    DOS_CRLC_SZ = 2
    DOS_CPARHDR_SZ = 2
    DOS_MINALLOC_SZ = 2
    DOS_MAXALLOC_SZ = 2
    DOS_SS_SZ = 2
    DOS_SP_SZ = 2
    DOS_CHECKSUM_SZ = 2
    DOS_IP_SZ = 2
    DOS_CS_SZ = 2
    DOS_LFARLC_SZ = 2
    DOS_NOVERLAY_SZ = 2
    DOS_RESERVED1_SZ = 8
    DOS_OEMID_SZ = 2
    DOS_OEMINFO_SZ = 2
    DOS_RESERVED2_SZ = 20
    DOS_LFANEW_SZ = 4

    def __init__(self, signature=0, cblp=0, cp=0, crlc=0, cparhdr=0, minalloc=0, maxalloc=0, ss=0, sp=0, checksum=0, ip=0, cs=0, lfarlc=0, noverlay=0, reserved1=None, oemid=0, oeminfo=0, reserved2=None, lfanew=0):
        super().__init__(
            {
                "dos_signature":  signature,
                "dos_cblp": cblp,
                "dos_cp":         cp,
                "dos_crlc":       crlc,
                "dos_cparhdr":    cparhdr,
                "dos_minalloc":   minalloc,
                "dos_maxalloc":   maxalloc,
                "dos_ss":         ss,
                "dos_sp":         sp,
                "dos_checksum":   checksum,
                "dos_ip":        ip,
                "dos_cs":         cs,
                "dos_lfarlc": lfarlc,
                "dos_noverlay": noverlay,
                "dos_reserved1": reserved1,
                "dos_oemid": oemid,
                "dos_oeminfo": oeminfo,
                "dos_reserved2": reserved2,
                "dos_lfanew": lfanew
            },
            always_32bit=True
        )

    def get_lfanew(self):
        return self.members['dos_lfanew']

    def __str__(self):
        out = "\n[DosHeader]\n"
        out += utils.formatter("Signature:", self.members['dos_signature'], hex=True)
        return out
