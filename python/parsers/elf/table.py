import utils

class StringTable:

    def __init__(self, section_header, section_data):
        self.section_header = section_header
        self.section_data = section_data

    def find_string(self, str_idx):
        return utils.readstring(self.section_data.get_data(), str_idx)

    def add_string(self):
        str_idx = self.section_data.get_size()
        utils.update(f".partial_{str_idx:x}\0".encode(), self.section_data.get_data(), str_idx)
        self.section_header.set_size(self.section_data.get_size())
        return str_idx