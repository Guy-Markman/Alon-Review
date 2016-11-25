#!/usr/bin/env python
import os
import struct

FORMAT = ("I", 16)


def data_to_int(data):
    return struct.unpack(FORMAT[0], data)[0]


def int_to_data(integer):
    return struct.pack(FORMAT[0], integer)


def write_to_target(target, text):
    while text:
        text = text[os.write(target, text):]
