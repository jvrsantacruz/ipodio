# -*- coding: utf-8 -*-

import os
import shutil
from contextlib import contextmanager

import gpod

from expects import expect
from scripttest import TestFileEnvironment
from mamba import describe, context, before, after


with describe('ipodio') as _:

    with context('the list command'):
        def it_should_return_an_error_with_bad_expressions():
            execution = _.env.run(*_.cmd + ['list', _.bad_expression], expect_error=True)

            expect(execution.stdout).to.have("Error: Invalid expression")

        with context('when iPod is empty'):
            def it_should_print_nothing():
                execution = _.env.run(*_.cmd + ['list'])

                expect(execution.stdout).to.be.empty

        with context('when iPod has songs'):
            def it_should_print_a_header():
                execution = _.env.run(*_.cmd + ['list'])

                expect(execution.stdout).to.have('Title', 'Album', 'Artist')

            def it_should_print_a_line_per_song():
                execution = _.env.run(*_.cmd + ['list'])

                length_of_footer = 2
                length_of_header = 1
                number_of_songs = len(_.songs)
                stdout_lines = execution.stdout.split('\n')

                expect(stdout_lines).to.have.length(
                    length_of_header + number_of_songs + length_of_footer)

            @before.each
            def setup_list():
                _populate_ipod(_.mountpoint_path, _.songs)

    with context('the push command'):
        def it_should_return_an_error_with_no_files():
            execution = _.env.run(*_.cmd + ['push'], expect_error=True)

            expect(execution.stderr).to.have('Usage')

        def it_should_log_files_sent_to_the_ipod():
            execution = _.env.run(*_.cmd + ['push'] + _.song_paths)

            expect(execution.stdout.count('Sending')).to.be(len(_.songs))

        def it_should_refuse_to_duplicate_a_song():
            _.env.run(*_.cmd + ['push'] + _.song_paths)
            execution = _.env.run(*_.cmd + ['push'] + _.song_paths)

            expect(execution.stdout.count('Not sending')).to.be(len(_.songs))

        def it_should_send_duplicated_songs_anyway_if_forced():
            _populate_ipod(_.mountpoint_path, _.songs)

            execution = _.env.run(*_.cmd + ['--force', 'push'] + _.song_paths)

            expect(execution.stdout.count('Sending')).to.be(len(_.songs))

    with context('when executing rename'):
        def it_should_show_an_error_when_called_without_arguments():
            execution = _.env.run(*_.cmd + ['rename'], expect_error=True)

            expect(execution.stderr).to.have('Usage')

        def it_should_show_an_error_when_called_with_expression_but_without_replacement():
            execution = _.env.run(*_.cmd + ['rename', _.expression], expect_error=True)

            expect(execution.stderr).to.have('Usage')

    @before.each
    def setup():
        _bootstrap_ipod(_.mountpoint_path)

    @after.each
    def cleanup():
        try:
            shutil.rmtree(_.mountpoint_path)
        except:
            pass

    @before.all
    def fixture():
        _.bad_expression = '?'
        _.expression = 'john lennon'

        _.env_path = 'testing-sandbox'
        _.env = TestFileEnvironment(_.env_path)

        _.songs = ['fixtures/song1.mp3', 'fixtures/song2.mp3']
        _.song_paths = [os.path.join('..', song) for song in _.songs]

        _.mountpoint = 'ipod'
        _.mountpoint_path = os.path.join(_.env_path, _.mountpoint)
        _.cmd = ['ipodio', '--mount', _.mountpoint]

    @contextmanager
    def _database(mountpoint):
        db = gpod.Database(mountpoint)
        yield db
        db.close()

    def _bootstrap_ipod(mountpoint):
        gpod.itdb_init_ipod(mountpoint, None, 'my iPod', None)

    def _populate_ipod(mountpoint, files):
        with _database(mountpoint) as db:
            for path in files:
                db.new_Track(filename=path)
            db.copy_delayed_files()

    def _empty_ipod(mountpoint):
        with _database(mountpoint) as db:
            [db.remove(track, quiet=True) for track in db]
