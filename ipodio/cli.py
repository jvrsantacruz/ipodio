# -*- coding: utf-8 -*-
"""
iPodio

Usage:
  ipodio list   [options] [<expression>...]
  ipodio push   [options] [--force] [--recursive] <filename>...
  ipodio pull   [options] [--dest=<directory>] [--force] [--plain] [<expression>...]
  ipodio rm     [options] <expression>...
  ipodio rename [options] <expression> <replacement>
  ipodio duplicates [options] [<expression>...]

Options:
  -m PATH, --mount PATH  Path to the iPod's mountpoint.
  -y , --yes  Do not prompt the user with questions.
"""

import re
import os
import sys
import shutil

from docopt import docopt

from . import __version__
from .console import Console
from .database import Database, Track


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


def _separator(sep, console=Console()):
    return sep * console.width


def _line(data, console=Console()):
    column_width = console.relative_width(0.4)
    right_column_width = console.relative_width(0.2)

    title = unicode(data['title'] or '')[:column_width]
    album = unicode(data['album'] or '')[:column_width]
    artist = unicode(data['artist'] or '')[:right_column_width]

    return "{title:<{w}}  {album:<{w}}  {artist:<{rw}}".format(
        title=title, album=album, artist=artist,
        w=column_width, rw=right_column_width)


def _internal_line(data):
    title = unicode(data['title'] or '')
    album = unicode(data['album'] or '')
    artist = unicode(data['artist'] or '')

    return "{title}  {album}  {artist}".format(
        title=title, album=album, artist=artist)


def _compile_regular_expression(expression):
    try:
        return re.compile(expression, flags=re.IGNORECASE)
    except (ValueError, TypeError, re.error):
        error('Invalid expression "{}"'.format(expression))


def _filter_by_regular_expression(regexp, tracks):
    return [track for track in tracks if regexp.search(_internal_line(track.internal))]


def list(mount, expression=None):
    """List ipod contents"""
    database = Database.create(mount)
    database.update_index()

    tracks = database.tracks
    if expression is not None:
        regexp = _compile_regular_expression(' '.join(expression))
        tracks = _filter_by_regular_expression(regexp, tracks)

    if tracks:
        print(_line(dict(title='Title', album='Album', artist='Artist')))
        print(_separator('-'))

    for track in _sorted_tracks(tracks):
        print(_line(track.internal))

    if database.updated:
        database.save()


def duplicates(mount, expression):
    """List ipod contents grouping duplicated tracks"""
    database = Database.create(mount)
    database.update_index()

    regexp = _compile_regular_expression(' '.join(expression))
    track_groups = _sorted_tracks(database.duplicates, key=lambda g: first(g))

    if track_groups:
        print(_line(dict(title='Title', album='Album', artist='Artist')))
        print(_separator('-'))

    for group in track_groups:
        if any(_filter_by_regular_expression(regexp, group)):
            for track in group:
                print(_line(track.internal))

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
        except Exception, error:
            print('Could not read track "{}": {}'.format(path, error))
            continue

        if not force and database.get(track):
            print('Not sending: "{}" which is already in the ipod.'
                  .format(track))
        else:
            database.add(track)

    if database.updated:
        def progress(database, track, n, total):
            print('Sending {}/{}: {}'.format(n, total, track))

        database.copy_files(progress)
        database.save()
    else:
        print('No files sent.')


def _make_directory_hierarchy(base, *steps):
    base_path = base

    for step in steps:
        base_path = os.path.join(base_path, step)
        if not os.path.isdir(base_path):
            os.mkdir(base_path)

    return base_path


def pull(mount, expression, dest, force, plain):
    """List ipod contents grouping duplicated tracks"""
    database = Database.create(mount)
    database.update_index()

    regexp = _compile_regular_expression(' '.join(expression))
    tracks = _filter_by_regular_expression(regexp, database.tracks)

    destination = os.path.realpath(dest or '.')
    if not os.path.exists(destination):
        os.mkdir(destination)

    for track in tracks:
        track_nr = track.internal['track_nr'] or 0
        title = unicode(track.internal['title'] or '')
        album = unicode(track.internal['album'] or '')
        artist = unicode(track.internal['artist'] or '')

        track_name = u'{track_nr}_{title}_{album}_{artist}.{extension}'.format(
            track_nr=track_nr, title=title, album=album, artist=artist,
            extension=track.filename.split('.')[-1])

        track_destination = os.path.join(destination, track_name)

        if not plain:
            directory_hierarchy = _make_directory_hierarchy(
                destination, artist, album)
            track_destination = os.path.join(directory_hierarchy, track_name)

        if not force and os.path.exists(track_destination):
            print('Not overwriting {}'.format(
                track_name, os.path.dirname(track_destination)))
        else:
            print('Copying {} to {}').format(
                track_name, os.path.dirname(track_destination))
            shutil.copy(track.filename, track_destination)


def rm(mount, expression, yes):
    database = Database.create(mount)
    database.update_index()

    regexp = _compile_regular_expression(' '.join(expression))
    tracks = _filter_by_regular_expression(regexp, database.tracks)

    if not tracks:
        print('No tracks removed.')
        return

    print(_line(dict(title='Title', album='Album', artist='Artist')))
    print(_separator('-'))

    for track in tracks:
        print(_line(track.internal))
        database.remove(track)

    if database.updated and (yes or raw_input('Remove? [y/n]: ') == 'y'):
        database.save()


def rename(mount, expression, replacement, yes):
    database = Database.create(mount)
    database.update_index()

    regexp = re.compile(' '.join(expression))
    tracks = [track for track in database.tracks if regexp.search(_line(track.internal))]

    for track in tracks:
        track.internal['artist'] = regexp.sub(replacement, track.internal['artist'])
        track.internal['album'] = regexp.sub(replacement, track.internal['album'])
        track.internal['title'] = regexp.sub(replacement, track.internal['title'])

        print(_line(track.internal))

    if tracks and (yes or raw_input('Rename? [y/n]: ') == 'y'):
        database.save()


class Options(object):
    def __init__(self, options, defaults=None):
        self.defaults = defaults if defaults else {}
        self.options = self._parse_options(options)
        self.arguments = self._parse_arguments(options)
        self.commands = self._parse_commands(options)
        self.active_commands = self._parse_active_commands(self.commands)
        self.active_command = self._parse_active_command(self.active_commands)
        data = dict(self.options.items() + self.arguments.items())
        self.data = self._parse_default_values(data, self.defaults)

    def _parse_default_values(self, options, defaults):
        options.update({key: value for key, value in defaults.items()
                        if options.get(key) is None})
        return options

    def _parse_options(self, options):
        return {k.replace('-', ''): v
                for k, v in options.items() if k.startswith('-')}

    def _parse_arguments(self, options):
        return {k.replace('<', '').replace('>', ''): v
                for k, v in options.items() if k.startswith('<')}

    def _parse_commands(self, options):
        return {k: v for k, v in options.items() if k[0] not in ('-', '<')}

    def _parse_active_commands(self, commands):
        return [k for k, v in commands.items() if v]

    def _parse_active_command(self, active_commands):
        return active_commands[0] if active_commands else None


def function_argument_names(function):
    return function.func_code.co_varnames[:function.func_code.co_argcount]


def pluck(dct, names):
    return {name: dct.get(name) for name in names}


def main():
    defaults = {'mount': os.environ.get('IPODIO_MOUNTPOINT')}
    parsed_input = docopt(__doc__, version=__version__)
    options = Options(parsed_input, defaults)

    functions = {'list': list, 'push': push, 'pull': pull, 'rm': rm, 'duplicates': duplicates, 'rename': rename}
    function = functions[options.active_command]
    function_arguments = pluck(options.data, function_argument_names(function))
    function(**function_arguments)


if __name__ == '__main__':
    main()
