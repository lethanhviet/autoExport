autoExport
=========

This simple script is for automove torrent(s) from Deluge to rTorrent at set interval with cron.

It's more of a personal project, hence use it at your own risk.

## Requirements:

* Python 2
* Deluge
* rTorrent
* •rtorrent_fast_resume.pl script for fast resume any downloaded torrent for rTorrent
* •perl's module Convert::Bencode which is needed for rtorrent_fast_resume.pl

## Instructions

1. Install perl module Convert::Bencode:

```bash
perl -MCPAN -e 'install Convert::Bencode'
```

2. Edit autoExport.py and change all the information on the "Customize" section according to your own setup.

3. The script can be executed mannually or automatic at set interval by adding it to crontab. To execute automatically, add below line to crontab:

`0 */6 * * * python ~/link/to/folder/autoExport.py`

This means that the script will be executed at 6:00, 12:00, 18:00 & 24:00 (6-hour interval). Change it to fit your own need.

## Notes

1. This script only checks the seeding time before export the torrent to rTorrent. You can also combine in the current upload rate, ratio... for more complex check. Again, pls customize it to fit your own need.