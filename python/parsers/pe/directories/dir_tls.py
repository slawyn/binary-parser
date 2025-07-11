from packer import Packer
import utils
from parsers.pe.directories.shared import Table


class TlsObject(Packer):

    def __init__(self):
        super().__init__(
            {
                "tls_rawdata_start_va": 4,
                "tls_rawdata_end_va": 4,
                "tls_address_of_index": 4,
                "tls_address_of_callbacks": 4,
                "tls_size_of_zerofill": 4,
                "tls_characteristics": 8,
            },
            {
                "tls_rawdata_start_va": 8,
                "tls_rawdata_end_va": 8,
                "tls_address_of_index": 8,
                "tls_address_of_callbacks": 8,
                "tls_size_of_zerofill": 4,
                "tls_characteristics": 8,
            }
        )

    def is_empty(self):
        return (
            self.get_value("tls_rawdata_start_va")
            | self.get_value("tls_rawdata_end_va")
            | self.get_value("tls_address_of_index")
            | self.get_value("tls_address_of_callbacks")
            | self.get_value("tls_size_of_zerofill")
            | self.get_value("tls_characteristics")
        ) == 0

    @staticmethod
    def get_column_titles():
        out = ""
        out += utils.formatter2("%-20s", "[Start VA]")
        out += utils.formatter2("%-20s", "[End VA]")
        out += utils.formatter2("%-20s", "[Address of Index]")
        out += utils.formatter2("%-20s", "[Address of Callbacks]")
        out += utils.formatter2("%-20s", "[Size of Zerofill]")
        out += utils.formatter2("%-20s", "[Characteristics]")
        return out

    def __str__(self):
        out = ""
        out += utils.formatter2("%-20x", self.get_value("tls_rawdata_start_va"))
        out += utils.formatter2("%-20x", self.get_value("tls_rawdata_end_va"))
        out += utils.formatter2("%-20x", self.get_value("tls_address_of_index"))
        out += utils.formatter2("%-20x", self.get_value("tls_address_of_callbacks"))
        out += utils.formatter2("%-20x", self.get_value("tls_size_of_zerofill"))
        out += utils.formatter2("%-20x", self.get_value("tls_characteristics"))
        return out


class TlsTable(Table):
    def __init__(self):
        super().__init__({})
        self.tls_objects = []

    def unpack(self, buffer):
        offset = self.offset
        while True:
            obj = TlsObject()
            obj.set_offset(offset)
            offset = obj.unpack(buffer)

            if obj.is_empty():
                break
            self.tls_objects.append(obj)

    def __str__(self):
        out = f"\n[TLS]({len(self.tls_objects)})\n"
        out += f"{TlsObject.get_column_titles()}\n"
        for obj in self.tls_objects:
            out += str(obj)
            out += "\n"
        return out
