# -*- coding: utf-8 -*-
"""
Track

Provides ordered and convenient access to the Track data and a hashing API so
the track can be referred by its inner contents. It aims to be a very thin
wrapper around gpod.Track.

Current implementation includes two hashing processes for each song file.

1. gpod's default sha1 hashing accessible through gtrack['userdata']['sha1_hash]
2. mp3hash partial hashing to avoid track's id3 tags noise in their hashes

    # Create the track without hashing the file
    track = ipodio.Track(gpod.Track('/path/to/song'))

    # Read file content's and obtain a hash
    # This will be stored as userdata within the gpod's own database
    track.update_hash()
"""

import gpod
import mp3hash


class Hasher(object):
    def hash(self, filename, maxbytes=512 * 1024):
        return mp3hash.mp3hash(filename, maxbytes=maxbytes)


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

    def _get_trackdata(self, name):
        return self.__track.__getitem__(name)

    def _get_unicode_trackdata(self, name):
        return unicode(self._get_trackdata(name) or '')

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

    @property
    def filename_from_tags(self):
        def _clean_filename(filename):
            space_chars = [' ', '-']
            not_allowed_chars = [
                '.', '!', ':', ';', '/', ',', '(', ')', '[', ']', '{',
                '}', '&', '"', "'", '*', '\\', '<', '>',
            ]

            table = dict((ord(c), u'') for c in not_allowed_chars)
            table.update(dict((ord(c), u'_') for c in space_chars))

            return filename.translate(table)

        filename = u'{number}_{title}_{album}_{artist}'.format(
            number=self.number or 0, title=self.title,
            album=self.album, artist=self.artist)

        return "{filename}.{extension}".format(
            filename=_clean_filename(filename),
            extension=self.filename.split('.')[-1])

    @property
    def number(self):
        return self._get_trackdata('track_nr')

    @property
    def title(self):
        return self._get_unicode_trackdata('title')

    @property
    def album(self):
        return self._get_unicode_trackdata('album')

    @property
    def artist(self):
        return self._get_unicode_trackdata('artist')

    def __str__(self):
        number = u"{}. ".format(self.number) if self.number else u""

        return "{number}'{title}' by: '{artist}'".format(
            number=number, title=self.title, artist=self.artist)
