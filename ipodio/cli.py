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


class Console(object):
    width = None

    def _get_console_size(self):
        import sys
        return (self._get_window_size(sys.stdin)
                or self._get_window_size(sys.stdout)
                or self._get_window_size(sys.stderr)
                or self._get_term_window_size()
                or (25, 80))

    def _get_term_window_size(self):
        try:
            with os.open(os.ctermid(), os.O_RDONLY) as term:
                return self._get_window_size(term)
        except:
            return None

    def _get_window_size(self, fd):
        import struct, fcntl, termios
        try:
            data = fcntl.ioctl(fd, termios.TIOCGWINSZ, '12345678')
            height, width, hp, wp = struct.unpack('HHHH', data)
            return height, width
        except:
            return None

    @property
    def width(self):
        if self.width is None:
            _, self._width = self._get_console_size()
        return self._width

    def relative_width(self, percentage):
        """Return the width of a part of the screen in number of characters"""
        return int((self.width - 4) * percentage)


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

    regexp = _compile_regular_expression(expression)
    tracks = _filter_by_regular_expression(regexp, database.tracks)

    if tracks:
        print(_line(dict(title='Title', album='Album', artist='Artist')))
        print('-' * 80)

    for track in _sorted_tracks(tracks):
        print(_line(track.internal))

    if database.updated:
        database.save()


@manager.command
def duplicates(mountpoint):
    """List ipod contents grouping duplicated tracks"""
    database = ipodio.Database.create(mountpoint)
    database.update_index()

    track_groups = _sorted_tracks(database.duplicates, key=lambda g: first(g))

    if track_groups:
        print(_line(dict(title='Title', album='Album', artist='Artist')))
        print('-' * 80)

    for group in track_groups:
        for track in group:
            print(_line(track.internal))

    if database.updated:
        database.save()


@manager.command
def push(mountpoint, filename, force=False):
    """List ipod contents grouping duplicated tracks"""
    database = ipodio.Database.create(mountpoint)
    database.update_index()

    track = ipodio.database.Track.create(filename)
    track.update_hash()

    if not force and database.get(track):
        return '{} is already in the ipod'.format(repr(track.internal))

    database.add(track)
    database.copy_files()
    database.save()

    return repr(track.internal)


@manager.command
def pull(mountpoint, expression):
    """List ipod contents grouping duplicated tracks"""
    database = ipodio.Database.create(mountpoint)
    database.update_index()

    destination = os.path.realpath('.')

    regexp = _compile_regular_expression(expression)
    tracks = _filter_by_regular_expression(regexp, database.tracks)

    for track in tracks:
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


@manager.command
def rm(mountpoint, expression):
    database = ipodio.Database.create(mountpoint)
    database.update_index()

    print(_line(dict(title='Title', album='Album', artist='Artist')))
    print('-' * 80)

    regexp = _compile_regular_expression(expression)
    tracks = _filter_by_regular_expression(regexp, database.tracks)

    for track in tracks:
        print(_line(track.internal))
        database.remove(track)

    if database.updated:
        database.save()


@manager.command
def rename(mountpoint, expression, replacement):
    database = ipodio.Database.create(mountpoint)
    database.update_index()

    regexp = _compile_regular_expression(expression)
    tracks = _filter_by_regular_expression(regexp, database.tracks)

    for track in tracks:
        track.internal['artist'] = regexp.sub(replacement, track.internal['artist'])
        track.internal['album'] = regexp.sub(replacement, track.internal['album'])
        track.internal['title'] = regexp.sub(replacement, track.internal['title'])

        print(_line(track.internal))

    if tracks:
        database.save()


class Options(object):
    def __init__(self, options):
        self.options = self._parse_options(options)
        self.arguments = self._parse_arguments(options)
        self.data = dict(self.options.items() + self.arguments.items())
        self.commands = self._parse_commands(options)
        self.active_commands = self._parse_active_commands(self.commands)
        self.active_command = self._parse_active_command(self.active_commands)

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


def main():
    manager.main()


if __name__ == '__main__':
    main()
