# ipodio: iPod in the command line 

[![](http://badge.fury.io/py/ipodio.png)](http://badge.fury.io/py/ipodio)
[![](https://travis-ci.org/jvrsantacruz/ipodio.png?branch=master)](https://travis-ci.org/jvrsantacruz/ipodio)
[![](https://pypip.in/d/ipodio/badge.png)](https://crate.io/packages/ipodio?version=latest)

Fast and comfortable iPod managing for advanced users.

- Easy and powerful regex search
- Advanced repeated tracks detection
- Metadata fixing with regex substitution
- Repository-like ( *push*, *pull*, ...)
- Playlist support

### Planned

- Playlist *m3u* and *xspf* integration
- iPod checkings and cleanup
- Playcounts management, export and stats
- Historical of iPod modification operations
- Extension/Plugins system
- Last.fm scrobbling

## Dependencies

- libgpod
- docopt
- mp3hash

## Install

Install libgpod dependency

```shell
$ sudo apt-get install python-gpod // pacman -S libgpod
$ pip install .
```

## Development

```shell
# install libgpod as before
$ virtualenv env --python python2 --system-site-packages
source env/bin/activate
(ipodio)$ python setup.py develop
(ipodio)$ pip install -r dev-requirements.txt
```

To run all the tests:

```shell
$ tox
```

The whole lot of tests can take quite a few seconds. This is because of the integration tests (spec/ui).
To only run unit tests while developing, type:

```shell
(ipodio)$ mamba spec/unit
```

You can have a working ipod filesystem on local just by running:

```shell
$ python fixture.py /path/ipod/fixture
```

Working with a real ipod is both slow and dangerous; besides, it is just a directory convention
along with some files.


## Lend me a hand!

If you detect error or bugs, feel free to open an issue.

If your aim is to add some extra features to the project, send me a pull request:

1. Fork this project
1. Create a topic branch `git checkout -b myfeature`
1. Work on your feature, one idea per branch
1. Push it to your own topic branch `git push origin myfeature`
1. Send me a *Pull Request*


## Usage

```
iPodio

Usage:
  ipodio list   [options] [<expression>...]
  ipodio push   [options] [--force] [--recursive] <filename>...
  ipodio pull   [options] [--dest=<directory>] [--force] [--plain] [<expression>...]
  ipodio rm     [options] <expression>...
  ipodio rename [options] <expression> <replacement>
  ipodio duplicates [options] [<expression>...]
  
  ipodio playlist list [options] [--force] [<name>] [<expression>...]
  ipodio playlist create [options] <name>
  ipodio playlist add [options] <name> <expression>...
  ipodio playlist rm [options] <name> [<expression>...]
  ipodio playlist rename [options] <name> <new_name>


Options:
  -m PATH, --mount PATH  Path to the iPod's mountpoint.
```

The ipod location can be provided via the `--mount` option or by setting `export IPODIO_MOUNTPOINT=/path/to/ipod`.
Examples assume env var present.

### Push files into the ipod

```shell
$ ipodio push Working-Class-Hero.mp3
Sending 1/1: title: Working Class Hero album: Working Class Hero artist: John Lennon
```

```shell
$ ipodio push Albums/John-Lennon/Working-Class-Hero
Not sending "title: Working Class Hero artist: John Lennon" which is already in the ipod
Sending 1/38: title: Imagine album: Working Class Hero artist: John Lennon
(..)
```

### Search and list

List can take any regular expression that [Python understands](http://docs.python.org/dev/howto/regex.html).
Matching is case insensitive by default.

```
$ ipodio list "john(ny)?"
Title                      Album                                       Artist
-----------------------------------------------------------------------------------
Working Class Hero         Working Class Hero (The definitive Lennon)  John Lennon
Imagine                    Working Class Hero (The definitive Lennon)  John Lennon
(..)
Solitary Man               American III                                Johnny Cash
One                        American III                                Johnny Cash
(..)
```

### Renaming

Think of it like a sort of `s/expression/replacement/g`. Case matters here.

```
$ ipodio rename "The definitive (Lennon)" "DEFINITIVE \1"
Title                      Album                                       Artist
-----------------------------------------------------------------------------------
Working Class Hero         Working Class Hero (DEFINITIVE Lennon)      John Lennon
(..)
Rename? [y/n]: n
```

```
$ ipodio rename "\(The definitive Lennon\)" ""
Title                      Album                                       Artist
-----------------------------------------------------------------------------------
Working Class Hero         Working Class Hero                          John Lennon
(..)
Rename? [y/n]: y
```

### Pull songs to the computer

Copies all the files creating a `artist/album/tracks` directory hierarchy.

```
$ ipodio pull john lennon
Copying 2_Imagine_Working Class Hero_John Lennon.mp3 to John Lennon/Working Class Hero
Copying 3_Working_Class_Hero_Working Class Hero_John Lennon.mp3 to John Lennon/Working Class Hero

(..)
```

With `--plain`, all files will be just copied without directories beign created.

```
$ ipodio pull --plain john lennon
Copying 2_Imagine_Working Class Hero_John Lennon.mp3 to /current/directory
```

By default it will refuse to overwrite existing tracks. You can avoid this using the `--force`
option.

```
$ ipodio pull john lennon
Copying 2_Imagine_Working Class Hero_John Lennon.mp3 to John Lennon/Working Class Hero

$ ipodio pull john lennon
Not sending "Imagine by: John Lenon" which is already in the ipod.

$ ipodio pull --force john lennon
Copying 2_Imagine_Working Class Hero_John Lennon.mp3 to John Lennon/Working Class Hero
```

### Remove

```
$ ipodio rm trash
Title                      Album                                       Artist
-----------------------------------------------------------------------------------
Country Trash              American III                                Johnny Cash
Total Trash                Daydream Nation                             Sonic Youth
(..)
Remove? [y/n]: y
```


### Duplicates

List groups duplicated tracks. Comparision is made using the song music content, not the tags.

```
$ ipodio push /home/user/music --force  # repeat songs!
$ ipodio duplicates
Title                      Album                                       Artist
-----------------------------------------------------------------------------------
Country Trash              American III                                Johnny Cash
Country Trash              American III                                Johnny Cash
Total Trash                Daydream Nation                             Sonic Youth
Total Trash                Daydream Nation                             Sonic Youth
```
