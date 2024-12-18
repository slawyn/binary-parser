import struct
import datetime
import os
from datetime import datetime
from random import randint
import json

STRUCT_FORMAT = {1: "B", 2: "H", 4: "I", 8: "Q"}
STRUCT_FORMAT_SIGNED = {1: "b", 2: "h", 4: "i", 8: "q"}


def convert_rva_to_offset(address, sections):
    for section in sections:
        if address >= section.get_virtual_address() and address <= (section.get_virtual_address()+section.get_virtual_size()):
            return (address - section.get_virtual_address()) + section.get_pointer_to_raw_data()


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


def get_alignment_count(address, alignment):
    return ((address + (alignment - 1)) & ~(alignment-1)) - address


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


def unpack(buffer, byte=False, little_endian=True, unsigned=True):
    '''Unpack buffer
    '''
    idx = len(buffer)
    if idx not in STRUCT_FORMAT or byte:
        return list(struct.unpack(f"<{idx}B", buffer))

    if unsigned:
        if little_endian:
            return struct.unpack("<" + STRUCT_FORMAT[idx], buffer)[0]
        return struct.unpack(">" + STRUCT_FORMAT[idx], buffer)[0]
    else:
        if little_endian:
            return struct.unpack("<" + STRUCT_FORMAT_SIGNED[idx], buffer)[0]
        return struct.unpack(">" + STRUCT_FORMAT_SIGNED[idx], buffer)[0]


def pack(data, size, byte=False, little_endian=True, unsigned=True):
    '''Pack data into buffer
    '''
    if size not in STRUCT_FORMAT or byte:
        if little_endian:
            return struct.pack(f"<{len(data)}B", *data)
        return struct.pack(f">{len(data)}B", *data)

    if unsigned:
        if little_endian:
            return struct.pack("<" + STRUCT_FORMAT[size], data)
        return struct.pack(">" + STRUCT_FORMAT[size], data)
    else:
        if little_endian:
            return struct.pack("<" + STRUCT_FORMAT_SIGNED[size], data)
        return struct.pack(">" + STRUCT_FORMAT_SIGNED[size], data)


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


def convert_long_to_list(long, little_endian=True):
    converted = [long & 0xFF, long >> 8 & 0xFF, long >> 16 & 0xFF, long >> 24 & 0xFF, long >> 32 & 0xFF, long >> 40 & 0xFF, long >> 48 & 0xFF, long >> 56 & 0xFF]
    if not little_endian:
        return list(reversed(converted))

    return converted


def convert_long_to_str(long):
    out = ""
    for x in convert_long_to_list(long):
        if x == 0:
            break
        out += chr(x)

    return out


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


def format_array(_list):
    out = ""
    for element in _list:
        out += hex(element) + " "
    return out


def bytes_to_int_array(byte_data, int_size=1):
    if len(byte_data) % int_size != 0:
        raise ValueError("Byte data length must be a multiple of int_size.")

    format_string = f"<{len(byte_data) // int_size}{int_size}B"
    return struct.unpack(format_string, byte_data)


def formatter(string, value, table=None, hex=False, mask=False, pad=0):
    if value == b'':
        return ""
    if string == "":
        return f"{value}\n"

    string = " "*pad + string

    if table != None:
        _value = value
        out = ""
        if mask:
            for flag in table:
                if (_value & flag) == flag:
                    out += table[_value & flag] + " "
                    _value = (_value & ~flag)
                if _value == 0:
                    break
        else:
            if _value in table:
                out = table[_value]
                _value = 0

        if out == "" or _value != 0:
            return f"{string:40} {value:x}\n"
        return f"{string:40} {out}\n"
    elif hex:
        if type(value) == list:
            return f"{string:40} {format_array(value)}\n"
        return f"{string:40} {value:x}\n"
    else:
        return f"{string:40} {value}\n"


def formatter2(format, value, table=None, mask=False):
    if value == b'':
        return value

    _value = value
    if table != None:
        out = ""
        if mask:
            for flag in table:
                if (_value & flag) == flag:
                    out += table[_value & flag] + " "
                    _value = (_value & ~flag)

                if _value == 0:
                    break

            if _value != 0:
                out += hex(_value)

            if out == "":
                out += hex(_value)
            _value = out
        else:
            if _value in table:
                _value = table[_value]

    return format % _value


def update(source, destination, offset):
    for idx in range(len(source)):
        if (offset + idx) >= len(destination):
            destination.extend(source[idx:])
        else:
            destination[offset + idx] = source[idx]
