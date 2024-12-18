from packer import Packer
import utils
from parsers.pe.directories.shared import Table


class TlsObject(Packer):
    TLS_RAWDATA_START_VA_SZ = 4
    TLS_RAWDATA_END_VA_SZ = 4
    TLS_ADDRESS_OF_INDEX_SZ = 4
    TLS_ADDRESS_OF_CALLBACKS_SZ = 4
    TLS_SIZE_OF_ZEROFILL_SZ = 4
    TLS_CHARACTERISTICS_SZ = 8

    TLS_RAWDATA_START_VA_64SZ = 8
    TLS_RAWDATA_END_VA_64SZ = 8
    TLS_ADDRESS_OF_INDEX_64SZ = 8
    TLS_ADDRESS_OF_CALLBACKS_64SZ = 8
    TLS_SIZE_OF_ZEROFILL_64SZ = 4
    TLS_CHARACTERISTICS_64SZ = 8

    def __init__(self, tls_rawdata_start_va=0, tls_rawdata_end_va=0,  tls_address_of_index=0, tls_address_of_callbacks=0, tls_size_of_zerofill=0, tls_characteristics=0):
        super().__init__(
            {
                "tls_rawdata_start_va": tls_rawdata_start_va,
                "tls_rawdata_end_va": tls_rawdata_end_va,
                "tls_address_of_index": tls_address_of_index,
                "tls_address_of_callbacks": tls_address_of_callbacks,
                "tls_size_of_zerofill": tls_size_of_zerofill,
                "tls_characteristics": tls_characteristics
            }
        )

    def is_empty(self):
        return self.members["tls_rawdata_start_va"] | self.members["tls_rawdata_end_va"] | self.members["tls_address_of_index"] | self.members["tls_address_of_callbacks"] | self.members["tls_size_of_zerofill"] | self.members["tls_characteristics"] == 0

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
        out += utils.formatter2("%-20x", self.members["tls_rawdata_start_va"])
        out += utils.formatter2("%-20x", self.members["tls_rawdata_end_va"])
        out += utils.formatter2("%-20x", self.members["tls_address_of_index"])
        out += utils.formatter2("%-20x", self.members["tls_address_of_callbacks"])
        out += utils.formatter2("%-20x", self.members["tls_size_of_zerofill"])
        out += utils.formatter2("%-20x", self.members["tls_characteristics"])
        return out


class TlsTable(Table):
    def __init__(self):
        super().__init__({})
        self.tls_objects = []

    def unpack(self, buffer):
        offset = self.offset
        while True:
            object = TlsObject()
            object.set_offset(offset)
            offset = object.unpack(buffer)

            if object.is_empty():
                break
            self.tls_objects.append(object)

    def __str__(self):
        out = f"\n[TLS]({len(self.tls_objects)})\n"
        out += f"{TlsObject.get_column_titles()}\n"
        for object in self.tls_objects:
            out += str(object)
            out += "\n"
        return out
