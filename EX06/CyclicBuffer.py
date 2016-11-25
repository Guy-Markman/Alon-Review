#!/usr/bin/env python
import base
import constants
import util


class CyclicBuffer(base.Base):

    def __init__(self, mm, start=0, size=constants.BUFFER_SIZE):
        super(CyclicBuffer, self).__init__()
        self.logger.debug("Created cyclic Buffer")
        self._mm = mm
        self.start = start
        self.size = size

        # [Start , End]
        self._head_offset = {"start": start + size - 2 * constants.OFFSET_SIZE,
                             "end": start + size - constants.OFFSET_SIZE}
        self._tail_offset = {"start": start + size - constants.OFFSET_SIZE,
                             "end": start + size}

    def min_allocate(self):
        return self.size - 2 * constants.OFFSET_SIZE

    @property
    def head(self):
        return util.data_to_int(self._mm[self._head_offset["start"]:
                                         self._head_offset["end"]])

    @head.setter
    def head(self, value):
        self.logger.debug("Set head offset to %d" % value)
        self._mm[self._head_offset["start"]:self._head_offset[
            "end"]] = util.int_to_data(value)

    @property
    def tail(self):
        return util.data_to_int(self._mm[self._tail_offset["start"]:
                                         self._tail_offset["end"]])

    @tail.setter
    def tail(self, value):
        self.logger.debug("Set tail offset to %d" % value)
        self._mm[self._tail_offset["start"]:self._tail_offset["end"]] = \
            util.int_to_data(value)

    def read_head(self):
        return self._mm[self.head]

    def read_tail(self):
        return self._mm[self.tail]

    def write_head(self, value):
        self.logger.debug("Wrote %s into %s" % (value, self.head))
        self._mm[self.head] = value

    def write_tail(self, value):
        self.logger.debug("Wrote %s into %d" % (value, self.tail))
        self._mm[self._tail] = value

    def increas_head(self):
        plus_one = self.head + 1
        self.head = plus_one if plus_one < self.min_allocate() else self.start

    def increas_tail(self):
        plus_one = self.tail + 1
        self.tail = plus_one if plus_one < self.min_allocate() else self.start
