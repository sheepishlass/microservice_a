import zmq
import requests
import json
import time
from threading import Thread
from datetime import datetime

EXCHANGE_API_URL = "https://api.exchangerate-api.com/v4/latest/USD"
CACHE = {}
LAST_UPDATE = 0
CACHE_EXPIRY = 86400  # 24 hours in seconds


def fetch_exchange_rates():
    global CACHE, LAST_UPDATE
    while True:
        success = False
        for _ in range(3):
            try:
                response = requests.get(EXCHANGE_API_URL)
                if response.status_code == 200:
                    CACHE = response.json().get("rates", {})
                    LAST_UPDATE = time.time()
                    print("Exchange rates updated.")
                    success = True
                    break
            except Exception as e:
                last_exception = e
        if not success:
            print(f"Error fetching exchange rates after 3 attempts: {last_exception}")
        time.sleep(CACHE_EXPIRY)


def convert_currency(amount, from_currency, to_currency):
    if from_currency not in CACHE or to_currency not in CACHE:
        return {"request_type": "conversion", "error": "Currency not supported."}
    converted_amount = amount * (CACHE[to_currency] / CACHE[from_currency])
    return {"request_type": "conversion", "converted_amount": converted_amount, "to_currency": to_currency}


def handle_request(request):
    request_data = json.loads(request)
    req_type = request_data.get("request_type")
    data = request_data.get("data")

    if req_type == "conversion":
        amount = data.get("amount")
        from_currency = data.get("from_currency", "USD")
        to_currency = data.get("to_currency")
        return json.dumps(convert_currency(amount, from_currency, to_currency))

    elif req_type == "retrieval":
        selected_currencies = {currency: CACHE[currency] for currency in ["EUR", "JPY", "CAD", "GBP", "AUD", "MXN", "CHF", "HKD", "SGD", "CNY"] if currency in CACHE}
        readable_timestamp = datetime.fromtimestamp(LAST_UPDATE).strftime('%Y-%m-%d %H:%M:%S') if LAST_UPDATE else "Never"
        return json.dumps({"request_type": "retrieval", "exchange_rates": selected_currencies, "last_updated": readable_timestamp})

    return json.dumps({"error": "Invalid request type."})


def start_server():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    print("Microservice running on port 5555...")

    while True:
        request = socket.recv()
        response = handle_request(request)
        socket.send_string(response)


if __name__ == "__main__":
    # Start the exchange rate updater in a separate thread
    Thread(target=fetch_exchange_rates, daemon=True).start()

    # Start the microservice server
    start_server()
