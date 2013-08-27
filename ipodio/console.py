# -*- coding: utf-8 -*-

import os
import sys
import fcntl
import struct
import termios


class Console(object):
    _width = None

    def _get_console_size(self):
        return (self._get_window_size(sys.stdin)
                or self._get_window_size(sys.stdout)
                or self._get_window_size(sys.stderr)
                or self._get_term_window_size()
                or (25, 80))

    def _get_term_window_size(self):
        try:
            with os.open(os.ctermid(), os.O_RDONLY) as term:
                return self._get_window_size(term)
        except:
            return None

    def _get_window_size(self, fd):
        try:
            data = fcntl.ioctl(fd, termios.TIOCGWINSZ, '0' * 8)
            height, width, hp, wp = struct.unpack('HHHH', data)
            return height, width
        except:
            return None

    @property
    def width(self):
        if self._width is None:
            _, self._width = self._get_console_size()
        return self._width

    def relative_width(self, percentage):
        """Return the width of a part of the screen in number of characters"""
        return int((self.width - 4) * percentage)
