############################################################################################################################################################################################################################################################################################
#Imports

import os
import io
import socket
from time import sleep
import traceback
from progress.bar import Bar
from googleapiclient.http import MediaIoBaseDownload
from datetime import datetime as dt

from Colors import COLORS
from Authentication import Create_Service
from Utility_Functions import sizeScaler, sortFileName, sortFolderFiles, progressPercentage
from Install_requirements import install_requirements


############################################################################################################################################################################################################################################################################################
# Generating Client_Secret file, pickle and Creating Service

service = Create_Service()

############################################################################################################################################################################################################################################################################################
# Global Variables

parentDownloadDirectory = os.getcwd()
totalNumberOfFiles = 0
totalSize = 0
currentFileNumber = 0

# ############################################################################################################################################################################################################################################################################################
# Download Functions


def currentDirectoryLister(folder_id):
    query = f"'{folder_id}' in parents"
    response = service.files().list(q=query, includeItemsFromAllDrives=True, supportsAllDrives=True, corpora='allDrives').execute()
    itemsList = response.get('files')
    nextPageToken = response.get('nextPageToken')
    while nextPageToken:
        response = service.files().list(q=query, pageToken=nextPageToken, includeItemsFromAllDrives=True, supportsAllDrives=True, corpora='allDrives').execute()
        itemsList.extend(response.get('files'))
        nextPageToken = response.get('nextPageToken')
    return itemsList


def numberAndSizeOfOfFilesRecursive(id): 
    global totalNumberOfFiles
    global totalSize
    itemsList = currentDirectoryLister(id)
    if itemsList is not None or len(itemsList) != 0:
        itemsList = sortFolderFiles(itemsList)
        for current in itemsList:
            if current['mimeType'] == 'application/vnd.google-apps.folder':
                numberAndSizeOfOfFilesRecursive(current['id'])
                
            elif current['mimeType'] != 'application/vnd.google-apps.folder': 
                totalNumberOfFiles += 1
                try:
                    totalSize += int(service.files().get(fileId=current['id'], supportsAllDrives=True, fields='name,mimeType,size,modifiedTime').execute()['size'])
                except:
                    print("Size Error")

                
def downloadFile(file_id, path, size):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh, request=request)
    done = False
    bar = None
    p1 = p2 = 0
    bar = Bar(max=100, fill='▇', suffix='%(percent)d%%')
    print(f"\n[{currentFileNumber}/{totalNumberOfFiles}]", " Downloading:",service.files().get(fileId=file_id, supportsAllDrives=True).execute()['name'], sizeScaler(size))
    while not done:
        try:
            status, done = downloader.next_chunk()
            p2 = progressPercentage(status.progress())
            for x in range(p1,p2):
                sleep(0.005)
                bar.next()
            p1 = p2
            
        except socket.timeout:
            print("\nRetrying(socket.timeout)...")
            pass
        except:
            traceback.print_exc()
            exit()
    bar.finish()
    fh.seek(0)

    with open(os.path.join(path, service.files().get(fileId=file_id, supportsAllDrives=True).execute()['name']), 'wb') as f:
        f.write(fh.read())
        f.close()


def downloadFolderRecursive(id): 
    global currentFileNumber
    itemsList = currentDirectoryLister(id)
    if itemsList is not None or len(itemsList) != 0:
        itemsList = sortFileName(itemsList)
        itemsList = sortFolderFiles(itemsList)
        for current in itemsList:
            path = ""
            if current['mimeType'] == 'application/vnd.google-apps.folder':
                folderName = current['name']
                path = os.path.join(os.getcwd(), folderName)
                print("\n\n\nFolder:", (path.replace(parentDownloadDirectory,'')).replace(os.sep,' > ')[2:])
                if not os.path.isdir(path):
                    os.makedirs(path)
                os.chdir(path)
                downloadFolderRecursive(current['id'])
                folderName = current['name']
                print("\n\n\nFolder:", folderName)
                os.chdir('..')
                path = os.getcwd()

            elif current['mimeType'] != 'application/vnd.google-apps.folder': 
                currentFileNumber += 1
                currentFileSize = int(service.files().get(fileId=current['id'], supportsAllDrives=True, fields='size,modifiedTime').execute()['size'])
                downloadFile(current['id'], path, currentFileSize)
            
        
def downloadFolder(id):
    folderName = service.files().get(fileId=id, supportsAllDrives=True).execute()['name']
    path = os.path.join(os.getcwd(), folderName)
    print("|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|")
    print("Download Path:", path)
    print("Parent Drive Folder:", folderName)
    print("Total number of files to Download:",totalNumberOfFiles, COLORS['Yellow'], sizeScaler(totalSize), COLORS['Reset'])
    print("|____________________________________________________________________________________________|")
    if not os.path.isdir(path):
        os.makedirs(path)
    os.chdir(path)
    downloadFolderRecursive(id)


############################################################################################################################################################################################################################################################################################
# Call Function


def main():
    global parentDownloadDirectory
    global totalNumberOfFiles
    global totalSize
    global currentFileNumber

    install_requirements() # Install requirements
    os.system('cls||clear')

    print(f"[##########################{COLORS['Yellow']}Google Drive Folder Download Without Zip{COLORS['Reset']}##########################]")

    ids = input(f"\nEnter Google Drive Folder Id(s) (separated by comma): {COLORS['Cyan']}")
    idList = [x.replace(" ","") for x in ids.split(",")]
    noOfDownloads = len(idList)
    path = input(f"{COLORS['Reset']} \nEnter destination path (leave empty to create a Downloads folder in current directory): {COLORS['Cyan']}")

    if not os.path.isdir(path):
        path = os.path.join(os.getcwd(), "Downloads")
        print(f"{COLORS['Yellow']}\n-Folder (with subfolders and files) Will be Downloaded to the Current Directory.")
    else:
        print(f"{COLORS['Yellow']}\n-Folder (with subfolders and files) Will be Downloaded to: {path}")

    print(f"-Note: To stop the download open ['Task Manager'(Windows)/'System Monitor'(Linux)] and")
    print(f"['End Task'/'Stop'] 'python' or 'python3'.{COLORS['Reset']}")
    key = input(f"-Press 'y' to Continue OR 'n' to Quit. {COLORS['Cyan']}")

    if key == "y":
        if not os.path.isdir(path):
            os.makedirs(path)
        parentDownloadDirectory = path
        try:
            print(COLORS['Green'], "\n**********************************************************************************************\n*                                      Download Startig                                      *\n**********************************************************************************************\n",COLORS['Reset'])
            for x,id in zip(range(0,noOfDownloads),idList):
                os.chdir(parentDownloadDirectory)
                totalNumberOfFiles = 0
                totalSize = 0
                currentFileNumber = 0
                print(f"\n\n\n|#############################[Downloading parent folder {(x+1)} of {noOfDownloads}]#############################|\n")
                numberAndSizeOfOfFilesRecursive(id)
                downloadFolder(id)
            print(COLORS['Green'], "\n\n**********************************************************************************************\n*                                      Download Complete                                     *\n**********************************************************************************************\n", COLORS['Reset'])
        except:
            traceback.print_exc()
    elif key == "n":
        exit()

main() 
