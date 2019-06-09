from bs4 import BeautifulSoup as bs
import requests
import sys
import os

amountOfLinks = len(sys.argv)-1
urlCounter = 0
urlList = []

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


def downloadImages(url, urlCounter):
    linkList = []

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
    response = requests.get(url)
    soup = bs(response.text, "html.parser")

    containers = soup.find_all('div', {'class':'card-action'})

    #Checks if there are any images and returns an error if not. Also skipps the url.
    try:
        containers[0]
    except IndexError:
        print("\nCould not find Images. The cause might be a invalid url or there just aren't any Images")
        print("Skipping url: " + url + "\n")
        print("============" + str(urlCounter) + "/" + str(amountOfLinks) + "===============\n")
        return

    #Searches for Image-Boxes.
    for container in containers:
        shortLink = container.a['href']
        linkList.append("https://yiff.party" + shortLink)

    #Loops through the Image Urls amd downloads them.
    for url in linkList:
        imageName = url.split("/")[6]
        #print("Downloading " + name)           #Shows the name of the current downloading image
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(".\\Images\\" + patreonAuthor + "\\" + imageName, 'wb') as f:
                for chunk in r:
                    f.write(chunk)

    #Just a finishing message.
    print("\nSuccessfully downloaded " + str(len(containers)) + " Images!\n")
    print("============" + str(urlCounter) + "/" + str(amountOfLinks) + "===============\n")

#Loops through all Yiff.party-Urls and downloads the images.
for url in urlList:
    urlCounter += 1
    downloadImages(url, urlCounter)