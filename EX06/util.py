#!/usr/bin/env python
import os
import struct

import constants

FORMAT = ("B", 16)


def data_to_int(data):
    integer = 0
    if len(data) == 0:
        raise ValueError
    for x in data:
        integer = integer * FORMAT[1]**2 + struct.unpack(FORMAT[0], x)[0]
    return integer


def int_to_data(integer):
    data = ""
    integer = "%0*x" % (2 * constants.OFFSET_SIZE, integer)
    while integer:
        data += struct.pack(FORMAT[0], int(integer[:2], FORMAT[1]))
        integer = integer[2:]
    return data


def length_integer(integer):
    return len(str(integer))


def write_to_target(target, text):
    while text:
        text = text[os.write(target, text):]
