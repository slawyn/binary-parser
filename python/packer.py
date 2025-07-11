import utils


class Member:
    def __init__(self, size):
        self.value = 0
        self.size = size

    def get_value(self):
        return self.value


class Packer:
    is_64bit = False
    is_little_endian = False

    def __init__(self, members_32bit, members_64bit={}, start_offset=0, always_32bit=False, always_little_endian=True):
        self.always_32bit = not members_64bit
        self.always_little_endian = always_little_endian
        self.offset = start_offset

        if not self.always_32bit and Packer.is_64bit and members_64bit:
            selected = members_64bit
        else:
            selected = members_32bit

        self.members = {}
        for key, size in selected.items():
            self.members[key] = Member(size)

    def key_exists(self, key):
        return key in self.members

    def get_value(self, key):
        if key in self.members:
            return self.members[key].get_value()
        else:
            raise KeyError(f"Member '{key}' not found in Packer.")

    def get_members_size(self):
        return sum([member.size for member in self.members.values()])

    def get_offset(self):
        return self.offset

    def set_offset(self, offset):
        self.offset = offset

    def set_packer_config(is_64bit=False, is_little_endian=False):
        Packer.is_64bit = is_64bit
        Packer.is_little_endian = is_little_endian

    def _unpack(self, buffer, byte=False):
        return utils.unpack(buffer, byte=byte, little_endian=Packer.is_little_endian or self.always_little_endian)

    def _pack(self, data, size, byte=False):
        return utils.pack(data, size, byte=byte, little_endian=Packer.is_little_endian and self.always_little_endian)

    def _is_variable_length(self, key):
        return hasattr(self, key.upper() + "_V")

    def unpack(self, buffer):
        s_offset = self.offset
        for member in self.members.values():
            e_offset = s_offset + member.size

            if member.size == 0:
                e_offset += self._unpack(buffer[s_offset:e_offset+1])
                value = self._unpack(buffer[s_offset:e_offset])
            else:
                value = self._unpack(buffer[s_offset:e_offset])

            member.value = value
            s_offset = e_offset
        return s_offset

    def pack(self):
        buffer = []
        for member in self.members.values():
            buffer.extend(self._pack(member.value, member.size, byte=type(member.value) == list))
        return buffer
