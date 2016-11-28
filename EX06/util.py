#!/usr/bin/env python
import os
import struct


def int_to_bin(integer):
    return struct.pack("B", integer)


def bin_to_int(binary):
    return struct.unpack("B", binary)[0]


def data_to_int(data):
    return struct.unpack("I", data)[0]


def int_to_data(integer):
    return struct.pack("I", integer)


def write_to_target(target, text):
    while text:
        text = text[os.write(target, text):]
