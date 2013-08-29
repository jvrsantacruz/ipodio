# -*- coding: utf-8 -*-
"""
iPodio

Usage:
  ipodio list   [options] [<expression>...]
  ipodio push   [options] [--force] <filename>...
  ipodio pull   [options] [--dest=<directory>] [<expression>...]
  ipodio rm     [options] [<expression>...]
  ipodio rename [options] <expression> <replacement>
  ipodio duplicates [options] [<expression>...]

Options:
  -m PATH, --mount PATH  Path to the iPod's mountpoint.
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


def _compile_regular_expression(expression):
    try:
        return re.compile(expression, flags=re.IGNORECASE)
    except (ValueError, TypeError, re.error):
        error('Invalid expression "{}"'.format(expression))


def _filter_by_regular_expression(regexp, tracks):
    return [track for track in tracks if regexp.search(_line(track.internal))]


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


def push(mount, filename, force=False):
    """Push music files into the ipod"""
    paths = [os.path.abspath(path) for path in filename if os.path.isfile(path)]
    directories = [os.path.abspath(path) for path in filename if os.path.isdir(path)]
    paths.extend(os.path.join(directory, contained_file)
                 for directory in directories
                 for contained_file in os.listdir(directory))

    database = Database.create(mount)
    database.update_index()

    for path in paths:
        try:
            track = Track.create(path)
            track.update_hash()
        except Exception, error:
            print('Could not read track "{}": {}'.format(path, error))
            continue

        if not force and database.get(track):
            print('Not sending: "{}" which is already in the ipod.'
                  .format(repr(track.internal)))
        else:
            database.add(track)
            print(repr(track.internal))

    if database.updated:
        def progress(database, track, n, total):
            print('Sending {}/{}: {}'.format(n, total, track))

        database.copy_files(progress)
        database.save()
    else:
        print('No files sent.')


def pull(mount, expression, dest):
    """List ipod contents grouping duplicated tracks"""
    database = Database.create(mount)
    database.update_index()

    destination = os.path.realpath(dest or '.')

    regexp = _compile_regular_expression(' '.join(expression))
    tracks = _filter_by_regular_expression(regexp, database.tracks)

    for track in tracks:
        if not track.filename:
            print('No filename for track {}'.format(track.internal))

        track_name = u'{track_nr}_{title}_{album}_{artist}.{extension}'.format(
            track_nr=track.internal['track_nr'],
            title=track.internal['title'],
            album=track.internal['album'],
            artist=track.internal['artist'],
            extension=track.filename.split('.')[-1]
        )

        track_destination = os.path.join(destination, track_name)

        if os.path.exists(track_destination):
            print('Not overwriting {} at {}'.format(track_name, destination))
        else:
            print('Copying {} to {}').format(track_name, destination)
            shutil.copy(track.filename, track_destination)


def rm(mount, expression):
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

    if database.updated and raw_input('Remove? [y/n]: ') == 'y':
        database.save()


        database.save()


def rename(mount, expression, replacement):
    database = Database.create(mount)
    database.update_index()

    regexp = re.compile(' '.join(expression))
    tracks = [track for track in database.tracks if regexp.search(_line(track.internal))]

    for track in tracks:
        track.internal['artist'] = regexp.sub(replacement, track.internal['artist'])
        track.internal['album'] = regexp.sub(replacement, track.internal['album'])
        track.internal['title'] = regexp.sub(replacement, track.internal['title'])

        print(_line(track.internal))

    if tracks and raw_input('Rename [y/n]: ') == 'y':
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
