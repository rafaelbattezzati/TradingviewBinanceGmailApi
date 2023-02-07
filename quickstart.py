from __future__ import print_function

import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        #if not labels:
        #    print('No labels found.')
        #    return
        #print('Labels:')
        #for label in labels:
        #    print(label['name'])

        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages', [])
        if not messages:
            print("NO MESSAGES")
        else:
            message_count = 0
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                message_count = message_count + 1
                email_data = msg['payload']['headers']
                for values in email_data:
                    name = values["name"]
                    if name == "Subject":
                        subject_name = values["value"]
                        if subject_name.startswith('Alerta'):
                            split_message = subject_name.split('Alerta:',1)[1]
                            print(split_message)
                            json_object = json.loads(split_message)
                            print(type(json_object))
                            print(json_object["volume"])


                    #if name == "From":
                        #from_name = values["value"]
                        #if from_name == "TradingView <noreply@tradingview.com>":
                            #print("You have a new message from " + from_name)
                            #print("Message: "+values['name'])
            #print("You have " + str(message_count) + " messages")


    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

#def markEmailAsRead(service, message):
    #service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()

if __name__ == '__main__':
    main()