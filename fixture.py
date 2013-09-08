#!/usr/bin env python
# -*- coding: utf-8 -*-
"""
Usage:
    fixture <path>
"""

import sys


def bootstrap_ipod(mountpoint):
    import gpod
    gpod.itdb_init_ipod(mountpoint, None, 'my iPod', None)


def main():
    mountpoint = sys.argv[1]
    print('Creating new empty ipod filesystem at {}'.format(mountpoint))
    bootstrap_ipod(mountpoint)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Error: Missing fixture directory')
        print(__doc__)
        sys.exit(1)

    main()
