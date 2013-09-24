# -*- coding: utf-8 -*-
"""
iPodio

Usage:
  ipodio list   [options] [<expression>...]
  ipodio push   [options] [--force] [--recursive] <filename>...
  ipodio pull   [options] [--dest=<directory>] [--force] [--plain] [<expression>...]
  ipodio rm     [options] <expression>...
  ipodio rename [options] <expression> <replacement>
  ipodio duplicates [options] [<expression>...]
  ipodio playlist list [options] [--force] [<name>] [<expression>...]
  ipodio playlist create [options] <name>
  ipodio playlist add [options] <name> <expression>...
  ipodio playlist rm [options] <name> [<expression>...]
  ipodio playlist rename [options] <name> <new_name>

Options:
  -m PATH, --mount PATH  Path to the iPod's mountpoint.
  -y , --yes  Do not prompt the user with questions.
"""

import os

from docopt import docopt

from . import handlers
from . import __version__


class Options(object):
    def __init__(self, options, defaults=None):
        self.defaults = defaults if defaults else {}
        self.options = self._parse_options(options)
        self.arguments = self._parse_arguments(options)
        self.commands = self._parse_commands(options)
        self.active_commands = self._parse_active_commands(self.commands)
        self.active_command = self._parse_active_command(self.active_commands)
        data = dict(self.options.items() + self.arguments.items())
        self.data = self._parse_default_values(data, self.defaults)

    def _parse_default_values(self, options, defaults):
        options.update({key: value for key, value in defaults.items()
                        if options.get(key) is None})
        return options

    def _parse_options(self, options):
        return {k.replace('-', ''): v
                for k, v in options.items() if k.startswith('-')}

    def _parse_arguments(self, options):
        return {k.replace('<', '').replace('>', ''): v
                for k, v in options.items() if k.startswith('<')}

    def _parse_commands(self, options):
        return {k: v for k, v in options.items() if k[0] not in ('-', '<')}

    def _parse_active_commands(self, commands):
        return [k for k, v in commands.items() if v]

    def _parse_active_command(self, active_commands):
        return active_commands[0] if active_commands else None


class Router(object):
    def __init__(self, *commands):
        self.commands = {c.key: c for c in commands}

    def get_command(self, key):
        return self.commands[frozenset(key)]


class Command(object):
    def __init__(self, key, handler):
        self.key = frozenset(key)
        self.handler = handler

    @property
    def handler_args(self):
        function = self.handler
        return function.func_code.co_varnames[:function.func_code.co_argcount]

    def call(self, **kwargs):
        expected_args = {name: kwargs.get(name) for name in self.handler_args}

        return self.handler(**expected_args)


def main():
    defaults = {'mount': os.environ.get('IPODIO_MOUNTPOINT')}
    parsed_input = docopt(__doc__, version=__version__)
    options = Options(parsed_input, defaults)

    router = Router(
        Command(['rm'], handlers.rm),
        Command(['list'], handlers.list),
        Command(['push'], handlers.push),
        Command(['pull'], handlers.pull),
        Command(['rename'], handlers.rename),
        Command(['duplicates'], handlers.duplicates),
        Command(['playlist', 'list'], handlers.playlist),
        Command(['playlist', 'add'], handlers.playlist_add),
        Command(['playlist', 'rm'], handlers.playlist_rm),
        Command(['playlist', 'rename'], handlers.playlist_rename),
        Command(['playlist', 'create'], handlers.playlist_create)
    )

    command = router.get_command(options.active_commands)
    command.call(**options.data)

if __name__ == '__main__':
    main()
