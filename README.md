# ipodio: Command line iPod client [![Build Status](https://travis-ci.org/jvrsantacruz/ipodio.png?branch=master)](https://travis-ci.org/jvrsantacruz/ipodio)

Fast and confortable iPod managing for advanced users.

- Easy and powerful regex search
- Advanced repeated tracks detection
- Metadata fixing with regex sustitution
- Repository-like concepts ( *push*, *pull*, ...)

### Planned

- Playlist management (with *m3u* and *xspf* integration)
- iPod checkings and cleanup
- Playcounts management, export and stats
- Extension/Plugins system
- Last.fm scrobbling

## Dependencies

- libgpod
- docopt
- mp3hash

## Install

Install libgpod dependency

```shell
$ sudo apt-get install python-gpod

OR

$ sudo pacman -S libgpod
```

```shell
$ pip install .

(ipodio)$ which ipodio
/usr/bin/ipodio

$ pip uninstall ipodio
```

## Develop

```shell
# install libgpod as before
$ mkvirtualenv ipodio --python python2 --system-site-packages
(ipodio)$ python setup.py develop
(ipodio)$ pip install -r dev-requirements.txt
```

## Lend me a hand!

If you detect error or bugs, feel free to open an issue.

If your aim is to add some extra features to the project, send me a pull request:

1. Fork this project
1. Create a topic branch `git checkout -b myfeature`
1. Work on your feature, one idea per branch
1. Push it to your own topic branch `git push origin myfeature`
1. Send me a *Pull Request*



## Usage

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

```
$ ipodio pull john lennon
Copying 2_Imagine_Working Class Hero_John Lennon.mp3 to /current/directory
Copying 3_Working_Class_Hero_Working Class Hero_John Lennon.mp3 to /current/directory
(..)
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

```
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
```
