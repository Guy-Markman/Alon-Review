#!/usr/bin/env python
import base
import util

BUFFER_SIZE = 16777224  # 16MB + Twice buffer size
OFFSET_SIZE = 4


class CyclicBuffer(base.Base):

    def __init__(self, mm, start=0, size=BUFFER_SIZE):
        super(CyclicBuffer, self).__init__()
        self.logger.debug(
            "Created cyclic Buffer. Starting in %d. Size %d",
            start,
            size)
        self._mm = mm
        self._start = start
        self.size = size

        # [Start , End]
        self._head_offset_start = start + size - 2 * OFFSET_SIZE
        self._head_offset_end = start + size - OFFSET_SIZE
        self._tail_offset_start = start + size - OFFSET_SIZE
        self._tail_offset_end = start + size
        self._min_allocate = self.size - 2 * OFFSET_SIZE

    @property
    def head(self):
        return util.data_to_int(self._mm[self._head_offset_start:
                                         self._head_offset_end])

    @head.setter
    def head(self, value):
        self.logger.debug("Set head offset to %d", value)
        self._mm[self._head_offset_start:self._head_offset_end] = \
            util.int_to_data(value)

    @property
    def tail(self):
        return util.data_to_int(self._mm[self._tail_offset_start:
                                         self._tail_offset_end])

    @tail.setter
    def tail(self, value):
        self.logger.debug("Set tail offset to %d", value)
        self._mm[self._tail_offset_start:self._tail_offset_end] = \
            util.int_to_data(value)

    def read_tail(self):
        while self.head == self.tail:
            pass
        tail = self.tail
        read_data = self._mm[tail]
        self.logger.debug("Read %s from %s", read_data, tail)
        self._increas_tail()
        return read_data

    def write_head(self, value):
        head = self.head
        n = (head + 1) % (self._min_allocate)
        while n == self.tail:
            pass
        self.logger.debug("Wrote %s into %s", value, head)
        self._mm[head] = value
        self._increas_head()

    def _increas_head(self):
        self.head = (self.head + 1) % (self._min_allocate)

    def _increas_tail(self):
        self.tail = (self.tail + 1) % (self._min_allocate)
