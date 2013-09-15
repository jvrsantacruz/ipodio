# -*- coding: utf-8 -*-

import re
import os
import shutil

from expects import expect
from mamba import describe, context, before, after

from spec.ui._ipod_helpers import *
from spec.ui._fixture import update_environment


with describe('ipodio pull') as _:

    @before.all
    def setup_all():
        update_environment(_)
        bootstrap_ipod(_.mountpoint_path)
        populate_ipod(_.mountpoint_path, _.songs)
        _.execution = _.env.run(*_.cmd + ['pull'])

    @after.all
    def cleanup():
        shutil.rmtree(_.env_path)

    def should_copy_selected_songs_to_the_current_directory():
        copied_songs = [path for path in _.execution.files_created if path.endswith('.mp3')]

        expect(copied_songs).to.have.length(2)

    def should_name_copied_songs_using_number_title_album_artist():
        pattern = re.compile('^(\d+)?_([\s\w]+)?_([\s\w]+)?_([\s\w]+)?.mp3$')
        copied_songs = [path for path in _.execution.files_created if pattern.match(os.path.basename(path))]

        expect(copied_songs).to.have.length(2)

    def should_create_a_hierarchy_of_directories_using_artist_and_album():
        created_directories = [path for path in _.execution.files_created if not path.endswith('.mp3')]

        expect(created_directories).to.have(
            'Jono Bacon',
            'Jono Bacon/Released as a single',
            'Richard Stallman',
        )

    def should_avoid_overwriting_song_files():
        execution = _.env.run(*_.cmd + ['pull'])

        expect(execution.files_created).to.be.empty

    with context('with filesystem errors'):
        def should_directory_creation_failures():
            execution = _.env.run(*_.cmd + ['pull', '--dest', _.unwritable_dir])

            expect(execution.stdout).to.have('Could not create directory')

        def should_file_copy_failures():
            execution = _.env.run(*_.cmd + ['pull', '--plain', '--dest', _.unwritable_dir])

            expect(execution.stdout).to.have('Could not copy')

        @before.each
        def setup_unwritable_destination():
            _.unwritable_dir = 'unwritable'
            _.unwritable_dir_path = os.path.join(_.env_path, _.unwritable_dir)

            with open(_.unwritable_dir_path, 'w') as fakedir:
                fakedir.write('foo\n')

    with context('with --force option'):
        def should_not_mind_overwriting_song_files():
            _.env.run(*_.cmd + ['pull'])
            execution = _.env.run(*_.cmd + ['--force', 'pull'])

            expect(execution.files_updated).to.have.length(2)

    with context('with --dest <destination> option'):
        def should_copy_the_songs_to_the_destination_directory():
            execution = _.env.run(*_.cmd + ['--dest', 'pulled', 'pull'])

            copied_songs = [path for path in execution.files_created
                            if 'pulled' in path and path.endswith('.mp3')]

            expect(copied_songs).to.have.length(2)

    with context('with --plain option'):
        def should_copy_all_files_without_hierarchy():
            execution = _.env.run(*_.cmd + ['--plain', 'pull'])

            expect(execution.files_created).to.have.length(2)
