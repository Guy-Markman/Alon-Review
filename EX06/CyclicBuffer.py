#!/usr/bin/env python
import base
import constants
import util


class CyclicBuffer(base.Base):

    def __init__(self, mm, start=0, size=constants.BUFFER_SIZE):
        super(CyclicBuffer, self).__init__()
        self.logger.debug(
            "Created cyclic Buffer. Starting in %d. Size %d",
            start,
            size)
        self._mm = mm
        self.start = start
        self.size = size

        # [Start , End]
        self._head_offset_start = start + size - 2 * constants.OFFSET_SIZE
        self._head_offset_end = start + size - constants.OFFSET_SIZE
        self._tail_offset_start = start + size - constants.OFFSET_SIZE
        self._tail_offset_end = start + size
        self.min_allocate = self.size - 2 * constants.OFFSET_SIZE

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

    def read_head(self):
        while self.head == self.tail:
            pass
        head = self.head
        read_head = self._mm[self.head]
        self.logger.debug("Read %s from %s", read_head, head)
        return self._mm[self.head]

    def read_tail(self):
        while self.head == self.tail:
            pass
        tail = self.tail
        read_data = self._mm[tail]
        self.logger.debug("Read %s from %s", read_data, tail)
        return read_data

    def write_head(self, value):
        n = (self.head + 1) % (self.size + 1)
        while n == self.tail:
            pass
        head = self.head
        self.logger.debug("Wrote %s into %s", value, head)
        self._mm[head] = value

    def write_tail(self, value):
        n = (self.tail + 1) % (self.size + 1)
        while n == self.head:
            pass
        tail = self._tail
        self.logger.debug("Wrote %s into %d", value, tail)
        self._mm[tail] = value

    def increas_head(self):
        self.head = (self.head + 1) % (self.min_allocate)

    def increas_tail(self):
        self.tail = (self.tail + 1) % (self.min_allocate)
