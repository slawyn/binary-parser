class ImportObject:
    def __init__(self, iatrva, ordinal, nametablerva, hint, name, forwarder, value):
        self.IATAddressRVA = iatrva
        self.Ordinal = ordinal
        self.Hint = hint
        self.NameTableRVA = nametablerva
        self.Name = name
        self.Forwarder = forwarder
        self.value = value
        self.ForwarderString = ""
