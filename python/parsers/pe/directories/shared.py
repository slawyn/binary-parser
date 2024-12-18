import utils
from packer import Packer


class Table(Packer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sections = []

    def set_sections(self, sections):
        self.sections = sections


class ImportObject:
    def __init__(self, iatrva, ordinal, nametablerva, hint, name, forwarder, value):
        self.Name = name
        self.IATAddressRVA = iatrva
        self.Ordinal = ordinal
        self.Hint = hint
        self.NameTableRVA = nametablerva
        self.Forwarder = forwarder
        self.value = value
        self.ForwarderString = ""

    @staticmethod
    def get_column_titles():
        out = ""
        out += utils.formatter2("%-20s", "[IATAddressRVA]")
        out += utils.formatter2("%-20s", "[Ordinal]")
        out += utils.formatter2("%-20s", "[Hint]")
        out += utils.formatter2("%-20s", "[NameTableRVA]")
        out += utils.formatter2("%-20s", "[Forwarder]")
        out += utils.formatter2("%-20s", "[ForwarderString]")
        out += utils.formatter2("%-20s", "[value]")
        out += utils.formatter2("%-40s", "[Name]")
        return out

    def __str__(self):
        out = ""
        out += utils.formatter2("%-20x",  self.IATAddressRVA)
        out += utils.formatter2("%-20x",  self.Ordinal)
        out += utils.formatter2("%-20x",  self.Hint)
        out += utils.formatter2("%-20x",  self.NameTableRVA)
        out += utils.formatter2("%-20x",  self.Forwarder)
        out += utils.formatter2("%-20s",  self.ForwarderString)
        out += utils.formatter2("%-20s",  self.value)
        out += utils.formatter2("%-40s",  self.Name)
        return out
