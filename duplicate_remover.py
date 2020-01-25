import os
import platform
import hashlib as hl

BLOCKSIZE = 65536
system = platform.system()
if(system == 'Windows'):
    sep = "\\"
else:
    sep = "/"
path = "." + sep + "Images" + sep

folders = os.listdir(path)

print("Removing duplicates...\n")

for folder in folders:
    hashDir = {}
    if os.path.isdir(path + folder):
        files = os.listdir(path + folder + sep)

        
        # MD5 check
        for aFile in files:
            hasher1 = hl.md5()
            fpath = path + folder + sep + aFile

            with open(fpath, 'rb') as afile:
                buf = afile.read(BLOCKSIZE)
                while len(buf) > 0:
                    hasher1.update(buf)
                    buf = afile.read(BLOCKSIZE)
            hashDir[hasher1.hexdigest()] = fpath

        # Removing duplicates
        if len(files) != len(hashDir):
            counter = 0
            for bFile in files:
                foundFlag = False

                fpath = path + folder + sep + bFile

                for key in hashDir:
                    if hashDir[key] == fpath:
                        foundFlag = True
                        break
                if not foundFlag:
                    os.remove(fpath)
                    counter += 1
                    print("{0}: Removed {1} in {2}".format(counter, bFile, folder))
        else:
            print("No duplicates found in {}".format(folder))
