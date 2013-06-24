# -*- coding: utf-8 -*-

from spec.fixtures import Mock, Internal

import sys
sys.modules['gpod'] = Mock()  # mock system-wide packages

from ipodio.database import Track

from expects import expect
from mamba import describe, context, before


with describe(Track) as _:

    with context('when fabricated'):
        def it_should_have_an_internal_track():
            expect(_.fabricated_track.internal).to.be.an(_.internal_class)

        def it_should_have_hash_to_none():
            expect(_.fabricated_track.hash).to.be.none

    with context('when constructed'):
        def it_should_have_an_internal_track_():
            expect(_.track.internal).to.be.an(_.internal_class)

        def it_should_have_hash_to_none_():
            expect(_.track.hash).to.be.none

        def it_should_save_hash_when_set():
            _.track.hash = _.hash

            expect(_.track.hash).to.be(_.hash)

        def it_should_return_the_hash_when_computed():
            expect(_.track.compute_hash()).to.be(_.hash)

    @before.all
    def fixture():
        _.internal_class = Internal
        _.hash = '204939024023840234'
        _.hasher = lambda filename: _.hash

        _.track_data = {'userdata': {}}
        _.fabricated_track = Track.create(
            _.track_data, internal_class=_.internal_class)
        _.track = Track(Internal(_.track_data), hasher=_.hasher)
