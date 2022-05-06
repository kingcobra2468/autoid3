# AutoID3
AutoID3 is a simple command-line tool which makes use of Shazam to automatically add title, artist,
album, genre, and cover art metadata to supported mp3 tracks.

## Usage
AutoID3 is accessible via the command-line and exposes the flags:
- **-d/--directory=** The mp3 source directory. This flag can be
  repeated 1 or more times in the case where multiple directories
  contain mp3s.
- **-w/--workers=** The number of concurrent workers to process the
  mp3s.
- **-h/--help=** Displays usage of AutoID3.

Example: `python3 autoid3.py -d ~/Music -w 5`

## Installation
To install AutoID3, follow these steps:
1. Ensure Python3.7 in on the system.
2. Install ffmpeg and ffprobe [binaries](https://ffbinaries.com/downloads)
   are installed on the system and are found in `$PATH`. 
3. Install dependencies with `pip3 install -r requirements.txt.
4. AutoID3 is now usable as explained [here](#usage).

## Using AutoID3 Library
AutoID3 can also be utilized as a package in other projects. Simply
install it with: 
```
pip3 install git+https://github.com/kingcobra2468/AutoID3.git
```
Post installation, AutoID3 can be imported as `autoid3`.

### Documentation
Extensive documentation can be found as docstrings throughout
the project.
