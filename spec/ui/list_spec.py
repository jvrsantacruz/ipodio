# -*- coding: utf-8 -*-

import shutil

from expects import expect
from mamba import describe, context, before, after

from spec.ui._ipod_helpers import *
from spec.ui._fixture import update_environment


with describe('ipodio list') as _:

    @before.all
    def setup_all():
        update_environment(_)
        bootstrap_ipod(_.mountpoint_path)

    with context('given a bad expression'):
        def should_print_an_error():
            execution = _.env.run(*_.cmd + ['list', _.bad_expression], expect_error=True)

            expect(execution.stdout).to.have("Error: Invalid expression")

    with context('with an empty iPod'):
        def should_print_nothing():
            execution = _.env.run(*_.cmd + ['list'])

            expect(execution.stdout).to.be.empty

    with context('with songs in the iPod'):
        def should_print_a_header():
            expect(_.execution_stdout).to.have('Title', 'Album', 'Artist')

        def should_print_a_line_per_song():
            length_of_footer = 2
            length_of_header = 1
            number_of_songs = len(_.songs)
            stdout_lines = _.execution_stdout.split('\n')

            expect(stdout_lines).to.have.length(
                length_of_header + number_of_songs + length_of_footer)

        @before.all
        def execution():
            _.execution_stdout = str(_.env.run(*_.cmd + ['list']).stdout)

        with context('given a filtering expression'):
            def should_print_a_line_per_song_that_matches():
                execution = _.env.run(*_.cmd + ['list'] + _.expression.split())

                length_of_footer = 2
                length_of_header = 1
                number_of_songs = 1
                stdout_lines = execution.stdout.split('\n')

                expect(stdout_lines).to.have.length(
                    length_of_header + number_of_songs + length_of_footer)

        @before.all
        def setup():
            populate_ipod(_.mountpoint_path, _.songs)

        @after.all
        def cleanup():
            try:
                shutil.rmtree(_.mountpoint_path)
            except:
                pass
