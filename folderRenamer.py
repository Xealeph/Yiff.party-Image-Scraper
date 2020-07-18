from bs4 import BeautifulSoup as bs
import requests
import os
import platform as pf

userAgent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36"

if(pf.system() == 'Windows'):
    dirSep = "\\"
else:
    dirSep = "/"

path = "." + dirSep + "Images" + dirSep

def getName(response, num):
    try:
        soup = bs(response.text, "html.parser")
        name = soup.find('title').text.split("|")[0]
        return name.strip()
    except:
        print("Problem getting the gallary name. Using the gallary number instead.")
        return num

def getGalleryName(gallNum):
    patreonUrl = "https://yiff.party/patreon/" + gallNum
    fantiaUrl = "https://yiff.party/fantia/" + gallNum
    folderName = ""

    patreonResponse = requests.get(patreonUrl, headers = {'User-Agent': userAgent})
    if patreonResponse.status_code == 200:
        folderName = "patreon_" + getName(patreonResponse, gallNum)
    else:
        fantiaResponse = requests.get(fantiaUrl, headers = {'User-Agent': userAgent})
        if fantiaResponse.status_code == 200:
            folderName = "fantia_" + getName(patreonResponse, gallNum)
        else:
            print("Problem getting the gallary platform. Using the gallary number instead.")
            folderName = gallNum
    return folderName

entityList = os.listdir(path)
folderList = []

for entity in entityList:
    if os.path.isdir(path + entity):
        folderList.append(path + entity)

for folder in folderList:
    if folder.split(dirSep)[-1].isdigit():
        newName = getGalleryName(folder.split(dirSep)[-1])
        os.rename(folder,path + newName)
        print("Renamed " + folder.split(dirSep)[-1] + " to " + newName)