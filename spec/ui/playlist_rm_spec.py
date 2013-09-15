# -*- coding: utf-8 -*-

from expects import expect
from mamba import describe, context, before

from spec.ui._ipod_helpers import *
from spec.ui._fixture import update_environment


with describe('ipodio playlist rm') as _:

    @before.all
    def setup_all():
        _.playlist_name = 'playlist'
        update_environment(_)
        bootstrap_ipod(_.mountpoint_path)
        populate_ipod(_.mountpoint_path, _.songs)

    def should_print_an_error_message():
        execution = _.env.run(*_.cmd + ['playlist', 'rm'], expect_error=True)

        expect(execution.stderr).to.have('Usage:')

    with context('given the master playlist name'):
        def should_print_an_error__():
            execution = _.env.run(*_.cmd + ['playlist', 'rm', 'my iPod'])

            expect(execution.stdout).to.have('Cannot remove master playlist')

    with context('given an unknown playlist name'):
        def should_print_an_error_():
            execution = _.env.run(*_.cmd + ['playlist', 'rm', 'foo', _.expression, '--yes'])

            expect(execution.stdout).to.have('does not exist')
    with context('given a playlist name'):
        def should_delete_the_playlist():
            execution = _.env.run(*_.cmd + ['playlist', 'rm', _.playlist_name, '--yes'])

            expect(execution.stdout).to.have('')

        with context('and a expression'):
            def should_print_the_tracks_to_be_removed():
                length_of_footer = 2
                length_of_header = 2
                number_of_songs = 1
                stdout_lines = _.execution.stdout.split('\n')

                expect(stdout_lines).to.have.length(
                    length_of_header + number_of_songs + length_of_footer)

            def should_remove_those_tracks_from_playlist():
                with database(_.mountpoint_path) as db:
                    playlist = find_playlist(db, _.playlist_name)

                    expect(playlist).to.have.length(1)

            @before.all
            def execution():
                populate_ipod_playlist(_.mountpoint_path, _.playlist_name, 2)
                _.execution = _.env.run(*_.cmd + ['playlist', 'rm', _.playlist_name, _.expression, '--yes'])

        with context('and a non matching expression'):
            def should_print_nothing():
                populate_ipod_playlist(_.mountpoint_path, _.playlist_name, 2)

                execution = _.env.run(*_.cmd + ['playlist', 'rm', _.playlist_name, '80090909', '--yes'])

                expect(execution.stdout).to.be.empty

        with context('and a bad expression'):
            def should_print_an_error():
                execution = _.env.run(*_.cmd + ['playlist', 'rm', _.playlist_name, _.bad_expression], expect_error=True)

                expect(execution.stdout).to.have("Error: Invalid expression")
