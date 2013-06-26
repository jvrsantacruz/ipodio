# -*- coding: utf-8 -*-

import ipodio

from manager import Manager

manager =  Manager()


def _sorted_tracks(tracks):
    def by(field):
        return lambda t: t.internal[field]

    tracks.sort(key=by('track_nr'))
    tracks.sort(key=by('album'))
    tracks.sort(key=by('artist'))

    return tracks


def _line(data):
    return "{0[title]:30} {0[album]:30} {0[artist]:20}".format(data)


@manager.command
def list(mountpoint):
    """Lists ipod contents"""
    database = ipodio.Database.create(mountpoint)
    database.update_index()

    print(_line(dict(title='Title', album='Album', artist='Artist')))
    print('-' * 80)

    for track in _sorted_tracks(database.tracks):
        print(_line(track.internal))

    if database.updated:
        database.save()


if __name__ == '__main__':
    manager.main()
