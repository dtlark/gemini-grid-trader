import requests
import hmac
import json
import base64
import hashlib
import datetime, time
from time import sleep

base_url = "https://api.gemini.com"

endpoints = {
    "new": "/v1/order/new",
    "cancel": "/v1/order/cancel",
    "heartbeat": "/v1/heartbeat",
    "usd": "v1/notionalbalances/:currency"
}

def load_settings():
    with open('settings.json') as settings:
        return json.load(settings)


config = load_settings()
api_secret = config["gemini_api_secret"].encode()
currencies = config["currencies"]

def getNonce():
    t = datetime.datetime.now()
    payload_nonce = str(int(time.mktime(t.timetuple()) * 1000))
    return payload_nonce


def getRequestHeaders(payload):
    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(api_secret, b64, hashlib.sha384).hexdigest()

    request_headers = {
        'Content-Type': "text/plain",
        'Content-Length': "0",
        'X-GEMINI-APIKEY': config["gemini_api_key"],
        'X-GEMINI-PAYLOAD': b64,
        'X-GEMINI-SIGNATURE': signature,
        'Cache-Control': "no-cache"
    }
    return request_headers


def postNew(nonce, order_id, symbol, amount, price):
    payload = {
        "request": "/v1/order/new",
        "nonce": nonce,
        "client_order_id": order_id,
        "symbol": symbol,
        "amount": amount,
        "price": price,
        "side": "buy",
        "type": "exchange limit",
        #"options": ["immediate-or-cancel"],
    }

    response = requests.post(base_url + "/v1/order/new", headers=getRequestHeaders(payload))
    return response.json()

def postHeartbeat(nonce):
    payload = {
        "request": "/v1/heartbeat",
        "nonce": nonce,
    }
    response = requests.post(base_url + "/v1/heartbeat", headers=getRequestHeaders(payload))
    return response.json

if __name__ == '__main__':
    print(config)
    print("\n")

    buy_orders = []
    sell_orders = []

    whileLoop = True

    while whileLoop:

        print(postHeartbeat(getNonce()))

        for curr in currencies:
            symbol = curr["symbol"]
            delta = (curr["upper_price"] - curr["lower_price"]) / curr["grid_lines"]

            try:
                response = requests.get(f"https://api.gemini.com/v1/pubticker/{symbol}").json()
                price = float(response['ask'])
                print(price)
            except Exception as e:
                print(f"Request Failed: {e} \n Retrying...")
                continue

            buy_orders.append(postNew(getNonce(), str(000), f"{symbol}", "0.1", 0.03))

        sleep(15)
