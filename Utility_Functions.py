# Utility Functions

def sortFolderFiles(itemsList):
    l1 = []
    l2 = []
    for x in itemsList:
        if x['mimeType'] == 'application/vnd.google-apps.folder':
            l1.append(x)
        else:
            l2.append(x)
    return l1+l2 

def sortFileName(itemsList):
    return sorted(itemsList, key=lambda x: x['name']) 

def progressPercentage(progress):
    return int(progress*100)

def sizeScaler(size): # size in bytes
    ret = ""
    if size <= 100: # bytes
        ret = "["+str(size)+" bytes]" 
    elif size > 100 and size <= 100000: # Kilobytes
        ret = "["+str(round((size/1024),2))+" KB]"
    elif size > 100000 and size <= 1000000000:
        ret = "["+str(round(size/pow(1024,2),2))+" MB]" #Megabytes
    elif size > 1000000000:
        ret = "["+str(round(size/pow(1024,3),2))+" GB]" # Gigabytes
    return ret
