# Yiff.party-Image-Scraper
### Description

A simple Image Scraper for yiff.party profiles.

### Setup

To ensure that the python modules <b>requests</b> and <b>bs4</b> are on a working version, open a shell and type:<br>
```
pip install -r requirements.txt
```
You will also need Python 3.7.3. (At least that is the version I'm using. Lower Versions might work too.)

### Usage
```
python yiff_image_scraper.py [start page] [last page] [-folders] firstLink secondLink ...
```
Replace <b>firstLink</b>, <b>secondLink</b>, <b>...</b> with your own Links.<br>
Note that every Link after the first one ist optional.

Optional: You can choose at what page the scraper should start and end (Only for the first link!).

Optional: If "-folders" is present, files will be placed in subfolders according to their original Patreon post.

If any links are skipped you can/should find them in <b>SkippedFiles.txt</b>.


There is also an additional script, which removes all files with the same md5-hash.
```
python duplicate_remover.py
```

### Examples
```
python yiff_image_scraper.py https://yiff.party/patreon/42

python yiff_image_scraper.py 2 3 https://yiff.party/patreon/42

python yiff_image_scraper.py 8 8 https://yiff.party/patreon/42
```
### Known Issues
File formats can sometimes be corrupt/invalid (e.g. <b>image.pngformat</b>)<br>
