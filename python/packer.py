import utils

class Packer:
    is_64bit = False
    is_little_endian = False

    def __init__(self, members_32bit, members_64bit={}, start_offset=0, always_bit32=False):
        self.always_bit32 = always_bit32
        self.start_offset = start_offset

        if not self.always_bit32 and Packer.is_64bit and members_64bit:
            self.members = members_64bit
        else:
            self.members = members_32bit

    def get_starting_offset(self):
        return self.start_offset

    def set(is_64bit, is_little_endian):
        Packer.is_64bit = is_64bit
        Packer.is_little_endian = is_little_endian

    def _unpack(buffer, byte=False):
        return utils.unpack(buffer, byte=byte, little_endian=Packer.is_little_endian)

    def _pack(data, size, byte=False):
        return utils.pack(data, size, byte=byte, little_endian=Packer.is_little_endian)
    
    def _get(self, key):
        return key.upper() + "_64SZ" if not self.always_bit32 and Packer.is_64bit else key.upper() + "_SZ"
    
    def _is_variable_length(self, key):
        return hasattr(self, key.upper() + "_V")

    def unpack(self, buffer):
        s_offset = self.start_offset
        for key in self.members:
            e_offset = s_offset + getattr(self,  self._get(key))

            if self._is_variable_length(key):
                e_offset += Packer._unpack(buffer[s_offset:e_offset])
                data = Packer._unpack(buffer[s_offset:e_offset])
            else:
                data = Packer._unpack(buffer[s_offset:e_offset])

            self.members[key] = data
            s_offset = e_offset
        return s_offset

    def pack(self):
        buffer = []
        for key in self.members:
            data = self.members[key]
            buffer.extend(Packer._pack(data, getattr(self, self._get(key)), byte=type(data) == list))
        return buffer