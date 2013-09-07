# -*- coding: utf-8 -*-

import types


from expects import expect
from mamba import describe, context, before


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


with describe(Command) as _:
    with context('the key property'):
        def should_be_a_frozenset():
            expect(_.command.key).to.be.a(frozenset)

        def should_contain_the_given_key_words():
            expect(_.command.key).to.have(*_.key)

    with context('the handler property'):
        def should_be_a_function():
            expect(_.command.handler).to.be.a(types.FunctionType)

        def should_be_the_given_handler():
            expect(_.command.handler).to.be(_.handler)

    with context('the handler_args property'):
        def should_be_the_list_of_argument_names():
            expect(_.command.handler_args).to.have(*_.handler_args)
            expect(_.command.handler_args).to.have.length(len(_.handler_args))

    with context('the call method'):
        def should_call_the_handler_the_given_arguments():
            call_result = _.command.call(**_.handler_kwargs)

            expect(call_result).to.be.equal(_.called)

        def should_call_only_with_arguments_that_the_handler_understands():
            call_args = {'evil_extra': None}
            call_args.update(_.handler_kwargs)

            call_result = _.command.call(**call_args)

            expect(call_result).to.be.equal(_.called)

    def _handler(first, second, third):
        varname1, varname2, varname3 = None, None, None
        return [first, second, third]

    @before.all
    def fixture():
        _.key = ['command', 'subcommand']
        _.handler = _handler
        _.handler_args = ['first', 'second', 'third']
        _.handler_kwargs = {name: name for name in _.handler_args}
        _.called = _.handler_args
        _.command = Command(_.key, _.handler)
