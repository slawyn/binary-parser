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

    def set(is_64bit, is_little_endian):
        Packer.is_64bit = is_64bit
        Packer.is_little_endian = is_little_endian

    def _unpack(buffer):
        return utils.unpack(buffer, little_endian=Packer.is_little_endian)

    def _pack(data, size):
        return utils.pack(data, size, little_endian=Packer.is_little_endian)
    
    def _get(self, key):
        if not self.always_bit32 and Packer.is_64bit:
            return key.upper() + "_64SZ"
        return key.upper() + "_SZ"

    def unpack(self, buffer):
        offset = self.start_offset
        for key in self.members:
            self.members[key] = Packer._unpack(buffer[offset:offset + getattr(self, self._get(key))])
            offset += getattr(self,  self._get(key))
        return offset

    def pack(self):
        buffer = []
        for key in self.members:
            buffer.extend(Packer._pack(self.members[key], getattr(self, self._get(key))))
        return buffer