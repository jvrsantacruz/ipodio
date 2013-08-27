# -*- coding: utf-8 -*-

from ipodio.cli import Options

from expects import expect
from mamba import describe, context, before


with describe(Options) as _:

    with context('when created'):
        def it_should_have_a_docopt_parsing_result_as_input():
            Options(_.parsed_input)

        def it_should_have_an_options_property():
            expect(_.options).to.have.property('options')

        def it_should_have_all_options_in_the_options_property():
            expect(_.options.options).to.equal(_.all_options)

        def it_should_have_an_arguments_property():
            expect(_.options).to.have.property('arguments')

        def it_should_have_all_arguments_in_the_arguments_property():
            expect(_.options.arguments).to.equal(_.all_arguments)

        def it_should_have_an_data_property():
            expect(_.options).to.have.property('data')

        def it_should_have_all_options_and_arguments_together_in_data():
            expect(_.options.data).to.equal(_.all_data)

        def it_should_have_a_commands_property():
            expect(_.options).to.have.property('commands')

        def it_should_have_all_commands_in_the_commands_property():
            expect(_.options.commands).to.equal(_.all_commands)

        def it_should_have_a_active_commands_property():
            expect(_.options).to.have.property('active_commands')

        def it_should_have_the_commands_marked_as_present():
            expect(_.options.active_commands).to.have(*_.active_commands)

        def it_should_have_a_active_command_property():
            expect(_.options).to.have.property('active_command')

        def it_should_have_a_single_active_command_property():
            expect(_.options.active_command).to.be(_.options.active_commands[0])

    with context('when created empty'):
        def it_should_have_empty_options():
            expect(_.empty_options.options).to.be.empty

        def it_should_have_empty_arguments():
            expect(_.empty_options.arguments).to.be.empty

        def it_should_have_empty_user_data():
            expect(_.empty_options.data).to.be.empty

        def it_should_have_empty_commands():
            expect(_.empty_options.commands).to.be.empty

        def it_should_have_empty_active_commands():
            expect(_.empty_options.active_commands).to.be.empty

        def it_should_have_active_command_to_none():
            expect(_.empty_options.active_command).to.be.none

    @before.all
    def fixture():
        _.parsed_input = {
            '-o': 'a short option',
            '--option': 'a long option',
            '<argument>': 'an argument',
            '<re-argument>': 'a repeated argument',
            'command': True,
            'subcommand': True,
            'subsubcommand': False
        }

        _.all_options = {
            'o': 'a short option',
            'option': 'a long option'
        }

        _.all_arguments = {
            'argument': 'an argument',
            're-argument': 'a repeated argument'
        }

        _.all_data = {
            'o': 'a short option',
            'option': 'a long option',
            'argument': 'an argument',
            're-argument': 'a repeated argument'
        }

        _.all_commands = {
            'command': True,
            'subcommand': True,
            'subsubcommand': False
        }

        _.active_commands = ['command', 'subcommand']

        _.options = Options(_.parsed_input)

        _.empty_options = Options({})
