# Yiff.party-Image-Scraper
### Description

A simple Image Scraper for yiff.party profiles.

### Setup

To ensure that the python modules <b>requests</b> and <b>bs4</b> are on a working version, open a shell and type:<br>
```
pip install -r requirements.txt
```
You will also need at least Python 3.7.3.

### Usage
```
python yiff_image_scraper.py firstLink secondLink ...
```
Replace <b><i>firstLink</i></b>, <b><i>secondLink</i></b>, <b><i>...</b></i> with your own Links.<br>
Note that every Link after the first one ist optional.

### Example
```
python yiff_image_scraper.py https://yiff.party/patreon/42
```
### Known Issues
File formats can sometimes be corrupt/invalid (e.g. image.pngformat)<br>
