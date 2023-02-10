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
# config_logging(logging, logging.DEBUG)
client = Client(config.API_KEY, config.API_SECRET)


def order(side, quantity, symbol, order_type):
    try:
        print(f"sending FUTURES order: {symbol} {side} {order_type} {quantity}")
        # test_order = client.create_test_order(
        #    symbol='BTCUSDT',
        #    type='MARKET',
        #    side='BUY',
        #    quantity=0.001
        # )
        # logging.info(test_order)

        client.futures_change_leverage(symbol=symbol, leverage=1)
        now = datetime.datetime.now()
        print("FIRST ORDER FUTURES:"+side)
        print("Time First Order..." + now.strftime("%Y-%m-%d %H:%M:%S"))
        order_futures = buy_sell(symbol=symbol,side=side,quantity=quantity)
        print(order_futures)

    except Exception as e:
        logging.error(
            "Found error. status: {}, error message: {}".format(e)
        )
        print("an exception occured - {}".format(e))
        return False
    return order_futures

def order2(side, quantity, symbol, order_type):
    try:
        print(f"sending FUTURES order: {symbol} {side} {order_type} {quantity}")
        client.futures_change_leverage(symbol=symbol, leverage=12)
        now = datetime.datetime.now()



        print("ORDER FUTURES 1 "+side)
        print("Time Futures 1..." + now.strftime("%Y-%m-%d %H:%M:%S"))
        order_futures = buy_sell(symbol=symbol,side=side,quantity=quantity)
        print(order_futures)

        time.sleep(2)

        #if side == 'BUY':
        #    side = 'SELL'
        #else:
        #    side = 'BUY'

        print("ORDER FUTURES 2:"+side)
        print("Time Futures 2..." + now.strftime("%Y-%m-%d %H:%M:%S"))
        order_futures = buy_sell(symbol=symbol,side=side,quantity=quantity)
        print(order_futures)

    except Exception as e:
        logging.error(
            "Found error. status: {}, error message: {}".format(e)
        )
        print("an exception occured - {}".format(e))
        return False
    return order_futures

def buy_sell(symbol, side, quantity):
    order_futures = client.futures_create_order(
        symbol=symbol,
        type='MARKET',
        side=side,
        quantity=quantity
    )
    return order_futures

@app.route('/webhook', methods=['POST'])
def webhook():
    print("webhook method starts")
    data = json.loads(request.data)
    if data['passphase'] != config.WEBHOOK_PASSPHRASE:
        return {
            "code": "error",
            "message": "Invalid Passphrase"
        }
    # TODO CORTAR PERP DO TICKER
    # TODO IDENTIFICAR BUY OR SELL PELO OPEN E CLOSE
    # TODO LOGICA DE CALCULAR PORCENTAGEM DE AMOUNT/ALAVACANGEM PARA DEFINIR QUANTIDADE
    tickerItem = data['ticker'].split("PERP", 1)
    ticker = str(tickerItem[0])
    print("ticker:" + ticker)
    side = 'SELL'
    if data['open'] < data['close']:
        side = 'BUY'

    print("side:" + side)
    order_response = order(side, 100, ticker, 'MARKET')
    return {
        "code": "success",
        "message": order_response
    }

@app.route('/webhook2', methods=['POST'])
def webhook2():
    print("webhook2 method starts")
    data = json.loads(request.data)
    if data['passphase'] != config.WEBHOOK_PASSPHRASE:
        return {
            "code": "error",
            "message": "Invalid Passphrase"
        }
    # TODO CORTAR PERP DO TICKER
    # TODO IDENTIFICAR BUY OR SELL PELO OPEN E CLOSE
    # TODO LOGICA DE CALCULAR PORCENTAGEM DE AMOUNT/ALAVACANGEM PARA DEFINIR QUANTIDADE
    tickerItem = data['ticker'].split("PERP", 1)
    ticker = str(tickerItem[0])
    print("ticker:" + ticker)
    side = 'SELL'
    if data['open'] < data['close']:
        side = 'BUY'

    print("side:" + side)
    order_response = order2(side, 100, ticker, 'MARKET')
    return {
        "code": "success",
        "message": order_response
    }

@app.route('/get', methods=['GET'])
def get():
    #order_response = order('BUY', 100, 'DOGEUSDT', 'MARKET')
    try:
        data = json.loads(request.data)
        print("request.data")
        print(request.data)
        print("DATAAAA GET")
        print(data)

        response = client.futures_get_position_mode()
        #response = client.get_order_book(symbol="AUDIOUSDT")
        #response = client.get_open_order(symbol="AUDIOUSDT")
        print("response ggg")
        print(response)
        print("response fim")
    except Exception as e:
        logging.error(
            "Found error. status: {}, error message: {}".format(e)
        )
        print("an exception occured - {}".format(e))
    return {
        "code": "success",
        "message": response
    }

def main():

    firstTime = True
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
                                markEmailAsRead(service, message)
                                print("MESSAGE ID SET TO UNREAD:" + message['id'])
                                print("firstTime:"+str(firstTime))
                                if firstTime == True:
                                    r = requests.post('http://localhost:5000/webhook', data=split_message)
                                    firstTime = False
                                else:
                                    r = requests.post('http://localhost:5000/webhook2', data=split_message)
                                print(f"Status Code: {r.status_code}")
                                print(f"JSON file: {split_message}")
        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')

        time.sleep(15)



def markEmailAsRead(service, message):
    service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()


if __name__ == '__main__':
    main()
