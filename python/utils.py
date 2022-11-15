import struct
import datetime
import os


def log(s):
    """Logging function
    """
    print("%s ## %s" % (datetime.datetime.now().time(), s))


def write_file(filename, buffer):
    """Write buffer into file
    """
    if os.path.isfile(filename):
        os.remove(filename)

    with open(filename, "wb") as f:
        f.write(buffer)
        f.close()

    log("[%s] Written Bytes: %s" % (filename, len(buffer)))


def load_file(filename):
    """Load binary file into buffer
    """
    bytes = []
    with open(filename, "rb") as f:
        bytes = f.read()

    log("[%s] Read Bytes: %s" % (filename, len(bytes)))
    return bytes


def unpack_str(buffer):
    return struct.unpack("s", buffer)


STRUCT_FORMAT = {1: "B", 2: "H", 4: "I", 8: "Q"}


def unpack(buffer, big_endian):
    """Unpack buffer
    """
    idx = len(buffer)
    if big_endian:
        return struct.unpack(">" + STRUCT_FORMAT[idx], buffer)[0]
    return struct.unpack("<" + STRUCT_FORMAT[idx], buffer)[0]


def unpackuint8(data):
    return struct.unpack("<B", data)[0]


def unpackint8(data):
    return struct.unpack("<b", data)[0]


def unpackuint16(data):
    return struct.unpack("<H", data)[0]


def unpackint16(data):
    return struct.unpack("<h", data)[0]


def unpackuint32(data):
    return struct.unpack("<I", data)[0]


def unpackint32(data):
    return struct.unpack("<i", data)[0]


def unpackuint64(data):
    return struct.unpack("<Q", data)[0]


def unpackint64(data):
    return struct.unpack("<q", data)[0]


def readstring(data, offset):
    i = 0
    string = ""
    while (data[offset + i] != 0):
        if data[offset + i] >= 32 and data[offset+i] <= 126:
            string += chr(data[offset + i])
        else:
            string += str(data[offset + i])
        i += 1

    return string


def convertRVAToOffset(address, sections):
    for section in sections:
        if address >= section.VirtualAddress and \
           address <= (section.VirtualAddress+section.VirtualSize):

            return (address - section.VirtualAddress) + section.PointerToRawData
