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
from flask import Flask, request

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


#Welcome page
@other_routes.route("/welcome")
def welcome():
    if person["is_logged_in"] == True:
        return render_template("welcome.html", image_urls=image_urls)
    else:
        return redirect(url_for('login'))

@other_routes.route("/start_scan")
def start_scan():
    if person["is_logged_in"] == True:
        selected_start_date = request.args.get('startDate')
        selected_end_date = request.args.get('endDate')

        
        selected_date_parts=selected_start_date.split('-')
        syear = int(selected_date_parts[0])
        smonth = int(selected_date_parts[1])
        sday = int(selected_date_parts[2])

        end_date_parts=selected_end_date.split('-')
        eyear = int(end_date_parts[0])
        emonth = int(end_date_parts[1])
        eday = int(end_date_parts[2])

        
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
                                    "year": syear,
                                    "month": smonth,
                                    "day": sday,
                                },
                                "endDate": {
                                    "year": eyear,
                                    "month": emonth,
                                    "day": eday,
                                }
                            }]
                        }
                    }
                })
            
            response_json = response.json()
            print(response_json)
            media_items += response_json["mediaItems"]
            
            if not "nextPageToken" in response_json:
                break
                
            nextPageToken = response_json["nextPageToken"]

        photos_df = pd.DataFrame(media_items)
        image_urls = photos_df.baseUrl.tolist()
        return render_template("welcome.html", image_urls=image_urls)
    else:
        return redirect(url_for('login'))