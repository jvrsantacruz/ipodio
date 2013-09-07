# -*- coding: utf-8 -*-

from expects import expect
from mamba import describe, context, before

from ipodio.cli import Router


class MockCommand(object):
    def __init__(self, key, handler):
        self.key = frozenset(key)
        self.hanlder = handler


with describe(Router) as _:
    with context('the commands property'):
        def should_be_a_dictionary_of_commands_by_key():
            expect(_.router.commands).to.be.equal(_.commands_by_key)

    with context('the get_command method'):
        def should_return_a_command_by_its_key_sequence():
            command = _.router.get_command(_.key_sequence)

            expect(command.key).to.have(*_.key_sequence)
            expect(command.key).to.have.length(len(_.key_sequence))

        def should_raise_KeyError_for_any_unknown_key():
            call = lambda: _.router.get_command(_.unknown_key)

            expect(call).to.raise_error(KeyError)

    @before.all
    def fixture():
        _.commands = [
            MockCommand(['key', 'subkey'], 'handler'),
            MockCommand(['fookey', 'foosubkey'], 'barhandler'),
        ]
        _.commands_by_key = {c.key: c for c in _.commands}
        _.key_sequence = ['key', 'subkey']
        _.unknown_key = _.key_sequence + ['bar']
        _.router = Router(*_.commands)
