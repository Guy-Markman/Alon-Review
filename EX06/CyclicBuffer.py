#!/usr/bin/env python
import base
import constants
import util


class CyclicBuffer(base.Base):

    def __init__(self, mm):
        super(CyclicBuffer, self).__init__()
        self.logger.debug("Created cyclic Buffer")
        self.mm = mm

    def max_size_buffer(self):
        return constants.BUFFER_SIZE - 2 * constants.OFFSET_SIZE

    def get_head_offset(self):
        head_offset = util.data_to_int(
            self.mm[-2 * constants.OFFSET_SIZE:-1 * constants.OFFSET_SIZE])
        self.logger.debug("head offset %s" % head_offset)
        return head_offset

    def set_head_offset(self, value):
        self.logger.debug("Set head offset to %d" % value)
        self.mm[-2 * constants.OFFSET_SIZE:-1 *
                constants.OFFSET_SIZE] = util.int_to_data(value)

    def get_tail_offset(self):
        tail_offset = util.data_to_int(
            self.mm[-1 * constants.OFFSET_SIZE:])
        self.logger.debug("Tail offset %d" % tail_offset)
        return tail_offset

    def set_tail_offset(self, value):
        self.logger.debug("Set tail offset to %d" % value)
        self.mm[-1 * constants.OFFSET_SIZE:] = util.int_to_data(value)

    def read_head(self):
        head_offset = self.get_head_offset()
        ans = self.mm[head_offset]
        return ans

    def read_tail(self):
        tail_offset = self.get_tail_offset()
        ans = self.mm[tail_offset]
        return ans

    def write_head(self, value):
        head_offset = self.get_head_offset()
        self.logger.debug("Wrote %s into %s" % (value, head_offset))
        self.mm[head_offset] = value

    def write_tail(self, value):
        tail_offset = self.get_tail_offset()
        self.logger.debug("Wrote %s into %d" % (value, tail_offset))
        self.mm[tail_offset] = value

    def increas_head(self):
        head_offset = self.get_head_offset()
        if head_offset + 1 <= self.max_size_buffer():
            self.set_head_offset(head_offset + 1)
            self.logger.debug("Increased head offset to %s" %
                              (head_offset + 1))
        else:
            self.logger.debug("Reset head offset")
            self.set_head_offset(0)

    def increas_tail(self):
        tail_offset = self.get_tail_offset()
        ans = self.mm[tail_offset]
        if tail_offset + 1 <= self.max_size_buffer():
            self.set_tail_offset(tail_offset + 1)
            self.logger.debug("Increased tail offset to" % (tail_offset + 1))
        else:
            self.logger.debug("Reset tail offset, returned %s" % ans)
            self.set_tail_offset(0)
