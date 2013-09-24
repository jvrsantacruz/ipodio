# -*- coding: utf-8 -*-

from expects import expect
from mamba import describe, context, before

from spec.ui._ipod_helpers import *
from spec.ui._fixture import update_environment


with describe('ipodio playlist create') as _:

    @before.all
    def setup_all():
        _.new_name = 'leño'
        _.playlist_name = 'playlist'
        _.existing_name = 'roña'
        update_environment(_)
        bootstrap_ipod(_.mountpoint_path)
        create_playlist(_.mountpoint_path, _.playlist_name)
        create_playlist(_.mountpoint_path, _.existing_name)

    def should_print_an_error():
        execution = _.env.run(*_.cmd + ['playlist', 'rename'], expect_error=True)

        expect(execution.stderr).to.have('Usage:')

    with context('given a non existing playlist name'):
        def should_print_an_error_():
            execution = _.env.run(*_.cmd + ['playlist', 'rename', _.new_name, _.playlist_name])

            expect(execution.stdout).to.have('does not exist')

    with context('given an existing playlist name'):
        def should_print_an_error__():
            execution = _.env.run(*_.cmd + ['playlist', 'rename'], expect_error=True)

            expect(execution.stderr).to.have('Usage:')

        with context('given an existing playlist name'):
            def should_print_an_error___():
                execution = _.env.run(*_.cmd + ['playlist', 'rename', _.playlist_name, _.existing_name])

                expect(execution.stdout).to.have('already exists')

        with context('and another valid playlist name'):
            def should_rename_that_playlist():
                execution = _.env.run(*_.cmd + ['playlist', 'rename', _.playlist_name, _.new_name])

                playlists = get_ipod_playlists_by_name(_.mountpoint_path)

                expect(playlists).to.have(_.new_name)
                expect(playlists).not_to.have(_.playlist_name)
                expect(execution.stdout).to.have('renamed to')
