#!/usr/bin/env python
import os
import errno
import time


def write_to_target(target, text):
    while text:
        text = text[os.write(target, text):]


def read_from_target(target, size):
    data = None
    while data is not None:
        try:
            data = os.read(target, size)
        except IOError as e:
            if e.errno != errno.EINTR:
                raise


def sleep(sec):  # Less acurate if you use time.sleep without signals
    while sec > 0:
        start = time.time()
        time.sleep(sec)
        sec -= time.time() - start
