# -*- coding: utf-8 -*-

from expects import expect
from mamba import describe, context, before, after

from spec.ui._ipod_helpers import *
from spec.ui._fixture import update_environment


with describe('ipodio playlist create') as _:

    @before.all
    def setup_all():
        _.playlist_name = 'playlist'
        update_environment(_)
        bootstrap_ipod(_.mountpoint_path)

    def should_print_an_error():
        execution = _.env.run(*_.cmd + ['playlist', 'create'], expect_error=True)

        expect(execution.stderr).to.have('Usage:')

    with context('given a playlist name'):
        def should_create_a_new_playlist():
            execution = _.env.run(*_.cmd + ['playlist', 'create', 'name'])

            expect(execution.stdout).to.have('Created playlist: "name"')

    with context('given an existing playlist name'):
        def should_refuse_to_create_a_new_playlist():
            execution = _.env.run(*_.cmd + ['playlist', 'create', _.playlist_name])

            expect(execution.stdout).to.have(
                'A playlist named "{}" already exists'.format(_.playlist_name))

        @before.all
        def setup_with_playlists():
            create_playlist(_.mountpoint_path, _.playlist_name)

        @after.all
        def cleanup_with_playlists():
            remove_ipod_playlist(_.mountpoint_path, _.playlist_name)
