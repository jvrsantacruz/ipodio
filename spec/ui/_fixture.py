# -*- coding: utf-8 -*-

import os
import shutil

from scripttest import TestFileEnvironment


def update_environment(_):
    _.bad_expression = '?'
    _.expression = 'richard stallman'

    _.env_path = '/tmp/testing-sandbox'
    _.env = TestFileEnvironment(_.env_path)

    _.fixtures = 'fixtures'
    _.fixtures_path = '/tmp/ipodio_fixtures'

    if not os.path.isdir(_.fixtures_path):
        shutil.copytree(_.fixtures, _.fixtures_path)

    _.songs = ['fixtures/song1.mp3', 'fixtures/song2.mp3']
    _.song_paths = [os.path.abspath(song) for song in _.songs]

    _.mountpoint = 'ipod'
    _.mountpoint_path = os.path.join(_.env_path, _.mountpoint)
    _.cmd = ['ipodio', '--mount', _.mountpoint]
