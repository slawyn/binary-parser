import struct
import datetime
import os
from datetime import datetime
from random import randint
import json

STRUCT_FORMAT = {1: "B", 2: "H", 4: "I", 8: "Q"}


def log(*args):
    global tsc_prev
    global pQueue
    ''' Logs information
        -> v(str): input string
    '''
    date_time = datetime.now()

    v = ""
    for a in args:
        v += str(a)

    o = f"{date_time}::{v}\n"
    print(o,  end="")


def read_binary(file_path):
    with open(file_path, 'rb') as f:
        return bytearray(f.read())


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


def unpack(buffer, little_endian=True):
    '''Unpack buffer
    '''
    idx = len(buffer)
    if idx in STRUCT_FORMAT:
        if little_endian:
            return struct.unpack("<" + STRUCT_FORMAT[idx], buffer)[0]
        return struct.unpack(">" + STRUCT_FORMAT[idx], buffer)[0]
    return buffer


def pack(data, size, little_endian=True):
    '''Pack data into buffer
    '''
    if size in STRUCT_FORMAT:
        if little_endian:
            return struct.pack("<" + STRUCT_FORMAT[size], data)
        return struct.pack(">" + STRUCT_FORMAT[size], data)
    return data


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

    while data[offset + i] != 0:
        if 32 <= data[offset + i] <= 126:
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


def read_json(filename):
    with open(filename, 'r') as fo:
        data = json.load(fo)
    return data


def read_file(filename):
    data = b""
    with open(filename, 'rb') as fo:
        data = fo.read()
    return data


def write_file(filename, data, out_type='binary'):
    if out_type == 'text':
        with open(filename, 'w+') as fo:
            fo.write(data)
    elif out_type == 'json':
        with open(filename, 'w+') as fo:
            json.dump(data, fo, indent=4)
    else:
        with open(filename, 'wb+') as fo:
            fo.write(data)


def convert_list_to_bytes(int_list):
    byte_list = b""
    for k in int_list:
        byte_list += k.to_bytes(4, "big")

    return byte_list


def convert_int_to_list(integer, little_endian=True):

    if little_endian:
        return [integer >> 24, integer >> 16 & 0xFF, integer >> 8 & 0xFF, integer & 0xFF]
    return [integer & 0xFF, integer >> 8 & 0xFF, integer >> 16 & 0xFF, integer >> 24]


def generate_random_bytes(size):
    rnd_bytes = b""
    for i in range(size):
        rnd_bytes += randint(0, 255).to_bytes(1, "big")
    return rnd_bytes


def compare(first, second):
    if len(first) != len(second):
        return False
    else:
        for fidx in range(len(first)):
            if first[fidx] != second[fidx]:
                return False

    return True
