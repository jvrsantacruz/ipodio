# -*- coding: utf-8 -*-

import os
import re
import sys
import shutil

from .track import Track
from .console import Console
from .database import Database, Playlist


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


class Namespace(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)


def _header(console=Console()):
    return _line(Namespace(
        title=u'Title', album=u'Album', artist=u'Artist'))


def _separator(sep, console=Console()):
    return sep * console.width


def _line(track, console=Console()):
    width = console.relative_width(0.4)
    right_width = console.relative_width(0.2)

    return "{title:<{w}.{w}}  {album:<{w}.{w}}  {artist:<{rw}.{rw}}".format(
        title=track.title, album=track.album, artist=track.artist,
        w=width, rw=right_width)


def _internal_line(track):
    return "{title}  {album}  {artist}".format(
        title=track.title, album=track.album, artist=track.artist)


def _compile_regular_expression(expression):
    try:
        return re.compile(expression, flags=re.IGNORECASE)
    except (ValueError, TypeError, re.error):
        error('Invalid expression "{}"'.format(expression))


def _filter_by_regular_expression(regexp, tracks):
    return [track for track in tracks if regexp.search(_internal_line(track))]


def list(mount, expression=None):
    """List ipod contents"""
    database = Database.create(mount)
    database.update_index()

    tracks = database.tracks
    if expression is not None:
        regexp = _compile_regular_expression(' '.join(expression))
        tracks = _filter_by_regular_expression(regexp, tracks)

    if tracks:
        print(_header())
        print(_separator('-'))

    for track in _sorted_tracks(tracks):
        print(_line(track))

    if database.updated:
        database.save()


def duplicates(mount, expression):
    """List ipod contents grouping duplicated tracks"""
    database = Database.create(mount)
    database.update_index()

    regexp = _compile_regular_expression(' '.join(expression))
    track_groups = _sorted_tracks(database.duplicates, key=lambda g: first(g))

    if track_groups:
        print(_header())
        print(_separator('-'))

    for group in track_groups:
        if any(_filter_by_regular_expression(regexp, group)):
            for track in group:
                print(_line(track))

    if database.updated:
        database.save()


def _find_files(filenames, recursive):
    paths = map(os.path.abspath, filter(os.path.isfile, filenames))
    directories = map(os.path.abspath, filter(os.path.isdir, filenames))

    if recursive:
        paths.extend(os.path.join(root, file)
                     for directory in directories
                     for root, subdirs, files in os.walk(directory)
                     for file in files)
    else:
        paths.extend(os.path.join(directory, contained_file)
                     for directory in directories
                     for contained_file in os.listdir(directory))

    return paths


def push(mount, filename, force, recursive):
    """Push music files into the ipod"""
    database = Database.create(mount)
    database.update_index()

    for path in _find_files(filename, recursive):
        try:
            track = Track.create(path)
            track.update_hash()
        except Exception as error:
            print('Could not read track "{}": {}'.format(path, error))
            continue

        if not force and database.get(track):
            print('Not sending: "{}" which is already in the ipod.'
                  .format(track))
        else:
            database.add(track)

    if database.updated:
        def progress(database, track, n, total):
            print('Sending {}/{}: {}'.format(n, total, Track(track)))

        database.copy_files(progress)
        database.save()
    else:
        print('No files sent.')


def _make_destination_directory(dest):
    destination = os.path.realpath(dest or '.')

    if not os.path.exists(destination):
        try:
            os.mkdir(destination)
        except (OSError, IOError) as error:
            print('Could not create directory "{}": {}'.format(
                destination, error))
            return

    return destination


def _make_directory_hierarchy(base, *steps):
    base_path = base

    for step in steps:
        base_path = os.path.join(base_path, step)
        if not os.path.isdir(base_path):
            os.mkdir(base_path)

    return base_path


def _make_track_destination(destination, track, plain):
    if not plain:
        try:
            destination = _make_directory_hierarchy(
                destination, track.artist, track.album)
        except (OSError, IOError) as error:
            print('Could not create directory: "{}"'.format(error))
            return

    return os.path.join(destination, track.filename_from_tags)


def _copy_track_from_ipod(track_destination, track, force):
    if not force and os.path.exists(track_destination):
        print('Not overwriting existing file "{}" in "{}"'.format(
            track.filename_from_tags, os.path.dirname(track_destination)))
        return

    try:
        shutil.copy(track.filename, track_destination)
    except (shutil.Error, OSError, IOError) as error:
        print('Could not copy "{}" to "{}": {}'.format(
            track.filename, track_destination, error))
    else:
        print('Copied "{}" to "{}"').format(
            track.filename_from_tags, os.path.dirname(track_destination))


def pull(mount, expression, dest, force, plain):
    """List ipod contents grouping duplicated tracks"""
    database = Database.create(mount)

    regexp = _compile_regular_expression(' '.join(expression))
    tracks = _filter_by_regular_expression(regexp, database.tracks)

    destination = _make_destination_directory(dest)
    if not destination:
        return

    for track in tracks:
        track_destination = _make_track_destination(destination, track, plain)
        if track_destination:
            _copy_track_from_ipod(track_destination, track, force)


def rm(mount, expression, yes):
    database = Database.create(mount)
    database.update_index()

    regexp = _compile_regular_expression(' '.join(expression))
    tracks = _filter_by_regular_expression(regexp, database.tracks)

    if not tracks:
        print('No tracks removed.')
        return

    print(_header())
    print(_separator('-'))

    for track in tracks:
        print(_line(track))
        database.remove(track)

    if database.updated and (yes or raw_input('Remove? [y/n]: ') == 'y'):
        database.save()


def rename(mount, expression, replacement, yes):
    database = Database.create(mount)
    database.update_index()

    regexp = re.compile(' '.join(expression))
    tracks = [track for track in database.tracks if regexp.search(_line(track))]

    for track in tracks:
        track.internal['artist'] = regexp.sub(replacement, track.internal['artist'])
        track.internal['album'] = regexp.sub(replacement, track.internal['album'])
        track.internal['title'] = regexp.sub(replacement, track.internal['title'])

        print(_line(track))

    if tracks and (yes or raw_input('Rename? [y/n]: ') == 'y'):
        database.save()


def _find_playlist_named(name, playlists):
    return first(p for p in playlists if p.name == name)


def playlist(mount, name, expression):
    database = Database.create(mount)

    if name is None:
        for playlist in database.playlists:
            print(playlist.name)
        return

    playlist = _find_playlist_named(name, database.playlists)
    if not playlist:
        print('The playlist "{}" does not exist'.format(name))
        return

    tracks = playlist.tracks
    if expression is not None:
        regexp = _compile_regular_expression(' '.join(expression))
        tracks = _filter_by_regular_expression(regexp, tracks)

    if tracks:
        print('Playlist: ' + name)
        print(_header())
        print(_separator('-'))

    for track in tracks:
        print(_line(track))


def playlist_create(mount, name):
    database = Database.create(mount)

    if _find_playlist_named(name, database.playlists):
        print('A playlist named "{}" already exists'.format(name))
        return

    Playlist.create(name, database)
    database.save()
    print('Created playlist: "{}"'.format(name))


def playlist_add(mount, name, expression, yes, force):
    database = Database.create(mount)

    playlist = _find_playlist_named(name, database.playlists)
    if not playlist:
        print('The playlist "{}" does not exist'.format(name))
        return

    tracks = database.tracks
    if expression is not None:
        regexp = _compile_regular_expression(' '.join(expression))
        tracks = _filter_by_regular_expression(regexp, tracks)

    if not tracks:
        print('No tracks to add')
        return

    print('Playlist: ' + name)
    print(_header())
    print(_separator('-'))

    for track in tracks:
        print(_line(track))

    if tracks and (yes or raw_input('Add tracks to playlist? [y/n]: ') == 'y'):
        playlist.extend(tracks)
        database.save()
