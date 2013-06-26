#-*- coding: utf-8 -*-


from spec.fixtures import Mock, Internal

import sys
sys.modules['gpod'] = Mock()  # mock system-wide packages

from ipodio.database import Track, Database

from expects import expect
from mamba import describe, context, before


with describe(Database) as _:

    with context('when fabricated'):
        def it_should_have_an_internal_database():
            expect(_.fabricated.internal).to.be.an(_.internal_class)

    with context('when constructed'):
        def it_should_have_an_empty_index():
            expect(_.database.index).to.be.empty

        def it_should_be_marked_as_not_updated():
            expect(_.database.updated).to.be.false

        with context('when calling find'):
            def it_should_return_an_empty_collection():
                expect(_.database.find(_.hash)).to.be.empty

        with context('when calling get'):
            def it_should_return_None():
                expect(_.database.get(_.hash)).to.be.none

    with context('when updating index'):
        def it_should_populate_index():
            expect(_.database.index).not_to.be.empty

        with context('when calling find'):
            def it_should_return_a_collection():
                expect(_.database.find(_.hash)).not_to.be.empty

        with context('when calling get'):
            def it_should_return_a_Track():
                expect(_.database.get(_.hash)).to.be.a(Track)

            def it_should_return_a_track_with_the_given_hash():
                expect(_.database.get(_.hash)).to.have.property('hash', _.hash)

        with context('when accessing tracks'):
            def it_should_be_a_collection():
                expect(_.database.tracks).not_to.be.empty

        @before.all
        def fixture():
            _.database.update_index()

    @before.all
    def fixtures():
        _.internal_class = Internal
        _.hash = '204939024023840234'
        _.internal_track = Internal({'userdata': {'mp3hash': _.hash}})
        _.database = Database(Internal([_.internal_track]))
        _.fabricated = Database.create('', internal_class=_.internal_class)
