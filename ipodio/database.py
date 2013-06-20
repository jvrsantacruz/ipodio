#-*- coding: utf-8 -*-

import gpod
import mp3hash

from itertools import chain
from collections import defaultdict


def hasher(filename, maxbytes=512 * 1024):
    return mp3hash.mp3hash(filename, maxbytes=maxbytes)


def first(iterable):
    for item in iterable:
        return item


class Track(object):
    def __init__(self, track):
        self.__track = track

    @classmethod
    def create(cls, filename, internal_class=gpod.Track):
        return cls(internal_class(filename))

    def compute_hash(self):
        return hasher(self.filename)

    @property
    def hash(self):
        return self.__userdata.get('mp3hash')

    @hash.setter
    def hash(self, hash):
        self.__userdata['mp3hash'] = hash

    @property
    def __userdata(self):
        if not self.__track['userdata']:
            self.__track['userdata'] = {}
        return self.__track['userdata']

    @property
    def internal(self):
        return self.__track

    @property
    def filename(self):
        return self.__track.ipod_filename() or self.__userdata['filename_locale']

    def __repr__(self):
        return ("<Track Artist:{t[artist]} Title:{t[title]} Album:{t[album]} "
                "{hash}>".format(t=self.__track, hash=self.hash or ''))


class Database(object):
    def __init__(self, database):
        self.__database = database
        self.index = defaultdict(set)
        self.updated = False

    @property
    def __tracks(self):
        return (Track(track) for track in self.__database)

    @classmethod
    def create(cls, mountpoint, internal_class=gpod.Database):
        return cls(internal_class(mountpoint))

    @property
    def tracks(self):
        return chain.from_iterable(self.index.itervalues())

    def __add_index(self, track):
        if not track.hash:
            self.updated = True
            track.hash = track.compute_hash()

        self.index[track.hash].add(track)

    def update_index(self):
        for track in self.__tracks:
            self.__add_index(track)

    def get(self, hash):
        return first(self.find(hash))

    def find(self, hash):
        return self.index[hash]

    def add(self, track):
        self.__add_index(track)
        self.__database.add(track.internal)

    def add_file(self, filename):
        self.add(Track.create(filename))

    @property
    def duplicates(self):
        return (group for group in self.index.itervalues() if len(group) > 1)

    @property
    def internal(self):
        return self.__database

    def save(self):
        self.__database.copy_delayed_files()
        self.__database.close()


if __name__ == "__main__":
    import sys
    file = sys.argv[1]
    hash = hasher(file)

    database = Database.create("/run/media/arl/IARL")
    database.update_index()

    print(database.get(hash))
    print(database.find(hash))

    print(len(list(database.duplicates)))
    print(str(database.get(hash).internal))

    print(len(list(database.tracks)))

    if database.updated:
        database.save()
