import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define the scopes
scopes = [
    'https://www.googleapis.com/auth/photoslibrary.readonly',
    'https://www.googleapis.com/auth/photoslibrary.appendonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid',  # Include openid scope
]

# Load or create credentials
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

    # Save the credentials for the next run
    with open('_secrets_/token.json', 'w') as token:
        token.write(creds.to_json())

# Create a People API service
people_service = build('people', 'v1', credentials=creds)

# Use the service to retrieve user information
profile = people_service.people().get(resourceName='people/me', personFields='names,emailAddresses').execute()
print(profile)
# Extract email and first name
email = profile['emailAddresses'][0]['value']
first_name = profile['names'][0]['givenName']

print(f"Email: {email}")
print(f"First Name: {first_name}")
