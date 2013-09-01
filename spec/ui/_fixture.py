# -*- coding: utf-8 -*-

import os

from scripttest import TestFileEnvironment


def update_environment(_):
    _.bad_expression = '?'
    _.expression = 'richard stall'

    _.env_path = 'testing-sandbox'
    _.env = TestFileEnvironment(_.env_path)

    _.fixtures = 'fixtures'
    _.fixtures_path = '../fixtures'

    _.songs = ['fixtures/song1.mp3', 'fixtures/song2.mp3']
    _.song_paths = [os.path.join('..', song) for song in _.songs]

    _.mountpoint = 'ipod'
    _.mountpoint_path = os.path.join(_.env_path, _.mountpoint)
    _.cmd = ['ipodio', '--mount', _.mountpoint]
