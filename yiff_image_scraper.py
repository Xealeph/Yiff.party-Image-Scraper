from bs4 import BeautifulSoup as bs
import requests
import sys
import os
import platform

amountOfLinks = len(sys.argv)-1
urlCounter = 0
imageCounter = 0
urlList = []
missingFiles = []
userAgent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36"
dirSep = ""
system = platform.system()
cLastPageFlag = False

if(system == 'Windows'):
    dirSep = "\\"
else:
    dirSep = "/"

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
if not os.path.isdir("."+ dirSep +"Images"+ dirSep +""):
    os.mkdir("."+ dirSep +"Images"+ dirSep +"")


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
        cleanedFolderName = "NA" + cleanFolderName
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


def downloader(myUrl, myImageName, myPatreonAuthor, postFolderName): #recursively tries to download the images - in the case of the site not accepting anymore requests
    global imageCounter
    try:
        r = requests.get(myUrl, headers = {'User-Agent': userAgent}, timeout=(3,6), stream=True)
        if r.status_code == 200:
            #If we were passed a valid folder name, use it to make a folder for the post
            if (postFolderName != False):
                if not os.path.isdir("."+ dirSep +"Images"+ dirSep +"" + myPatreonAuthor + ""+ dirSep +""+ postFolderName+ ""+ dirSep +""):
                    os.mkdir("."+ dirSep +"Images"+ dirSep +"" + myPatreonAuthor + ""+ dirSep +""+ postFolderName+ ""+ dirSep +"")
                with open("."+ dirSep +"Images"+ dirSep +"" + myPatreonAuthor + ""+ dirSep +""+ postFolderName+ ""+ dirSep +"" + myImageName, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
            #IF we were passed 'FALSE' instead of a folder name, do not create a folder, but simply save in Author page
            else:
                with open("."+ dirSep +"Images"+ dirSep +"" + myPatreonAuthor + ""+ dirSep +"" + myImageName, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
            imageCounter += 1
        else:
            print(">Skipped (Bad Response: " + str(r.status_code) + "): " + myUrl)
    except:
        print(">Skipped (Other Error): " + myUrl)
        if postFolderName:
            missingFiles.append(myUrl + ' ' + postFolderName)
        else:
            missingFiles.append(myUrl)
        return


def downloadImages(url, urlCounter, useFolders):
    imageNameDict = {}
    postDateTitleDict = {}
    postNumberDict = {}
    linkList = []
    imgContainerUrls = []
    global imageCounter
    imageCounter = 0

    #Gets the Patreon Author's number. Fails if link is shorter than https://yiff.party/patreon/1.
    #Also Creates a directory for the images.
    try:    
        patreonAuthor = url.split("/")[4]
    except IndexError:
        print("\nThe given url might not be valid.\nSkipping url: " + url + "\n")
        print("============" + str(urlCounter) + "/" + str(amountOfLinks) + "===============\n")
        return
    else:
        if not os.path.isdir("."+ dirSep +"Images"+ dirSep +"" + patreonAuthor + ""+ dirSep +""):
            os.mkdir("."+ dirSep +"Images"+ dirSep +"" + patreonAuthor + ""+ dirSep +"")
    
    #Gets the page and converts/reads it.
    response = requests.get(url, headers = {'User-Agent': userAgent})
    soup = bs(response.text, "html.parser")

    newUrl = "https://yiff.party/render_posts?s=patreon&c=" + patreonAuthor + "&p="

    #searches for the highest page number
    lastPage = soup.find_all('a', {'class':'btn pag-btn'})
    

    try: 
        lastPage = int(lastPage[1]["data-pag"])
        #print(lastPage)
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
    #print(imgContainerUrls)
    
    potOfAllSoup = ""
    for containerUrl in imgContainerUrls:
        #print(containerUrl)
        response = requests.get(containerUrl, headers = {'User-Agent': userAgent})
        soup = bs(response.text, "html.parser")
        potOfAllSoup = potOfAllSoup + response.text

        containersPart1 = soup.find_all('div', {'class': 'card-action'})
        containersPart2 = soup.find_all('div', {'class': 'post-body'})
        containersPart3 = soup.find_all('div', {'class': 'card-attachments'})

        containers = containersPart1 + containersPart2 + containersPart3

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
        i = 0 
 
        #Searches for Image-Boxes.
        for container in containers:
            i += 1
            if i <= containerCounter1:
                try:
                    shortLink = container.a['href']
                except:
                    continue
            elif i <= containerCounter2 and i > containerCounter1:
                try:
                    shortLink = container.p.a['href']
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

    for h in range(0, len(linkList)-1):
        updatedValue = {str(h):str(linkList[h].split("/")[len(linkList[h].split("/"))-1])}
        imageNameDict.update(updatedValue)

    imageNameDict = accountForDuplicates(imageNameDict)
    #print(len(linkList))
    #print(imageNameDict)
    #print(imageCounter)
    #print('\n'.join(map(str, sorted(linkList))))

    if useFolders:
        #Fetches appropriate DATE and TITLE for each URL in link list via Beautiful Soup
        #falls back on the post number provided by yiff.party if no appropriate title+date can be found
        allSoup = bs(potOfAllSoup, "html.parser")
        for h in range(0, len(linkList)-1):
            # Grab the post number (this is yiff.party's numbering, not patreon's)
            # May fail if the URL is not a media URL, in that case use the current loop number- this URL will likely get skipped
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

    print("Starting download of " + str(len(linkList)) + " items.")
    #Loops through the Image Urls and downloads them.
    for i in range(len(linkList)-1):
        if useFolders:
            postFolderName = postDateTitleDict[str(i)]
        else:
            postFolderName = False
        
        imageName = imageNameDict[str(i)]
        urlI = linkList[i]
        print("Downloading " + imageName)           #Shows the name of the current downloading image
        downloader(urlI, imageName, patreonAuthor, postFolderName)

    #Just a finishing message.
    if imageCounter == 0:
        print("No files downloaded. Maybe there are no files or you messed up the order of the arguments: python " + sys.argv[0] + " [start page] [last page] urls")
    else:
        print("\nSuccessfully downloaded " + str(imageCounter) + " Images/Files!\n")
        print("============" + str(urlCounter) + "/" + str(amountOfLinks) + "===============\n")

    f = open("SkippedLinks.txt", "w+")
    for files in missingFiles:
        f.write(files + "\n")
    f.close()


#Loops through all Yiff.party-Urls and downloads the images.
for url in urlList:
    urlCounter += 1
    downloadImages(url, urlCounter, useFolders)
