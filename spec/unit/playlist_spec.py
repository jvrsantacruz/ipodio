#-*- coding: utf-8 -*-

from ipodio.track import Track
from ipodio.database import Playlist

from expects import expect
from mockito import mock, when
from mamba import describe, context, before


with describe(Playlist) as _:

    with context('the name property'):
        def should_return_the_playlist_name():
            expect(_.playlist.name).to.be.equal(_.playlist_name)

    with context('the tracks property'):
        def should_be_a_list():
            expect(_.populated_playlist.tracks).to.be.a(list)

        def should_contain_tracks():
            expect(_.populated_playlist.tracks[0]).to.be.a(Track)

    @before.all
    def setup():
        _.playlist_name = 'playlist'

        _.internal_playlist = mock()
        when(_.internal_playlist).get_name().thenReturn(_.playlist_name)
        _.playlist = Playlist(_.internal_playlist)

        _.populated_playlist = Playlist([None])
