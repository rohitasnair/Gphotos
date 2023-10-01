from flask import render_template
from flask import Blueprint
other_routes = Blueprint("other_routes", __name__)
from configv import *
import pandas as pd
import os
from flask import  redirect, url_for
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


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


authed_session = AuthorizedSession(creds)
response = authed_session.get(
        'https://photoslibrary.googleapis.com/v1/mediaItems/AAJppL4wlEzL3y842AT4dsbt0zdYmF_kDseliNcPghokUVTbLpVswAEXJlv5qgEBR0-enOV_ILwxyC7_1ixNYOa9B0Cx6sqzmA')
    
response_json = response.json()
print(response_json)