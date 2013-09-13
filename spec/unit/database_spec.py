#-*- coding: utf-8 -*-


from spec.unit.fixtures import Internal, patch_gpod_module

gpod = patch_gpod_module()

from ipodio.track import Track
from ipodio.database import Database

from expects import expect
from mamba import describe, context, before


with describe(Database) as _:

    with context('when fabricated'):
        def should_have_an_internal_database():
            expect(_.fabricated.internal).to.be.an(_.internal_class)

    with context('when constructed'):
        def should_have_an_empty_index():
            expect(_.database.index).to.be.empty

        def should_be_marked_as_not_updated():
            expect(_.database.updated).to.be.false

        with context('when calling find_by_hash'):
            def should_return_an_empty_collection():
                expect(_.database.find_by_hash(_.hash)).to.be.empty

        with context('when calling get'):
            def should_return_None():
                expect(_.database.get_by_hash(_.hash)).to.be.none

        with context('when accessing tracks'):
            def should_return_a_list_with_tracks():
                expect(_.database.tracks).not_to.be.empty

    with context('when updating index'):
        def should_populate_index():
            expect(_.database.index).not_to.be.empty

        with context('when calling find_by_hash'):
            def should_return_a_collection():
                expect(_.database.find_by_hash(_.hash)).not_to.be.empty

        with context('when calling get_by_hash'):
            def should_return_a_Track():
                expect(_.database.get_by_hash(_.hash)).to.be.a(Track)

            def should_return_a_track_with_the_given_hash():
                expect(_.database.get_by_hash(_.hash)).to.have.property('hash', _.hash)

        with context('when accessing tracks'):
            def should_be_a_collection():
                expect(_.database.tracks).not_to.be.empty

        @before.all
        def fixture():
            _.database.update_index()

    with context('the playlists property'):
        def should_be_a_list():
            expect(_.database.playlists).to.be.a(list)

    @before.all
    def fixtures():
        _.internal_class = Internal
        _.hash = '204939024023840234'
        _.internal_track = Internal({'userdata': {'mp3hash': _.hash}})
        _.database = Database(Internal([_.internal_track]))
        _.fabricated = Database.create('', internal_class=_.internal_class)
