# -*- coding: utf-8 -*-

import re
import os
import glob
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

            def it_should_print_a_line_per_song_when_filtering_using_expression():
                execution = _.env.run(*_.cmd + ['list'] + _.expression.split())

                length_of_footer = 2
                length_of_header = 1
                number_of_songs = 1
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

        def it_should_find_files_within_a_given_directory():
            execution = _.env.run(*_.cmd + ['push', _.fixtures_path])

            expect(execution.stdout.count('Sending')).to.be(len(_.songs))

        def it_should_find_files_within_a_directory_tree_if_recursive():
            execution = _.env.run(*_.cmd + ['push', '--recursive', _.fixtures_path])

            expect(execution.stdout.count('ending')).to.be(2 * len(_.songs))

        def it_should_copy_song_files_into_the_ipod():
            execution = _.env.run(*_.cmd + ['--force', 'push'] + _.song_paths)

            number_of_added_songs = sum(1 for path in execution.files_created
                if 'iPod_Control/Music' in path and path.endswith('mp3'))

            expect(number_of_added_songs).to.be(2)

        def it_should_refuse_to_duplicate_a_song():
            _populate_ipod(_.mountpoint_path, _.songs)

            execution = _.env.run(*_.cmd + ['push'] + _.song_paths)

            expect(execution.stdout.count('Not sending')).to.be(len(_.songs))

        def it_should_send_duplicated_songs_anyway_if_forced():
            _populate_ipod(_.mountpoint_path, _.songs)

            execution = _.env.run(*_.cmd + ['--force', 'push'] + _.song_paths)

            expect(execution.stdout.count('Sending')).to.be(len(_.songs))

    with context('when executing rename'):
        def it_should_return_an_error_when_rename_with_bad_expressions():
            execution = _.env.run(
                *_.cmd + ['rm', _.bad_expression, _.bad_expression], expect_error=True)

            expect(execution.stdout).to.have("Error: Invalid expression")

        def it_should_show_an_error_when_called_without_arguments():
            execution = _.env.run(*_.cmd + ['rename'], expect_error=True)

            expect(execution.stderr).to.have('Usage')

        def it_should_show_an_error_when_called_with_expression_but_without_replacement():
            execution = _.env.run(*_.cmd + ['rename', _.expression], expect_error=True)

            expect(execution.stderr).to.have('Usage')

    with context('when executing rm'):
        def it_should_return_an_error_when_called_without_arguments():
            execution = _.env.run(*_.cmd + ['rm'], expect_error=True)

            expect(execution.stderr).to.have("Usage:")

        def it_should_return_an_error_when_rm_with_bad_expressions():
            execution = _.env.run(*_.cmd + ['rm', _.bad_expression], expect_error=True)

            expect(execution.stdout).to.have("Error: Invalid expression")

        def it_should_print_message_when_removing_no_songs():
            execution = _.env.run(*_.cmd + ['rm', 'foobarbaztaz'])

            expect(execution.stdout).to.have("No tracks removed.")

        def it_should_list_all_songs_that_were_removed():
            _populate_ipod(_.mountpoint_path, _.songs)

            execution = _.env.run(*_.cmd + ['-y', 'rm', '.'])

            expect(execution.stdout.count('\n')).to.be(2 + len(_.songs))

    with context('the pull command'):
        def it_should_copy_selected_songs_to_the_current_directory():
            execution = _.env.run(*_.cmd + ['pull'])

            copied_songs = [path for path in execution.files_created if path.endswith('.mp3')]

            expect(copied_songs).to.have.length(2)

        def it_should_name_copied_songs_using_number_title_album_artist():
            execution = _.env.run(*_.cmd + ['pull'])

            pattern = re.compile('^(\d+)?_([\s\w]+)?_([\s\w]+)?_([\s\w]+)?.mp3$')
            copied_songs = [path for path in execution.files_created if pattern.match(os.path.basename(path))]

            expect(copied_songs).to.have.length(2)

        def it_should_create_a_hierarchy_of_directories_using_artist_and_album():
            execution = _.env.run(*_.cmd + ['pull'])

            created_directories = [path for path in execution.files_created if not path.endswith('.mp3')]

            expect(created_directories).to.have(
                'Jono Bacon',
                'Jono Bacon/Released as a single',
                'Richard Stallman',
            )

        def it_should_avoid_overwriting_song_files():
            _.env.run(*_.cmd + ['pull'])
            execution = _.env.run(*_.cmd + ['pull'])

            expect(execution.files_created).to.be.empty

        with context('with --force option'):
            def it_should_not_mind_overwriting_song_files():
                _.env.run(*_.cmd + ['pull'])
                execution = _.env.run(*_.cmd + ['--force', 'pull'])

                expect(execution.files_updated).to.have.length(2)

        with context('with --dest <destination> option'):
            def it_should_copy_the_songs_to_the_destination_directory():
                execution = _.env.run(*_.cmd + ['--dest', 'pulled', 'pull'])

                copied_songs = [path for path in execution.files_created if 'pulled' in path and path.endswith('.mp3')]

                expect(copied_songs).to.have.length(2)

        with context('with --plain option'):
            def it_should_copy_all_files_without_hierarchy():
                execution = _.env.run(*_.cmd + ['--plain', 'pull'])

                expect(execution.files_created).to.have.length(2)

        @before.each
        def setup_pull():
            _bootstrap_ipod(_.mountpoint_path)
            _populate_ipod(_.mountpoint_path, _.songs)

        @after.each
        def cleanup_pull():
            def remove(path):
                remover = shutil.rmtree if os.path.isdir(path) else os.remove
                try:
                    remover(path)
                except:
                    pass

            [remove(path) for path in glob.glob(os.path.join(_.env_path, '*'))]

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
        _.expression = 'richard stall'

        _.env_path = 'testing-sandbox'
        _.env = TestFileEnvironment(_.env_path)

        _.fixtures = 'fixtures'
        _.fixtures_path = '../fixtures'

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