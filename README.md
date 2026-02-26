# Apple Music Library Analyser
The Apple Music application doesn't show a useful breakdown of your library contents.  They're more interested in pestering you to subscribe and own nuthin'.<br>

## Background
My iTunes library contains over 30,000 files and is over 1TB in size.  It was first created around 2002 on my iMac G4 with iTunes and has moved from Mac to Mac over the decades.<br>

Most of my songs have been ripped from CDs I've bought over the decades ... the first CD I got was, I think, "5 1/2" by Japanese band 米米CLUB (KOME KOME CLUB).<br>

I buy more music online now, mainly from Bandcamp, HD Tracks or Beatport, always in lossless or hi-res formats.  It's nice to have the physical CD but if you can get 48kHz and/or 24-bit/DSD resolution files online then I'll get those.  I've also ripped a bunch of my SACDs (Super Audio CD) as well.<br>

Anyway, here is a Python script that will analyse the files in your library and output a summary.  It can take a while to run as it checks every file: about 13min on my Intel Mac mini (3.2GHz), see example below.<br>

## Requirements
- Python 3
- Mutagen library (install with ```pip install mutagen```
- You need to set the path to your library in the script before running ... it could be almost anywhere these days so simpler if you just set it yourself!

Example file paths:<br>
On my Mac (M2) that came with Music application:<br>
```library_path = "/Users/brett/Music/Music/Media.localized/Music" ```<br>
On my Mac (Intel) that inherited the library I first created on original iMac G4 in 2002-ish:<br>
```library_path = "/Volumes/Hollie Data/Users/brett/Music/iTunes/iTunes Music/Music" ```<br>

## Execution
With you library path set in the script, run the script from wherever with: ```python3 iTunes_Analyser.py```<br>
A "." will be printed for every 100 files processed so you can see that's working.<br>
Any errors will be printed and processing continued.

## Example Output
Here is sample output from a small library on my Macbook Air:
```
% python3 iTunes_Analyser.py

###################################
# Brett's iTunes Library Analyser #
# 26/Feb/2026                     #
###################################

Processing: /Users/brett/Music/Music/Media.localized/Music
...

>> File count:          308
>> File types:
   ALAC                 243
   M4A (AAC)             42
   MP3                   23
>> Bitrates:
   256 kbps:             42
   320 kbps:             23
   321-1411 kbps:       155
   1411 kbps:            13
   1412-2115 kbps:       37
   2116 kbps:            30
   >2116 kbps:            8
>> Sample rates:
   44100 Hz:            298
   48000 Hz:             10
>> Sample size:
   16-bit:              233
   24-bit:               75
>> Types of files:
   Audio:               308
>> Total size: 8.26GB (8457.32MB)
>> Processing time: <1 sec
```
And this is from my 24-year old library (2002-2026):
```
% python3 iTunes_Analyser.py

###################################
# Brett's iTunes Library Analyser #
# 26/Feb/2026                     #
###################################

Processing: /Volumes/Hollie Data/Users/brett/Music/iTunes/iTunes Music/Music
........................................................................................................................................................
!! Skipping metadata for 01 Surface.m4a: not a MP4 file
.................................................................................
!! Skipping metadata for 01 It's Our Future 1.m4a: not a MP4 file
.........................................................................................................
!! Skipping metadata for 04 Right Mind.m4a: Not enough data
..
!! Skipping metadata for _2-12W~1.M4A: 'NoneType' object has no attribute 'info'
..................................
!! Skipping metadata for 01 D21438.m4a: not a MP4 file
......

>> File count:        38070
>> File types:
   AIFF                  18
   ALAC               31352
   M4A (AAC)           3332
   M4V                  472
   MP3                 2527
   MP4                  369
>> Bitrates:
    64 kbps:              9
   128 kbps:            752
   160 kbps:            697
   192 kbps:            988
   256 kbps:           1671
   320 kbps:           1798
   <320 kbps:           703
   321-1411 kbps:     26713
   1411 kbps:          3037
   1412-2115 kbps:      446
   2116 kbps:           278
   >2116 kbps:          946
   Unknown               27
>> Sample rates:
    22050 Hz:             1
    32000 Hz:            13
    44100 Hz:         36322
    48000 Hz:           958
    88200 Hz:            48
    96000 Hz:           521
   192000 Hz:           180
   352800 Hz:            22
>> Sample size:
   16-bit:            36542
   24-bit:             1521
   32-bit:                2
>> Types of files:
   Audio:             37229
   Video:               841
>> Total size: 1031.31GB (1056062.23MB)
>> Processing time: 12 min 24 sec
```
