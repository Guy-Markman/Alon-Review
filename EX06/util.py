#!/usr/bin/env python
import os
import struct


def bytes_to_int(bytes):
    ans = 0
    for x in xrange(bytes):
        ans += struct.unpack("B", x)[0]
    return ans


def str_to_bytes(str):
    ans =


def write_to_target(target, text):
    while text:
        text = text[os.write(target, text):]
