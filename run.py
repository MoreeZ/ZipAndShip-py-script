import zipfile
import os
import argparse
from oauth2client import file, client, tools
from httplib2 import Http
from googleapiclient.discovery import build
import io
import httplib2
from pathlib import Path
import re
import webbrowser


# ================================================
# Create a temporary zip file
# ================================================
def zipTheFiles(zipFileN):
    myFiles = []
    for file in os.listdir(os.path.dirname(runFolderPath)):
        regexp = re.compile(r'ZipAndShip')
        if not regexp.search(file):
            myFiles.append(file)

    with zipfile.ZipFile(zipFileN+".zip", "w") as zf:
        for f in myFiles:
            zf.write('../'+f, f)
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


# ================================================
# Run and handle the process
# ================================================
runFolderPath = os.path.dirname(os.path.abspath(__file__))

if os.path.isfile(runFolderPath+"\\credentials.json"):
    zipFileName = input("What do you want to call the zip file?: ")
    try:
        zipTheFiles(zipFileName)
    except:
        input("Oops! Failed to zip the files! Press Enter key to exit..")
    else:

        shipIt(zipFileName)
        askToOpen = input("Do you want to open your drive? y/n: ")
        if askToOpen == "y" or askToOpen == "yes":
            webbrowser.open('https://drive.google.com/drive/my-drive', new=2)

    finally:
        removeZipFile(zipFileName)
else:
    print('You MUST set up google api modules and include "credentials.json" in this folder!')
    print('1. Install google api modules: pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib oauth2client')
    print('2. Go to: https://developers.google.com/drive/api/v3/quickstart/python')
    print('3. Click on Enable Drive API and download the clinet config.')
    input('4. Place the client config in the ZipAndShip folder and run the app again.')
    exit()
