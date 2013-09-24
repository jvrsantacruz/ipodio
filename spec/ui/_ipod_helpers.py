# -*- coding: utf-8 -*-

from contextlib import contextmanager

import gpod


def get_database(mountpoint):
    return gpod.Database(mountpoint)


@contextmanager
def database(mountpoint):
    db = get_database(mountpoint)
    yield db
    db.close()


def bootstrap_ipod(mountpoint):
    gpod.itdb_init_ipod(mountpoint, None, 'my iPod', None)


def populate_ipod(mountpoint, files):
    with database(mountpoint) as db:
        for path in files:
            db.new_Track(filename=path)
        db.copy_delayed_files()


def empty_ipod(mountpoint):
    with database(mountpoint) as db:
        [db.remove(track, quiet=True) for track in db]


def find_playlist(database, name):
    for playlist in database.Playlists:
        if playlist.name == name:
            return playlist


def create_playlist(mountpoint, name):
    with database(mountpoint) as db:
        return find_playlist(db, name) or db.new_Playlist(name)


def populate_ipod_playlist(mountpoint, name, nsongs):
    with database(mountpoint) as db:
        playlist = find_playlist(db, name) or db.new_Playlist(name.encode('utf-8'))
        for n in range(nsongs):
            playlist.add(db[n])


def remove_ipod_playlist(mountpoint, name):
    with database(mountpoint) as db:
        playlist = find_playlist(db, name)
        if playlist:
            db.remove(playlist, quiet=True, ipod=False)


def get_ipod_playlists_by_name(mountpoint):
    db = get_database(mountpoint)
    return {playlist.name: playlist for playlist in db.Playlists}
