from bs4 import BeautifulSoup as bs
import requests
import sys
import os

amountOfLinks = len(sys.argv)-1
urlCounter = 0
urlList = []
userAgent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36"

print("\n======Starting Scraper========")

#Checks if there are links present and puts then in a list if they are
if amountOfLinks <= 0:
    print("\nPlease enter at least 1 link as argument.\ne.g. https://yiff.party/patreon/1\n")
    print("============0/0===============\n")
    quit()
for n in range(amountOfLinks):
    urlList.append(sys.argv[n+1])

#Creates Image Directory
if not os.path.isdir(".\\Images\\"):
    os.mkdir(".\\Images\\")


def accountForDuplicates(bList):
    counter = 0
    for h in range(len(bList)-2):
        if bList[h] == bList[h+1]:
            bList[h] = str(counter) + " " + bList[h]
            counter += 1
    return bList
        

def makeConformUrl(aList):
    for k in range(len(aList)-1):
        if(str(aList[k]).startswith("/")):
            aList[k] = "https://yiff.party" + str(aList[k])
    return aList


def persistentDownloader(myUrl, myImageName, myPatreonAuthor): #recursively tries to download the images - in the case of the site not accepting anymore requests
    try:
        r = requests.get(myUrl, headers = {'User-Agent': userAgent}, timeout=(2,5), stream=True)
        if r.status_code == 200:
            with open(".\\Images\\" + myPatreonAuthor + "\\" + myImageName, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
        else:
            print("beep -- file skipped: " + myUrl)
    except:
        print("Skipped " + myUrl)
        return


def downloadImages(url, urlCounter):
    linkList = []
    imageNameList = []
    imgContainerUrls = []
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
        if not os.path.isdir(".\\Images\\" + patreonAuthor + "\\"):
            os.mkdir(".\\Images\\" + patreonAuthor + "\\")
    
    #Gets the page and converts/reads it.
    response = requests.get(url, headers = {'User-Agent': userAgent})
    soup = bs(response.text, "html.parser")

    newUrl = "https://yiff.party/render_posts?s=patreon&c=" + patreonAuthor + "&p="

    #searches for the highest page number
    lastPage = soup.find_all('a', {'class':'btn pag-btn'})
    
    try: 
        lastPage = int(lastPage[(len(lastPage)/2)-1]["data-pag"])

        for i in range(0, lastPage-1):
            imgContainerUrls.append(newUrl + str(i+1)) #appends the page number to the url
    except:
        lastPage = 1
        imgContainerUrls.append(newUrl + str(1))
    
    for containerUrl in imgContainerUrls:
        response = requests.get(containerUrl, headers = {'User-Agent': userAgent})
        soup = bs(response.text, "html.parser")

        containersPart1 = soup.find_all('div', {'class': 'card-action'})
        containersPart2 = soup.find_all('div', {'class': 'post-body'})
        containersPart3 = soup.find_all('div', {'class': 'card-attachments'})

        containers = containersPart1 + containersPart2 + containersPart3

        #Checks if there are any images and returns an error if not. Also skips the url.
        try:
            containers[0]
        except IndexError:
            print("\nCould not find Images. The cause might be a invalid url or there just aren't any Images")
            print("Skipping url: " + url + "\n")
            print("============" + str(urlCounter) + "/" + str(amountOfLinks) + "===============\n")
            return
 
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
        imageCounter += len(linkList)

        for h in range(len(linkList)-1):
            imageNameList.append(linkList[h].split("/")[len(linkList[h].split("/"))-1])
        imageNameList = accountForDuplicates(sorted(imageNameList))

        #print(imageCounter)
        #print('\n'.join(map(str, sorted(linkList))))

        #Loops through the Image Urls amd downloads them.
        for i in range(len(linkList)-1):

            imageName = imageNameList[i]
            urlI = linkList[i]

            print("Downloading " + imageName)           #Shows the name of the current downloading image
            persistentDownloader(urlI, imageName, patreonAuthor)

    #Just a finishing message.
    print("\nSuccessfully downloaded " + str(imageCounter) + " Images!\n")
    print("============" + str(urlCounter) + "/" + str(amountOfLinks) + "===============\n")


#Loops through all Yiff.party-Urls and downloads the images.
for url in urlList:
    urlCounter += 1
    downloadImages(url, urlCounter)
