# -*- coding: utf-8 -*-

from mockito import mock


def patch_gpod_module():
    module = mock()

    module.Track = None
    module.Database = None

    import sys
    sys.modules['gpod'] = module

    return module


class Internal(object):
    _itdb = None

    def __init__(self, foo=None):
        self.data = foo

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, name):
        return self.data.__getitem__(name)

    def __setitem__(self, name, value):
        return self.data.__setitem__(name, value)

    def get(self, name, default=None):
        return self.data.get(name, default)

    def ipod_filename(self):
        return self.data.get('filename_locale', 'filename.mp3')

    @property
    def Playlists(self):
        return []
