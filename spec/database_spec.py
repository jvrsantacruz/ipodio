#-*- coding: utf-8 -*-

from ipodio.database import Database

from expects import expect
from mamba import describe, context, before


with describe(Database) as _:

    with context('when constructed'):
        def it_should_have_an_empty_index():
            expect(_.database.index).to.be.empty

        def it_should_be_marked_as_not_updated():
            expect(_.database.updated).to.be.false

    with context('when fabricated'):
        def it_should_have_an_internal_database():
            expect(_.fabricated.internal).to.be.an(_.internal_class)

    with context('when calling find'):
        def it_should_return_an_empty_iterable():
            expect(list(_.database.find(''))).to.be.empty

    with context('when calling get'):
        def it_should_return_None():
            expect(_.database.get('')).to.be.none

    with context('when accessing tracks'):
        def it_should_be_an_empty_iterable():
            expect(list(_.database.tracks)).to.be.empty

    @before.all
    def fixtures():
        class Internal(object):
            def __init__(self, foo=None):
                pass

        _.internal_class = Internal
        _.database = Database(Internal())
        _.fabricated = Database.create('', internal_class=_.internal_class)
