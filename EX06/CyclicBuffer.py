#!/usr/bin/env python
import base
import constants
import util


class CyclicBuffer(base.Base):

    def __init__(self, mm):
        super(CyclicBuffer, self).__init__()
        self.logger.debug("Created cyclic Buffer")
        self.mm = mm
        self._head = 0
        self._tail = 0

    def min_allocate(self):
        return constants.BUFFER_SIZE - 2 * constants.OFFSET_SIZE

    @property
    def head(self):
        return self._head

    @head.getter
    def head(self):
        self.logger.debug("head offset %s" % self._head)
        return self._head

    @head.setter
    def head(self, value):
        self.logger.debug("Set head offset to %d" % value)
        encrepted_data = util.int_to_data(value)
        self.mm[constants.BUFFER_SIZE - 2 * constants.OFFSET_SIZE:
                constants.BUFFER_SIZE - constants.OFFSET_SIZE] = encrepted_data
        self._head = encrepted_data

    @property
    def tail(self):
        return self._tail

    @tail.getter
    def tail(self):
        self.logger.debug("tail offset %s" % self._tail)
        return self._tail

    @tail.setter
    def tail(self, value):
        self.logger.debug("Set tail offset to %d" % value)
        encrepted_data = util.int_to_data(value)
        self.mm[constants.BUFFER_SIZE -
                constants.OFFSET_SIZE: constants.OFFSET_SIZE] = encrepted_data
        self._tail = encrepted_data

    def read_head(self):
        return self.mm[self._head]

    def read_tail(self):
        return self.mm[self._tail]

    def write_head(self, value):
        self.logger.debug("Wrote %s into %s" % (value, self.head))
        self.mm[self._head] = value

    def write_tail(self, value):
        self.logger.debug("Wrote %s into %d" % (value, self.tail))
        self.mm[self._tail] = value

    def increas_head(self):
        self._head = self._head + 1 if self._head + 1 < self.min_allocate() else 0

    def increas_tail(self):
        self._tail = self._tail + 1 if self._tail + 1 < self.min_allocate() else 0
