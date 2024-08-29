import utils

class Packer:
    is_64bit = False
    is_little_endian = False

    def set(is_64bit, is_little_endian):
        Packer.is_64bit = is_64bit
        Packer.is_little_endian = is_little_endian

    def unpack(buffer):
        return utils.unpack(buffer, little_endian=Packer.is_little_endian)

    def pack(data, size):
        return utils.pack(data, size, little_endian=Packer.is_little_endian)

    def get(key, override=False):
        if not override and Packer.is_64bit == True:
            return key.upper() + "_64SZ"
        return key.upper() + "_SZ"