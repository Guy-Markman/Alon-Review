#!/usr/bin/env python
import base
import constants


class CyclicBuffer(base.Base):

    def __init__(self, mm,):
        super(CyclicBuffer, self).__init__()
        self.mm = mm

    def max_size_buffer(self):
        return constants.BUFFER_SIZE - 2 * constants.OFFSET_SIZE

    def get_head_offset(self):
        return self.mm[-2 * constants.OFFSET_SIZE:-1 * constants.OFFSET_SIZE]

    def set_head_offset(self, value):
        self.mm[-2 * constants.OFFSET_SIZE:-1 * constants.OFFSET_SIZE] = value

    def get_tail_offset(self):
        return self.mm[-1 * constants.OFFSET_SIZE:]

    def set_tail_offset(self, value):
        self.mm[-1 * constants.OFFSET_SIZE:] = value

    def read_head(self):
        head_offset = self.get_head_offset()
        ans = self.mm[head_offset]
        if head_offset + 1 <= self.max_size_buffer():
            self.set_head_offset(head_offset + 1)
        else:
            self.set_head_offset(0)
        return ans

    def read_tail(self):
        tail_offset = self.get_head_offset()
        ans = self.mm[tail_offset]
        if tail_offset + 1 <= self.max_size_buffer():
            self.set_tail_offset(tail_offset + 1)
        else:
            self.set_head_offset(0)
        return ans
