from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import json

def get_user_profile():
    SCOPES = ['https://www.googleapis.com/auth/userinfo.profile',
              'https://www.googleapis.com/auth/userinfo.email', 
              'openid']
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES)
    
    creds = flow.run_local_server(port=0)

    # Save token for future reuse
    with open('token.json', 'w') as token_file:
        token_file.write(creds.to_json())

    people_service = build('people', 'v1', credentials=creds)
    profile = people_service.people().get(
        resourceName='people/me',
        personFields='names,emailAddresses,photos'
    ).execute()

    info = {
        "name": profile['names'][0]['displayName'],
        "email": profile['emailAddresses'][0]['value'],
        "photo": profile['photos'][0]['url']
    }
    return info
