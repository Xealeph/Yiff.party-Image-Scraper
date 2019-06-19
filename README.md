# Yiff.party-Image-Scraper
### Description

A simple Image Scraper for yiff.party profiles.

### Setup

To ensure that the python modules <b>requests</b> and <b>bs4</b> are on a working version, open a shell and type:<br>
```
pip install -r requirements.txt
```
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

### Issues
If you run into issues with files, which have a duplicate filename, to not be downloaded/ saved, you may want to use <b><i>yiff_image_scraper_duplicateFix.py</b></i> instead of the usual <b><i>yiff_image_scraper.py</b></i>.

Please note, that, because of the additional (and not quite efficient) code to check for duplicates, the script might run slower and eat more of your computer's resources.

If you can improve the code, feel free to do so.
