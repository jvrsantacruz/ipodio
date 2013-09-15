# -*- coding: utf-8 -*-

import shutil

from expects import expect
from mamba import describe, context, before, after

from spec.ui._ipod_helpers import *
from spec.ui._fixture import update_environment


with describe('ipodio playlist') as _:
    @before.all
    def setup_all():
        _.playlist_name = 'playlist'
        update_environment(_)
        bootstrap_ipod(_.mountpoint_path)

    with context('with an empty iPod'):
        def should_only_print_the_default_master_playlist():
            execution = _.env.run(*_.cmd + ['playlist', 'list'])

            expect(execution.stdout).to.be.equal('my iPod\n')

        with context('given the master playlist name'):
            def should_print_nothing():
                execution = _.env.run(*_.cmd + ['playlist', 'list', 'my iPod'])

                expect(execution.stdout).to.be.empty

        with context('given a non existing playlist name'):
            def should_print_a_non_existing_error():
                execution = _.env.run(*_.cmd + ['playlist', 'list', 'foo'])

                expect(execution.stdout).to.have('does not exist')

    with context('with songs in the iPod'):
        def should_only_print_the_default_master_playlist_():
            execution = _.env.run(*_.cmd + ['playlist', 'list'])

            expect(execution.stdout).to.be.equal('my iPod\n')

        with context('given the master playlist name'):
            def should_print_the_playlist_name_first():
                execution = _.env.run(*_.cmd + ['playlist', 'list', 'my iPod'])

                expect(execution.stdout).to.have('my iPod')

            def should_print_all_existing_songs():
                execution = _.env.run(*_.cmd + ['playlist', 'list', 'my iPod'])

                length_of_header = 2
                length_of_footer = 2
                number_of_songs = len(_.songs)
                stdout_lines = execution.stdout.split('\n')

                expect(stdout_lines).to.have.length(
                    length_of_header + number_of_songs + length_of_footer)

            with context('given a filtering expression'):
                def should_print_a_line_per_song_that_matches():
                    execution = _.env.run(*_.cmd + ['playlist', 'list', 'my iPod'] + _.expression.split())

                    length_of_header = 2
                    length_of_footer = 2
                    number_of_songs = 1
                    stdout_lines = execution.stdout.split('\n')

                    expect(stdout_lines).to.have.length(
                        length_of_header + number_of_songs + length_of_footer)

        with context('with playlists in the iPod'):
            def should_print_all_playlist_names_in_order():
                execution = _.env.run(*_.cmd + ['playlist', 'list'])

                expect(execution.stdout).to.be.equal('my iPod\n' + _.playlist_name + '\n')

            with context('given the playlist name'):
                def should_print_all_existing_songs_():
                    execution = _.env.run(*_.cmd + ['playlist', 'list', 'my iPod'])

                    length_of_header = 2
                    length_of_footer = 2
                    number_of_songs = len(_.songs)
                    stdout_lines = execution.stdout.split('\n')

                    expect(stdout_lines).to.have.length(
                        length_of_header + number_of_songs + length_of_footer)

            with context('given a filtering expression'):
                def should_print_a_line_per_song_that_matches_():
                    execution = _.env.run(*_.cmd + ['playlist', 'list', 'my iPod'] + _.expression.split())

                    length_of_header = 2
                    length_of_footer = 2
                    number_of_songs = 1
                    stdout_lines = execution.stdout.split('\n')

                    expect(stdout_lines).to.have.length(
                        length_of_header + number_of_songs + length_of_footer)

            @before.all
            def setup_with_playlists():
                create_playlist(_.mountpoint_path, _.playlist_name)

            @after.all
            def cleanup_with_playlists():
                remove_ipod_playlist(_.mountpoint_path, _.playlist_name)

        @before.all
        def setup_with_songs():
            populate_ipod(_.mountpoint_path, _.songs)

        @after.all
        def cleanup():
            try:
                shutil.rmtree(_.mountpoint_path)
            except:
                pass
