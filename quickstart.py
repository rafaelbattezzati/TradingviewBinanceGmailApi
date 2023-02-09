from __future__ import print_function

import os.path
import time
import datetime
import json, config
import logging
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask import Flask, request
from binance.lib.utils import config_logging
from binance.client import Client
from binance.enums import *


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify',
          'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive.metadata']

app = Flask(__name__)
#config_logging(logging, logging.DEBUG)
client = Client(config.API_KEY, config.API_SECRET)
def order(side, quantity, symbol, order_type):
    try:
        print(f"sending FUTURES order: {symbol} {side} {order_type} {quantity}")
        #test_order = client.create_test_order(
        #    symbol='BTCUSDT',
        #    type='MARKET',
        #    side='BUY',
        #    quantity=0.001
        #)
        #logging.info(test_order)

        #client.futures_change_margin_type(symbol=symbol, marginType='ISOLATED')
        client.futures_change_leverage(symbol=symbol, leverage=1)

        order_futures = client.futures_create_order(
            symbol=symbol,
            type='MARKET',
            side=side,
            quantity=quantity
        )
        print(order)
    except Exception as e:
        logging.error(
            "Found error. status: {}, error message: {}".format(e)
        )
        print("an exception occured - {}".format(e))
        return False
    return order_futures

@app.route('/webhook', methods=['POST'])
def webhook():
    print("Order method starts")
    data = json.loads(request.data)

    if data['passphase'] != config.WEBHOOK_PASSPHRASE:
        return {
            "code": "error",
            "message": "Invalid Passphrase"
        }

    #side = request.data['side']
    #quantity = request.data['quantity']
    #ticker = request.data['ticker']

    order_response = order('BUY', 100, 'DOGEUSDT', 'MARKET')
    #order_response = order(side, 100, ticker, 'MARKET')
    print(order_response)
    return {
        "code": "success",
        "message": data
    }


def main():
    while (True):
        now = datetime.datetime.now()
        print("Carregando TradingViewBinanceGmail..." + now.strftime("%Y-%m-%d %H:%M:%S"))
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

            # if not labels:
            #    print('No labels found.')
            #    return
            # print('Labels:')
            # for label in labels:
            #    print(label['name'])


            #headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            #json1 = '{                "passphase":"abcdefgh",                "time":"2023-02-09T00:25:00Z",                "exchange":"BINANCE",                "ticker":"DOGEUSDTPERP",                "time":"2023-02-09T00:24:00Z",                "open":0.0900261489017556,                "high":0.09004,                "low":0.08994,                "close":0.090005,                "volume":14158921            }'
            #r = requests.post('http://127.0.0.1:5000/webhook', data=json1)
            #print(f"Scheduler ASS333tatus: {r.status_code}")
            #print(f"Scheduler Status2: {json_object2}")

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
                                split_message = subject_name.split('Alerta:', 1)[1]
                                print(split_message)
                                json_object = json.loads(split_message)
                                print(json_object["volume"])
                                markEmailAsRead(service, message)
                                print("MESSAGE ID SET TO UNREAD:" + message['id'])
                                r = requests.post('http://localhost:5000/webhook', data=split_message)
                                print(f"VALENDO: {r.status_code}")
                                print(f"VALENDO2: {split_message}")
        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')

        time.sleep(60)


def markEmailAsRead(service, message):
    service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()


if __name__ == '__main__':
    main()
