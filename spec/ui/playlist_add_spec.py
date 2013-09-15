# -*- coding: utf-8 -*-

from expects import expect
from mamba import describe, context, before, after

from spec.ui._ipod_helpers import *
from spec.ui._fixture import update_environment


with describe('ipodio playlist add') as _:
    @before.all
    def setup_all():
        _.playlist_name = 'playlist'
        update_environment(_)
        bootstrap_ipod(_.mountpoint_path)
        populate_ipod(_.mountpoint_path, _.songs)

    with context('without a name'):
        def should_print_an_error():
            execution = _.env.run(*_.cmd + ['playlist', 'add'], expect_error=True)

            expect(execution.stderr).to.have('Usage:')

    with context('given a name which is not an existing playlist'):
        def should_print_an_error_():
            execution = _.env.run(*_.cmd + ['playlist', 'add', 'foo', _.expression])

            expect(execution.stdout).to.have('The playlist "foo" does not exist')

    with context('given a name'):
        with context('but not an expression'):
            def should_print_an_error__():
                execution = _.env.run(*_.cmd + ['playlist', 'add', _.playlist_name], expect_error=True)

                expect(execution.stderr).to.have('Usage:')

        with context('but with a bad expression'):
            def should_print_an_error___():
                execution = _.env.run(*_.cmd + ['playlist', 'add', _.playlist_name, _.bad_expression], expect_error=True)

                expect(execution.stdout).to.have("Error: Invalid expression")

        with context('and an expression wich does not match anything'):
            def should_print_a_warning_message():
                execution = _.env.run(*_.cmd + ['playlist', 'add', _.playlist_name, '777777'])

                expect(execution.stdout).to.have("No tracks to add")

        with context('and an expression'):
            def should_print_all_songs_to_be_added():
                execution = _.env.run(*_.cmd + ['playlist', 'add', _.playlist_name, _.expression, '--yes'])

                length_of_footer = 2
                length_of_header = 2
                number_of_songs = 1
                stdout_lines = execution.stdout.split('\n')

                expect(stdout_lines).to.have.length(
                    length_of_header + number_of_songs + length_of_footer)

        @before.each
        def setup_playlists():
            create_playlist(_.mountpoint_path, _.playlist_name)

        @after.each
        def cleanup_with_playlists():
            remove_ipod_playlist(_.mountpoint_path, _.playlist_name)
