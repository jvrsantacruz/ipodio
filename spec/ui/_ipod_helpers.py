# -*- coding: utf-8 -*-

from contextlib import contextmanager

import gpod


@contextmanager
def database(mountpoint):
    db = gpod.Database(mountpoint)
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
