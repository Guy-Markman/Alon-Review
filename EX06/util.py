#!/usr/bin/env python
import os


def write_to_target(target, text):
    while text:
        text = text[os.write(target, text):]
