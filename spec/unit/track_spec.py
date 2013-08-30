# -*- coding: utf-8 -*-

from spec.unit.fixtures import Internal, patch_gpod_module

patch_gpod_module()

from ipodio.database import Track

from expects import expect
from mockito import mock, spy, when, verify, any
from mamba import describe, context, before


with describe(Track) as _:

    with context('when fabricated'):
        def it_should_have_an_internal_track():
            expect(_.fabricated_track.internal).to.be.an(_.internal_class)

    with context('when constructed'):
        def it_should_have_an_internal_track_():
            expect(_.track.internal).to.be.an(_.internal_class)

        def it_should_set_hash_to_none():
            expect(_.track.hash).to.be(None)

    with context('when update_hash'):
        def it_should_compute_hash():
            track = spy(_.track)

            track.update_hash()

            verify(_.track._hasher).hash('filename')

    with context('when compute_hash'):
        def it_should_use_the_hasher():
            _.track.compute_hash()

            verify(_.track._hasher).hash('filename')

        def it_should_return_the_hash_when_computed():
            expect(_.track.compute_hash()).to.be(_.hash)

    def it_should_save_hash_when_set():
        _.track.hash = _.hash

        expect(_.track.hash).to.be(_.hash)

    @before.each
    def fixture():
        _.internal_class = Internal
        _.hash = '204939024023840234'

        _.hasher = mock()
        when(_.hasher).hash(any(str)).thenReturn(_.hash)

        _.track_data = {'userdata': {}}
        _.track = Track(Internal(_.track_data), hasher=_.hasher)
        _.fabricated_track = Track.create(
            _.track_data, internal_class=_.internal_class)
