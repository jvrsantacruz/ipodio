#-*- coding: utf-8 -*-

from ipodio.track import Track
from ipodio.database import Playlist

from expects import expect
from mockito import mock, when, verify, any
from mamba import describe, context, before


with describe(Playlist) as _:

    with context('when fabricated'):
        def should_have_an_internal_playlist():
            expect(_.fabricated_playlist).to.have.property(
                'internal', _.created_internal_playlist)

        def should_have_an_internal_database():
            verify(_.internal_playlist).constructor(
                _.database.internal, _.playlist_name)

    with context('the name property'):
        def should_be_the_playlist_name():
            expect(_.playlist.name).to.be.equal(_.playlist_name)

        def should_be_editable():
            _.playlist.name = 'foo'
            verify(_.internal_playlist).set_name('foo')

    with context('the tracks property'):
        def should_be_a_list():
            expect(_.populated_playlist.tracks).to.be.a(list)

        def should_contain_tracks():
            expect(_.populated_playlist.tracks[0]).to.be.a(Track)

    with context('when calling append'):
        def should_add_song_to_internal_playlist():
            _.playlist.append(_.track)

            verify(_.internal_playlist).add(any())

    with context('when calling extend'):
        def should_add_all_songs_to_internal_playlist():
            _.internal_playlist.invocations = []  # cleanup previous calls

            _.playlist.extend([_.track, _.track])

            verify(_.internal_playlist, times=2).add(any())

    with context('the is_master property'):
        def should_be_the_is_master_flag():
            _.playlist.is_master

            verify(_.internal_playlist).get_master()

    with context('when calling remove'):
        def should_detach_that_track_from_playlist():
            _.playlist.remove(_.track)

            verify(_.internal_playlist).remove(any())

    with context('when calling discard'):
        def should_detach_given_tracks_from_playlist():
            _.internal_playlist.invocations = []  # cleanup invocations

            _.playlist.discard([_.track, _.track])

            verify(_.internal_playlist, times=2).remove(any())

    @before.all
    def setup():
        _.playlist_smart = True
        _.playlist_name = 'playlist'

        _.internal_playlist = mock()
        when(_.internal_playlist).get_name().thenReturn(_.playlist_name)

        _.track = mock()
        _.database = mock()
        _.database.internal = 'foo'
        _.created_internal_playlist = 'foo'
        when(_.internal_playlist).constructor(_.database.internal, _.playlist_name)\
            .thenReturn(_.created_internal_playlist)

        _.playlist = Playlist(_.internal_playlist)
        _.populated_playlist = Playlist([None])
        _.fabricated_playlist = Playlist.create(
            _.playlist_name, _.database, _.internal_playlist.constructor)
