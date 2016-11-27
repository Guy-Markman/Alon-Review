#!/usr/bin/env python
import os
import struct

FORMATS = ("I", "B")

def int_to_bin(integer):
    return struct.pack(FORMATS[1], integer)

def bin_to_int(binary):
    return struct.unpack(FORMATS[1], binary)[0]

def data_to_int(data):
    return struct.unpack(FORMATS[0], data)[0]


def int_to_data(integer):
    return struct.pack(FORMATS[0], integer)


def write_to_target(target, text):
    while text:
        text = text[os.write(target, text):]
