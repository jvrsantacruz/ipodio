#-*- coding: utf-8 -*-
"""
Database

Stores all the tracks contained within the iPod indexed in a convenient way for
fast retrieval, iteration, addition and removal.

Intended as a very thin wrapper around gpod.Database in order to provide a
cleaner interface, extra functionality and resolve some flaws.

    # Create the database without indexing its contents
    database = ipodio.Database(gpod.Database('/ipod/mountpoint'))

    # Index all tracks by its hash.
    # The chosen structure is a dictionary of sets,
    # which might be regarded as # a multi-dict.
    database.update_index()

    # The indexing allows to get a database by its inner contents
    # and thus making it easy to detect and avoid duplication.
    database.get_by_hash('some_calculated_track_hash')

    # Basic operations along with a ipodio.Track instance
    database.get(track)
    database.add(track)
    database.remove(track)

    # The gpod Database reference is public until those use cases which need it
    # are sorted out and implemented as part of the class.
    database.internal

    # A flag is maintained and updated on database modification
    # so unnecessary expensive closing work is spared by checking.
    if database.updated:
        database.copy_files()   # Physically send track files if needed
        database.save()         # Save the current database state and store it
"""

import gpod

from collections import defaultdict

from .track import Track


def first(iterable):
    for item in iterable:
        return item


class Playlist(object):
    def __init__(self, playlist):
        self.__playlist = playlist

    @property
    def name(self):
        return self.__playlist.get_name()

    @property
    def tracks(self):
        return [Track(track) for track in self.__playlist]


class Database(object):
    def __init__(self, database):
        self.__database = database
        self.index = defaultdict(set)
        self.updated = False

    @classmethod
    def create(cls, mountpoint, internal_class=gpod.Database):
        return cls(internal_class(mountpoint))

    @property
    def internal(self):
        return self.__database

    @property
    def tracks(self):
        return [Track(track) for track in self.__database]

    def __add_index(self, track):
        if not track.hash:
            self.updated = True
            track.update_hash()

        self.index[track.hash].add(track)

    def update_index(self):
        for track in self.tracks:
            self.__add_index(track)

    def get(self, track):
        return self.get_by_hash(track.hash)

    def get_by_hash(self, hash):
        return first(self.find_by_hash(hash))

    def find_by_hash(self, hash):
        return self.index[hash]

    def add(self, track):
        self.updated = True
        self.__add_index(track)
        self.__database.add(track.internal)
        self.__database.Master.add(track.internal)

    @property
    def duplicates(self):
        return [group for group in self.index.itervalues() if len(group) > 1]

    def remove(self, track):
        self.updated = True
        self.__database.remove(track.internal, quiet=True)

    def copy_files(self, progress=None):
        self.__database.copy_delayed_files(progress)

    def save(self):
        self.__database.close()
