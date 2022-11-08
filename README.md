#  Google-Drive-Folder-Download-Without-Zip

# Why:
Whenever we need to download a folder from google drive, google first creates a zip of the folder on its backend and then downloads that zip file. Moreover if the folder size is more than 2 GB multiple zips are created that are parallelly downloaded. This creates a problem for users who are downloading some folder because it takes some extra time to zip the files and sometimes parallel downloading fails.
The idea is to use Google Drive API from the Google Cloud Console and download the folder and all the subfolders and files in that folder sequentially without zipping by using the folder ID and client_secret.json for authentication.

# How To Use:

## Step 1:
Download your client_secret.json file. To get this file follow [this][link1] video. Place this file (rename the file to 'client_secret.json') in same directory as this script.<br />
Note: Login with the same id on which the folder is present on drive.
 [Channel Credits][link2]

[link1]: <https://www.youtube.com/watch?v=6bzzpda63H0>
[link2]: <https://www.youtube.com/channel/UCvVZ19DRSLIC2-RUOeWx8ug>

## Step 2: 
Open Windows Terminal (or CMD) in the same directory as the script and type : `python G_Drive_Folder_Download.py`

## Step 3: 
Paste the folder ID(s) when prompted. <br />
Note: Folder ID of a folder on drive is the last part of the url when that folder is open. The yellow highlighted part in the image below. 
![image](https://user-images.githubusercontent.com/71930390/184150619-ff0cdb42-cc8f-4f21-b514-7699f18a2d0f.png)

[This][link3] article shows how to get Folder ID. 

[link3]: <https://robindirksen.com/blog/where-do-i-get-google-drive-folder-id>

## Screenshots:

![InkedG drive download](https://user-images.githubusercontent.com/71930390/183724620-cea8939d-5ccb-41cf-9b37-ed9bf4b18df2.jpg)

