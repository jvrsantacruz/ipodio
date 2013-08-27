#-*- coding: utf-8 -*-

import gpod
import mp3hash

from collections import defaultdict


class Hasher(object):
    def hash(self, filename, maxbytes=512 * 1024):
        return mp3hash.mp3hash(filename, maxbytes=maxbytes)


def first(iterable):
    for item in iterable:
        return item


class Track(object):
    def __init__(self, track, hasher=Hasher()):
        self.__track = track
        self._hasher = hasher

    @classmethod
    def create(cls, filename, internal_class=gpod.Track):
        return cls(internal_class(filename))

    def compute_hash(self):
        return self._hasher.hash(self.filename)

    def update_hash(self):
        self.hash = self.compute_hash()

    @property
    def _userdata(self):
        if not self.__track['userdata']:
            self.__track['userdata'] = {}
        return self.__track['userdata']

    @property
    def hash(self):
        return self._userdata.get('mp3hash')

    @hash.setter
    def hash(self, hash):
        self._userdata['mp3hash'] = hash

    @property
    def internal(self):
        return self.__track

    @property
    def filename(self):
        return (self.__track.ipod_filename()
                or self._userdata.get('filename_locale'))


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

    @property
    def __itdb(self):
        return self.__database._itdb

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

    @property
    def duplicates(self):
        return [group for group in self.index.itervalues() if len(group) > 1]

    def remove(self, track):
        self.updated = True
        self.__database.remove(track.internal)

    def copy_files(self):
        self.__database.copy_delayed_files()

    def save(self):
        self.__database.close()

if __name__ == "__main__":
    import sys
    file = sys.argv[1]
    hash = Hasher.hash(file)

    database = Database.create("/run/media/arl/IARL")
    database.update_index()

    print(database.get_by_hash(hash))
    print(database.find_by_hash(hash))

    print(len(list(database.duplicates)))
    print(str(database.get(hash).internal))

    print(len(list(database.tracks)))

    if database.updated:
        database.save()
