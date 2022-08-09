############################################################################################################################################################################################################################################################################################
#Install these libraries(ignore if already installed):


#pip install google
#pip install socket
#pip install progress
#pip install --upgrade google-auth
#pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib



############################################################################################################################################################################################################################################################################################
#Imports

import os
import io
import socket
import pickle
from time import sleep
import traceback
from progress.bar import IncrementalBar
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request

import time
from datetime import datetime as dt


from Colors import COLORS


############################################################################################################################################################################################################################################################################################
# Generating Client_Secret file, pickle and Creating Service


CLIENT_SECRET_FILE = 'client_secret.json' # Place this file (rename the file to 'client_secret.json') in same directory as this script. To get this file follow (https://www.youtube.com/watch?v=6bzzpda63H0). Credits (Channel: https://www.youtube.com/channel/UCvVZ19DRSLIC2-RUOeWx8ug)
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

def Create_Service(client_secret_file, api_name, api_version, *scopes): # From (Channel: https://www.youtube.com/channel/UCvVZ19DRSLIC2-RUOeWx8ug)
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]

    cred = None

    pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'
    # print(pickle_file)

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        #print(API_SERVICE_NAME, 'service created successfully')
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)



############################################################################################################################################################################################################################################################################################
# Global Variables


parentDownloadDirectory = os.getcwd()
totalNumberOfFiles = 0
totalSize = 0
currentFileNumber = 0
# OS = os.platform.system() # 'Linux', 'Windows', 'Darwin'



############################################################################################################################################################################################################################################################################################
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



############################################################################################################################################################################################################################################################################################
# Main Functions


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
    bar = IncrementalBar(max=100, suffix='%(percent)d%%')
    print(f"\n[{currentFileNumber}/{totalNumberOfFiles}]", " Downloading:",service.files().get(fileId=file_id, supportsAllDrives=True).execute()['name'], sizeScaler(size))
    while not done:
        try:
            status, done = downloader.next_chunk()
            p2 = progressPercentage(status.progress())
            # for x in track(range(p1,p2), description=""):
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
                #print("Path :", path)
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
    # print_color("-Note: To stop the download open ['Task Manager'(Windows)/'System Monitor'(Linux)] and ['End Task'/'Stop'] 'python' or 'python3'.", 'Red')
    print(f"-Note: To stop the download open ['Task Manager'(Windows)/'System Monitor'(Linux)] and")
    print(f"['End Task'/'Stop'] 'python' or 'python3'.{COLORS['Reset']}")
    key = input(f"-Press 'y' to Continue OR 'n' to Quit. {COLORS['Cyan']}")
    # key = input(" Enter: ")
    if key == "y":
        if not os.path.isdir(path):
            os.makedirs(path)
        parentDownloadDirectory = path
        try:
            # os.system('cls||clear');
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

#https://drive.google.com/drive/folders/197dYJHyL95ebF_gXXU1I1U-AiTlNB4GK



# 1SU1TuWHbThPI-B7AhyYpP-I_xjgb3DsC

# print("[                       Google Drive Folder Download Without Zip                             ]")
# print("[##########################Google Drive Folder Download Without Zip##########################]")
# print("|#############################[Downloading parent folder 1 of 1]#############################|")
# print("|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|")
# print("|____________________________________________________________________________________________|")