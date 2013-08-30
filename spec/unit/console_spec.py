## -*- coding: utf-8 -*-

import fcntl
import struct
import termios
from contextlib import contextmanager


from expects import expect
from mamba import describe, context, before


class IoctlMock(object):
    fail = False
    _data = (20, 70, 0, 0)  # h w x x

    def monkey_patch(self):
        fcntl.ioctl = self

    @property
    @contextmanager
    def failing(self):
        self.fail = True
        yield
        self.fail = False

    def __call__(self, fd, operation, data):
        expect(data).to.have.length(8)
        expect(operation).to.be(termios.TIOCGWINSZ)
        if self.fail:
            raise Exception('ioctl failure')
        return struct.pack('HHHH', *self._data)


ioctl = IoctlMock()
ioctl.monkey_patch()

from ipodio.cli import Console


with describe(Console) as _:
    with context('when created'):
        def it_should_have_a_width_property():
            expect(_.console()).to.have.property('width')

    with context('when accesing width'):
        def it_should_return_system_console_width():
            expect(_.console().width).to.be(_.width)

    with context('when calling relative_width'):
        def it_should_return_the_proportional_size():
            relative_width = _.console().relative_width(0.8)

            expect(relative_width).to.be(_.relative_width_80)

    with context('when ioctl fails'):
        def it_should_return_default_values():
            with ioctl.failing:
                expect(_.console().width).to.be(_.default)

    @before.all
    def fixture():
        _.console = lambda: Console()
        _.width = 70
        _.default = 80
        _.relative_width_80 = int((_.width - 4) * 0.8)
