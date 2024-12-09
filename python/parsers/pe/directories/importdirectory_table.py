from packer import Packer
import utils

class IMPORTDIRECTORYTABLE(Packer):
    IDT_ILT_RVA_SZ = 4
    IDT_TIMESTAMP_SZ = 4
    IDT_FORWARDER_CHAIN_SZ = 4
    IDT_NAME_RVA_SZ = 4
    IDT_IAT_RVA_SZ = 4

    IDT_ILT_RVA_64SZ = 4
    IDT_TIMESTAMP_64SZ = 4
    IDT_FORWARDER_CHAIN_64SZ = 4
    IDT_NAME_RVA_64SZ = 4
    IDT_IAT_RVA_64SZ = 4

    def __init__(self, ILTRVA=0, timestamp=0, forwarder_chain=0, name_rva=0, IATRVA=0):
        super().__init__(
            {
                "idt_ilt_rva":ILTRVA,
                "idt_timestamp":timestamp,
                "idt_forwarder_chain":forwarder_chain,
                "idt_name_rva":name_rva,
                "idt_iat_rva":IATRVA
            }
        )
        self.importObjects = []
        self.nameOfDLL = ""

    def set_dll_name(self, name):
        self.nameOfDLL = name

    def get_dll_name(self):
        return self.nameOfDLL

    def is_empty(self):
        return self.members["idt_ilt_rva"]|self.members["idt_timestamp"]|self.members["idt_forwarder_chain"]|self.members["idt_name_rva"]|self.members["idt_iat_rva"] == 0

    def get_ilt_rva(self):
        return self.members["idt_ilt_rva"]
    
    def get_iat_rva(self):
        return self.members["idt_iat_rva"]
    
    def get_name_rva(self):
        return self.members["idt_name_rva"]
    
    def get_forwarder_chain(self):
        return self.members["idt_forwarder_chain"]

    def set_import_objects(self, io):
        self.importObjects = io

    def get_import_objects(self):
        return self.importObjects

    def __str__(self):
        out =""
        out += utils.formatter("nameOfDLL:", self.nameOfDLL)
        out += utils.formatter("ILTRVA:", self.members["idt_ilt_rva"])
        out += utils.formatter("TimeStamp:", self.members["idt_timestamp"])
        out += utils.formatter("ForwarderChain:", self.members["idt_forwarder_chain"], hex=True)
        out += utils.formatter("NameRVA:", self.members["idt_name_rva"])
        out += utils.formatter("IATRVA:", self.members["idt_iat_rva"])
        return out