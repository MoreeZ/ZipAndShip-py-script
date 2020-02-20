import zipfile
import os
import argparse
from oauth2client import file, client, tools
from httplib2 import Http
from googleapiclient.discovery import build
import io
import httplib2
from pathlib import Path

# ================================================
# Create a temporary zip file
# ================================================

runFolderPath = os.path.dirname(os.path.abspath(__file__))


def zipTheFiles(zipFileN):
    myFiles = []
    for file in os.listdir(os.path.dirname(runFolderPath)):
        if file != "ZipAndShip":
            myFiles.append(file)

    with zipfile.ZipFile(zipFileN+".zip", "w") as zf:
        for f in myFiles:
            zf.write(f)
            print(f)
    return True

# ================================================
# Send to Google Drive
# ================================================


def shipIt(zipFileN):
    # Authentication
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

    SCOPES = 'https://www.googleapis.com/auth/drive.file'
    store = file.Storage(os.path.join(runFolderPath, 'storage.json'))
    creds = store.get()

    if not creds or creds.invalid:
        print("make new storage data file ")
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store, flags) \
            if flags else tools.run(flow, store)

    DRIVE = build('drive', 'v3', http=creds.authorize(Http()))

    # Upload
    file_name = (zipFileN+'.zip')
    metadata = {'name': file_name,
                'mimeType': None
                }
    print("Uploading your zip file... : "+file_name)
    res = DRIVE.files().create(body=metadata, media_body=file_name).execute()
    if res:
        print('Uploaded "%s" (%s)' % (file_name, res['mimeType']))

# ================================================
# Remove the zip file
# ================================================


def removeZipFile(zipFileN):
    os.remove(zipFileN+".zip")


zipFileName = input("What do you want to call the zip file?: ")
try:
    zipTheFiles(zipFileName)
except:
    print("Oops! Failed to zip the files!")
else:
    shipIt(zipFileName)
finally:
    removeZipFile(zipFileName)
