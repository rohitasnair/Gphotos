 
import os
import pandas as pd
from configv import *

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

scopes=['https://www.googleapis.com/auth/photoslibrary.readonly','https://www.googleapis.com/auth/photoslibrary.appendonly']
creds = None

if os.path.exists('_secrets_/token.json'):
    creds = Credentials.from_authorized_user_file('_secrets_/token.json', scopes)
        
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            '_secrets_/client_secret.json', scopes)
        creds = flow.run_local_server()
    print(creds)
    # Save the credentials for the next run
    with open('_secrets_/token.json', 'w') as token:
        token.write(creds.to_json())




#Search for a pic using below code


from google.auth.transport.requests import AuthorizedSession
authed_session = AuthorizedSession(creds)

nextPageToken = None
idx = 0
media_items = []
while True:
    idx += 1
    print(idx)
    
    response = authed_session.post(
        'https://photoslibrary.googleapis.com/v1/mediaItems:search', 
        headers = { 'content-type': 'application/json' },
        json={ 
            "pageSize": 100,
            "pageToken": nextPageToken,
            "filters": {
                "dateFilter": {
                    "ranges": [{ 
                        "startDate": {
                            "year": 2023,
                            "month": 1,
                            "day": 1,
                        },
                        "endDate": {
                            "year": 2023,
                            "month": 1,
                            "day": 26,
                        }
                    }]
                }
            }
        })
    
    response_json = response.json()
    #print(response_json)
    media_items += response_json["mediaItems"]
    
    if not "nextPageToken" in response_json:
        break
        
    nextPageToken = response_json["nextPageToken"]



#convert to pandas

photos_df = pd.DataFrame(media_items)
photos_df = pd.concat([photos_df, pd.json_normalize(photos_df.mediaMetadata).rename(columns={"creationTime": "creationTime_metadata"})], axis=1)
photos_df["creationTime_metadata_dt"] = pd.to_datetime(photos_df["creationTime_metadata"], utc=True).dt.tz_localize(None)

photos_df
photos_df.iloc[2]


#View
from IPython import display

image_data_response = authed_session.get(photos_df.baseUrl[2] + "=w500-h250")
display.Image(data=image_data_response.content)




# read image from file
with open("a.png", "rb") as f:
    image_contents = f.read()

# upload photo and get upload token
response = authed_session.post(
    "https://photoslibrary.googleapis.com/v1/uploads", 
    headers={},
    data=image_contents)
upload_token = response.text
print(upload_token)
# use batch create to add photo and description
response = authed_session.post(
        'https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate', 
        headers = { 'content-type': 'application/json' },
        json={
            "newMediaItems": [{
                "description": "Test photo",
                "simpleMediaItem": {
                    "uploadToken": upload_token,
                    "fileName": "test.jpg"
                }
            }]
        }
)
print(response.text)