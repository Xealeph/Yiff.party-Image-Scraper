from bs4 import BeautifulSoup as bs
import requests
import re
import sys
import os
import platform as pf

amountOfLinks = len(sys.argv)-1
urlCounter = 0
imageCounter = 0
skippedCounter = 0
urlList = []
missingFiles = []
downloadedFiles = []
dlFileList = []
userAgent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36"
dirSep = ""
system = pf.system()
cLastPageFlag = False

if(system == 'Windows'):
    dirSep = "\\"
else:
    dirSep = "/"

print("Please input a path to save your Images in.\nLeave blank for the default path.")
cPath = input().strip()
if cPath is None:
    cPath = '.' + dirSep
elif os.path.isfile(cPath):
    print("The chosen path leads to a file not a folder")
    quit()
elif os.path.isdir(cPath) and cPath[-1] != dirSep:
    cPath += dirSep

print("\n======Starting Scraper========")

for n in range(amountOfLinks):
    urlList.append(sys.argv[n+1])

try:
    startPage = int(sys.argv[1])-1
    urlList.pop(0)
    amountOfLinks -= 1
except:
    startPage = 0

try:
    cLastPage = int(sys.argv[2])
    cLastPageFlag = True
    urlList.pop(0)
    amountOfLinks -= 1
    if cLastPage < startPage:
        sys.exit()
except SystemExit:
    sys.exit("Please choose a lower starting page. Your current pagenumbers are: Starting Page: " + (startPage) + ", Last Page: " + str(cLastPage))
except:
    pass

# Check the arguments for the "-folders" flag. If present, remove it, decrement amountOfLinks, and set useFolders flag
try:
    if ('-folders' in urlList):
        print("Sub folders will be created.\n")
        useFolders = True
        urlList.remove('-folders')
        amountOfLinks -= 1
    else:
        useFolders = False
except:
    useFolders = False

#Checks if there are any links present
if amountOfLinks <= 0:
    print("\nPlease enter at least 1 link as argument.\ne.g. https://yiff.party/patreon/1\n")
    print("============0/0===============\n")
    sys.exit()

#Creates Image Directory
if not os.path.isdir(cPath +"Images"+ dirSep +""):
    os.mkdir(cPath +"Images"+ dirSep +"")

#Creates Database Directory
if not os.path.isdir(cPath +"DB"+ dirSep +""):
    os.mkdir(cPath +"DB"+ dirSep +"")

def getFlag():
    return cLastPageFlag

def setFlag(boolean):
    cLastPageFlag = boolean

def sanitiseFolderName(rawFolderName):
    #First remove all characters that are not alphanumerics or in this list: '_- #!(),.$+
    cleanedFolderName = "".join(x for x in rawFolderName if(x.isalnum() or x in "'_- #!(),.$+"))
    #Then let's remove any preceding or trailing spaces, periods, commas
    cleanedFolderName = cleanedFolderName.strip(' .,')
    #If those steps have trimmed the name down to no characters, add a placeholder
    if (len(cleanedFolderName) < 1):
        cleanedFolderName = "NA" #+ cleanFolderName  <- This seems unnecessary 
    return cleanedFolderName

def accountForDuplicates(aDict):
    counter = 0
    bList = [] 
    cList = []
    newDict = {}
    aDict = sorted(aDict.items(), key=lambda item: item[1])
    #print(aDict)
    for i1 in range(len(aDict)):
        #print(aDict[i1][1])
        bList.append(aDict[i1][1])
    for i2 in range(len(aDict)):
        cList.append(aDict[i2][0])
    bList.append("buffer")
    cList.append("buffer")
    for h in range(len(bList)-1):
        if bList[h] == bList[h+1]:
            #print(bList[h])
            #updatedItem = {cList[h]:}
            newDict[cList[h]] = (str(counter) + " " + bList[h])
            counter += 1
        else:
            newDict[cList[h]] = bList[h]
    return newDict
        

def makeConformUrl(aList):
    for k in range(len(aList)-1):
        if(str(aList[k]).startswith("/")):
            aList[k] = "https://yiff.party" + str(aList[k])
    return aList

def downloader(myUrl, myImageName, myGalleryAuthor, postFolderName): #recursively tries to download the images - in the case of the site not accepting anymore requests
    global imageCounter
    global skippedCounter
    global downloadedFiles
    global dlFileList
    try:
        r = requests.get(myUrl, headers = {'User-Agent': userAgent}, timeout=(30,30), stream=True)
        if r.status_code == 200:
            #If we were passed a valid folder name, use it to make a folder for the post
            if (postFolderName != False):
                # If the file doesn't already exist, download it!
                #if not os.path.isfile(cPath + "Images" + dirSep + myGalleryAuthor + dirSep + postFolderName+ dirSep + myImageName):
                if not myImageName in dlFileList:
                    # If the folder does not already exist, make it!
                    if not os.path.isdir(cPath + "Images" + dirSep + myGalleryAuthor + dirSep + postFolderName + dirSep + ""):
                        os.mkdir(cPath + "Images" + dirSep + myGalleryAuthor + dirSep + postFolderName+ dirSep + "")

                    with open(cPath + "Images" + dirSep + myGalleryAuthor + dirSep + postFolderName+ dirSep + myImageName, 'wb') as f:
                        for chunk in r:
                            f.write(chunk)
                    imageCounter += 1
                    downloadedFiles.append(myImageName)
                else:
                    print(">Skipped, already exists!")
                    skippedCounter += 1
            #IF we were passed 'FALSE' instead of a folder name, do not create a folder, but simply save in Author page
            else:
                # If the file doesn't already exist, download it!
                #if not os.path.isfile(cPath + "Images" + dirSep + myGalleryAuthor + dirSep + myImageName):
                if not myImageName in dlFileList:
                    with open(cPath + "Images" + dirSep + myGalleryAuthor + dirSep + myImageName, 'wb') as f:
                        for chunk in r:
                            f.write(chunk)
                    imageCounter += 1
                    downloadedFiles.append(myImageName)
                else:
                    print(">Skipped, already exists!")
                    skippedCounter += 1
        else:
            # If we get a bad response, let the user know what it was
            print(">Skipped ["+myUrl+"]:\n>"+"(Error: Bad Response- " + str(r.status_code) + ")")
    except Exception as errorCode:
        #If we failed out of the download entirely, show the user the exception code
        print(">Skipped ["+myUrl+"]:\n>"+"(Error: " + str(errorCode) + ")")
        missingFiles.append(myUrl)
        return

#short function to get the video link from a link with embedded video like https://yiff.party/vimeo/1
def getEmbeddedVideos(url): #Only tested with Vimeo Videos so far and also not working
    #print("embed found with url " + url) 
    url = "https://yiff.party/vimeo_embed?v=" + str(url).split("/")[-1]
    response = requests.get(url, headers = {'User-Agent': userAgent})
    regex = r'("url":"[^,]*\.mp4",)'
    tempLink = str(re.findall(regex, response.text)[0])
    link = tempLink.split("\"")[3]
    return link

def fantiaSubroutine(postList):
    linklist = []
    for postUrl in postList:
        response = requests.get(postUrl, headers = {'User-Agent': userAgent})
        soup = bs(response.text, "html.parser")
        
        try:
            var = soup.find('div', {'class':'col s12 l9'})
            linklist.append(var.a['href'])
            var2 = var.find_all('div', {'class':'yp-post-content'})
            for img in var2:
                try:
                    linklist.append(img.a['href'])
                    continue
                except:
                    pass
                try:
                    imglist = img.find_all('div', {'class': 'ccol s12 m6'})
                    for img in imglist:
                        linklist.append(img.a['src'])
                except:
                    pass
        except TypeError:
            pass
    return linklist

def getGalleryName(gallUrl, gallNum):
    try:
        response = requests.get(gallUrl, headers = {'User-Agent': userAgent})
        soup = bs(response.text, "html.parser")

        name = soup.find('title').text.split("|")[0]
        return name.strip()
    except:
        print("Problem getting the authors name. Using the authors number instead.")
        return gallNum

def downloadImages(url, urlCounter, useFolders):
    imageNameDict = {}
    postDateTitleDict = {}
    postNumberDict = {}
    linkList = []
    imgContainerUrls = []
    embeddedVideos = []
    global imageCounter
    imageCounter = 0
    global downloadedFiles
    downloadedFiles.clear()
    global dlFileList

    #Gets the Gallery Author's number. Fails if link is shorter than https://yiff.party/patreon/1.
    #Also Creates a directory for the images.
    try:    
        galleryNumber = url.split("/")[4]
        platform = url.split("/")[3]
        galleryAuthor = platform + "_" + getGalleryName(url, galleryNumber)
    except IndexError:
        print("\nThe given url might not be valid.\nSkipping url: " + url + "\n")
        print("============" + str(urlCounter) + "/" + str(amountOfLinks) + "===============\n")
        return
    else:
        if not os.path.isdir(cPath + "Images" + dirSep + galleryAuthor + dirSep):
            os.mkdir(cPath + "Images" + dirSep + galleryAuthor + dirSep)
    
    #Gets the page and converts/reads it.
    response = requests.get(url, headers = {'User-Agent': userAgent})
    soup = bs(response.text, "html.parser")

    newUrl = "https://yiff.party/render_posts?s=" + platform + "&c=" + galleryNumber + "&p="

    #searches for the highest page number
    lastPage = soup.find_all('a', {'class':'btn pag-btn'})
    

    try: 
        lastPage = int(lastPage[1]["data-pag"])
        cLPFlag = getFlag()
        if cLPFlag:
            if cLastPage > lastPage:
                sys.exit()
            lastPage = cLastPage
            startPage = startPage
            setFlag(False)
        else:
            startPage = 0
        for i in range(startPage, lastPage):
            imgContainerUrls.append(newUrl + str(i+1)) #appends the page number to the url
    except SystemExit:
        sys.exit("Last Page Number is too high. Please choose a number lower or equal than: " + str(lastPage))
    except:
        lastPage = 1
        imgContainerUrls.append(newUrl + str(1))
    
    potOfAllSoup = ""
    for containerUrl in imgContainerUrls:

        response = requests.get(containerUrl, headers = {'User-Agent': userAgent})
        soup = bs(response.text, "html.parser")
        potOfAllSoup = potOfAllSoup + response.text

        if platform == 'fantia':
            fantiaList = []
            containersFantia = soup.find_all('div', {'class': 'col s12 m6'})
            for cont in containersFantia:
                fantiaList.append("https://yiff.party" + cont.a['href'].strip())
            linkList += fantiaSubroutine(fantiaList)
            continue

        containersPart1 = soup.find_all('div', {'class': 'card-action'})
        containersPart2 = soup.find_all('div', {'class': 'post-body'})
        containersPart3 = soup.find_all('img', {'class': 'lazyload'})
        containersPart4 = soup.find_all('p', {'class': 'yp-vimeo-proxy-embed'})
        containersPart5 = soup.find_all('div', {'class': 'card-attachments'})

        containers = containersPart1 + containersPart2 + containersPart3 + containersPart4 + containersPart5

        #Checks if there are any images and returns an error if not. Also skips the url.
        try:
            containers[0]
        except IndexError:
            page = containerUrl.split("p=")[1]
            print("\nCould not find Images. The cause might be a invalid url or there just aren't any Images.")
            missingFiles.append("Page " + page + " was skipped. You can retry scraping this page with: python " + sys.argv[0] + " " + page + " " + page + " urls")
            #print("Skipping url: " + url + "\n")
            #print("============" + str(urlCounter) + "/" + str(amountOfLinks) + "===============\n")
            continue
 
        containerCounter1 = len(containersPart1) #amount of containers with class 'card-action'
        containerCounter2 = len(containersPart2) #amount of containers with class 'post-body'
        containerCounter3 = len(containersPart3) #amount of containers with class 'lazyload'
        containerCounter4 = len(containersPart4) #amount of containers with class 'card-embed'
        i = 0 
        

        #Searches for Image-Boxes.
        for container in containers:
            shortLink = ""
            i += 1
            if i <= containerCounter1:
                try:
                    shortLink = container.a['href']
                except:
                    continue
            elif i <= containerCounter2 and i > containerCounter1:
                try:
                    subContainer = container.find_all('a')
                    for subCont in subContainer:
                        linkList.append(subCont['href'])
                except:
                    continue
            elif i <= containerCounter3 and i > containerCounter2:
                try:
                    shortLink = container['data-src'].split("&w=")[0]
                    shortLink = "https://" + shortLink.split("ssl:")[1]
                except:
                    continue
            elif i <= containerCounter4 and i > containerCounter3:
                try:
                    embeddedVideos.append(container.a['href'])
                except:
                    continue
            else:
                try:
                    subContainer = container.p
                    subContainer = subContainer.find_all('a')
                    for subCont in subContainer:
                        linkList.append(subCont['href'])
                except:
                    continue

            linkList.append(shortLink)
    
    linkList = makeConformUrl(sorted(linkList))
    linkList = list(dict.fromkeys(linkList))

    #Hardcoded way of filtering 3rdParty Links
    thirdPartyLinks = []
    for entity in linkList:
        if not str(entity).startswith(("https://data.yiff.party", "https://yiff.party")):
            thirdPartyLinks.append(entity)
            linkList.remove(entity)

    #print(embeddedVideos)
    for videoLink in embeddedVideos:   #loop to get the video link of the embedded videos
        try:
            linkList.append(getEmbeddedVideos(videoLink))
            #removes embedded links it could find
            embeddedVideos.remove(videoLink)    
        except:
            pass
    #print(embeddedVideos)

    #embedded video links that couldnt be found get appended to the 3rd party textfile
    thirdPartyLinks.append("\nEmbedded Video Links:")
    thirdPartyLinks += embeddedVideos

    #Saves the 3rdParty Links to a respective File in the folder of the author
    f = open(cPath + "Images" + dirSep + galleryAuthor + dirSep + "3rdPartyLinks.txt", "w+")
    for link in thirdPartyLinks:
        f.write(str(link) + "\n")
    f.close()  

    #Creates or checks for a 'db' file
    if not os.path.isfile("." + dirSep + "DB" + dirSep + galleryNumber + ".txt"):
        f = open("." + dirSep + "DB" + dirSep + galleryNumber + ".txt", 'w', encoding='utf-8')
        f.writelines(galleryAuthor + '\n;')
        f.close()
    f = open("." + dirSep + "DB" + dirSep + galleryNumber + ".txt", 'r', encoding='utf-8')
    dlFileList = f.read()#.split(';')[1:]
    f.close()

    for h in range(0, len(linkList)-1):
        updatedValue = {str(h):str(linkList[h].split("/")[len(linkList[h].split("/"))-1])}
        imageNameDict.update(updatedValue)

    imageNameDict = accountForDuplicates(imageNameDict)

    #print(len(linkList))
    #print(imageNameDict)
    #print(imageCounter)
    #print('\n'.join(map(str, sorted(linkList))))
    #quit()

    if useFolders:
        #Fetches appropriate DATE and TITLE for each URL in link list via Beautiful Soup
        #falls back on the post number provided by yiff.party if no appropriate title+date can be found
        allSoup = bs(potOfAllSoup, "html.parser")
        for h in range(0, len(linkList)-1):
            # Grab the post number (this is yiff.party's numbering, not patreon's)
            # May fail if the URL is not a media URL, in that case use the current loop number- this URL won't be downloaded anyway
            try:
                postNumber = {str(h):str(linkList[h].split("/")[5])}
            except:
                postNumber = {str(h):str(h).zfill(8)}
            
            try:
                #Find the location in the soup where the URL in question is located
                location = allSoup.find("a",href=linkList[h].replace("https://yiff.party",""))
                #Search for the part of the post immediately above it that is a span with the 'post-time' class
                timeStamp = location.find_previous("span","grey-text post-time").contents
                trimmedTimeStamp = ''.join(timeStamp).split("T")[0]
                
                #Search for the part of the post immediately above it that is a span with the 'card-title activator grey-text text-darken-4' class
                postName = location.find_previous("span","card-title activator grey-text text-darken-4").contents
                #Split out the post title and Remove any characters that would be illegal file names
                CleanedPostName = sanitiseFolderName(''.join(postName[0]))
                
                dateTitle = {str(h):(trimmedTimeStamp + " " + CleanedPostName)}
            #If we can't find a nice post name and date for whatever reason, fail to using the yiff-provided post number
            except:
                dateTitle = postNumber

            postDateTitleDict.update(dateTitle)

    print("Starting download of " + str(len(linkList)-1) + " items.")
    #Loops through the Image Urls and downloads them.
    try:
        for i in range(len(linkList)-1):
            if useFolders:
                postFolderName = postDateTitleDict[str(i)]
            else:
                postFolderName = False

            imageName = imageNameDict[str(i)]
            urlI = linkList[i]
            print("Downloading " + imageName)           #Shows the name of the current downloading image
            downloader(urlI, imageName, galleryAuthor, postFolderName)

    except KeyboardInterrupt:
        f = open("." + dirSep + "DB" + dirSep + galleryNumber + ".txt", 'a+')
        f.write(';'.join(downloadedFiles))
        f.close()
        missingFiles.append(linkList[i:-1])
        f = open(cPath + "Images" + dirSep + galleryAuthor + dirSep + "SkippedLinks.txt", "w+")
        for files in missingFiles:
            f.write(str(files) + "\n")
        f.close()
        print("\nSuccessfully skipped " + str(len(missingFiles)) + " existing Images/Files!\n")
        print("Successfully downloaded " + str(imageCounter) + " new Images/Files!\n")
        print("============" + str(urlCounter) + "/" + str(amountOfLinks) + "===============\n")
        quit()

    f = open("." + dirSep + "DB" + dirSep + galleryNumber + ".txt", 'a+')
    f.write(';'.join(downloadedFiles))
    f.close()

    #Just a finishing message.
    if (imageCounter == 0) and (skippedCounter == 0):
        print("No files downloaded, and no existing files skipped. Maybe there are no files or you messed up the order of the arguments: python " + sys.argv[0] + " [start page] [last page] urls")
    else:
        print("\nSuccessfully skipped " + str(skippedCounter) + " existing Images/Files!\n")
        print("Successfully downloaded " + str(imageCounter) + " new Images/Files!\n")
        print("============" + str(urlCounter) + "/" + str(amountOfLinks) + "===============\n")

    f = open(cPath + "Images" + dirSep + galleryAuthor + dirSep + "SkippedLinks.txt", "w+")
    for files in missingFiles:
        f.write(str(files) + "\n")
    f.close()


#Loops through all Yiff.party-Urls and downloads the images.
for url in urlList:
    urlCounter += 1
    downloadImages(url, urlCounter, useFolders)
