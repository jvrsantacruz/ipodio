# -*- coding: utf-8 -*-

import re
import os
import sys
import shutil

import ipodio

from manager import Manager


manager = Manager()


def first(collection):
    for element in collection:
        return element


def error(message):
    print('Error: ' + message)
    sys.exit(1)


def _sorted_tracks(tracks, key=None):
    def by(field):
        def accessor(element):
            return (key(element) if key else element).internal[field]
        return accessor

    tracks.sort(key=by('track_nr'))
    tracks.sort(key=by('album'))
    tracks.sort(key=by('artist'))

    return tracks


def _line(data):
    title = data['title'] or ''
    album = data['album'] or ''
    artist = data['artist'] or ''

    return "{title:30}  {album:30}  {artist:18}".format(
        title=title[:30], album=album[:30], artist=artist[:18])


def _compile_regular_expression(expression):
    try:
        return re.compile(expression, flags=re.IGNORECASE)
    except (ValueError, TypeError, re.error):
        error('Invalid expression "{}"'.format(expression))


def _filter_by_regular_expression(regexp, tracks):
    return [track for track in tracks if regexp.search(_line(track.internal))]


@manager.command
def list(mountpoint, expression):
    """List ipod contents"""
    database = ipodio.Database.create(mountpoint)
    database.update_index()

    print(_line(dict(title='Title', album='Album', artist='Artist')))
    print('-' * 80)

    for track in _sorted_tracks(database.tracks):
        print(_line(track.internal))

    if database.updated:
        database.save()


def main():
    manager.main()


if __name__ == '__main__':
    main()
