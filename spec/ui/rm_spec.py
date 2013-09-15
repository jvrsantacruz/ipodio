# -*- coding: utf-8 -*-

from expects import expect
from mamba import describe, context, before

from spec.ui._ipod_helpers import *
from spec.ui._fixture import update_environment


with describe('ipodio rm') as _:

    @before.all
    def setup_all():
        update_environment(_)
        bootstrap_ipod(_.mountpoint_path)

    def should_return_an_error_when_called_without_arguments():
        execution = _.env.run(*_.cmd + ['rm'], expect_error=True)

        expect(execution.stderr).to.have("Usage:")

    def should_return_an_error_when_rm_with_bad_expressions():
        execution = _.env.run(*_.cmd + ['rm', _.bad_expression], expect_error=True)

        expect(execution.stdout).to.have("Error: Invalid expression")

    def should_print_message_when_removing_no_songs():
        execution = _.env.run(*_.cmd + ['rm', 'foobarbaztaz'])

        expect(execution.stdout).to.have("No tracks removed.")

    with context('with songs in the iPod'):
        def should_list_all_songs_that_were_removed():
            populate_ipod(_.mountpoint_path, _.songs)

            execution = _.env.run(*_.cmd + ['-y', 'rm', '.'])

            expect(execution.stdout.count('\n')).to.be(2 + len(_.songs))
