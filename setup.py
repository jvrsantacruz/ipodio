# -*- coding: utf-8 -*-

import ipodio
from setuptools import setup, find_packages


setup(
    name='ipodio',
    version=ipodio.__version__,
    description='iPod command line managing tool',
    author='Javier Santacruz',
    author_email='javier.santacruz.lc@gmail.com',
    url='https://github.com/jvrsantacruz/ipodio',
    packages=find_packages(exclude=['spec', 'spec.*']),
    install_requires=[
        'docopt',
        'mp3hash'
    ],
    classifiers=[
        'Environment :: Console',
        'Operating System :: POSIX',
        'Development Status :: 3 - Alpha',
        'Topic :: Multimedia :: Sound/Audio',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    platforms=['Unix'],
    entry_points={
        'console_scripts': ['ipodio = ipodio.cli:main']
    }
)
