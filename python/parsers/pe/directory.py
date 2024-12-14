import utils
from packer import Packer


class DirectoryTable(Packer):
    DT_RVA_SZ = 4
    DT_SIZE_SZ = 4

    def __init__(self, rva=0, size=0):
        super().__init__(
            {
                "dt_rva": rva,
                "dt_size": size
            },
            always_32bit=True,
            always_little_endian=True
        )
        self.section_header = None

    def assign_section(self, section_header):
        self.section_header = section_header

    def has_section(self):
        return self.section_header

    def get_rva(self):
        return self.members['dt_rva']

    def get_size(self):
        return self.members['dt_size']

    def get_table_offset(self):
        return self.get_rva() - self.section_header.get_virtual_address() + self.section_header.get_pointer_to_raw_data()

    def __str__(self):
        out = ""
        out += utils.formatter2("%-20x", self.members['dt_rva'])
        out += utils.formatter2("%-20x", self.members['dt_size'])
        out += utils.formatter2("%-20s", self.section_header.get_formatted_name() if self.section_header else '')
        return out


class Directory(Packer):
    DIRECTORY_COUNT = 16

    def __init__(self):
        self.directory_tables = {
            "EXPORT": DirectoryTable(),
            "IMPORT": DirectoryTable(),
            "RESOURCE": DirectoryTable(),
            "EXCEPTION": DirectoryTable(),
            "CERTIFICATE": DirectoryTable(),
            "RELOCATION": DirectoryTable(),
            "DEBUG": DirectoryTable(),
            "ARCHITECTURE": DirectoryTable(),
            "GLOBALPTR": DirectoryTable(),
            "TLS": DirectoryTable(),
            "CONFIG": DirectoryTable(),
            "BOUNDIMPORT": DirectoryTable(),
            "IAT": DirectoryTable(),
            "DELAYIMPORT": DirectoryTable(),
            "META": DirectoryTable(),
            "RESERVED": DirectoryTable(),
        }

    def unpack(self, buffer):
        offset = 0
        for key, dt in self.directory_tables.items():
            dt.set_offset(offset)
            offset = dt.unpack(buffer)

    def pack(self):
        buffer = []
        for key, dt in self.directory_tables.items():
            buffer.extend(dt.pack())
        return buffer

    def get_table_directory(self, name):
        dt = self.directory_tables[name]
        return dt if dt.has_section() else None

    def assign_section_headers(self, section_headers):
        for key, dt in self.directory_tables.items():
            rva = dt.get_rva()
            size = dt.get_size()
            for sh in section_headers:
                sh_rva = sh.get_virtual_address()
                sh_size = sh.get_virtual_size()
                if rva >= sh_rva and rva <= sh_rva+sh_size:
                    dt.assign_section(sh)
                    break

    def get_number_of_directories(self):
        return Directory.DIRECTORY_COUNT

    def __str__(self):
        out = f"\n[Directory]({len(self.directory_tables)})\n"
        out += utils.formatter2("%-20s", "[Name]")
        out += utils.formatter2("%-20s", "[RVA]")
        out += utils.formatter2("%-20s", "[Size]")
        out += utils.formatter2("%-20s", "[Section]")
        out += "\n"
        for key, dt in self.directory_tables.items():
            out += utils.formatter2("%-20s", key)
            out += str(dt)
            out += "\n"
        return out
