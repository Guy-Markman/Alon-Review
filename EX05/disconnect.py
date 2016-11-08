#!/usr/bin/env python
# Disconnect class
class Disconnect(RuntimeError):
    def __init__(self):
        super(Disconnect, self).__init__("Disconnect")