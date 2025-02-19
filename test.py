import zmq
import json


def send_request(request_data):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    socket.send_string(json.dumps(request_data))
    response = socket.recv_string()
    return json.loads(response)


# Test currency conversion
conversion_request = {
    "request_type": "conversion",
    "data": {
        "amount": 100,
        "from_currency": "USD",
        "to_currency": "EUR"
    }
}
print("Test 1: currency conversion")
print("Conversion Request:", conversion_request)
conversion_response = send_request(conversion_request)
print("Conversion Response:", conversion_response)

# Test currency conversion for unsupported currency
conversion_request = {
    "request_type": "conversion",
    "data": {
        "amount": 50,
        "from_currency": "ABC",
        "to_currency": "TWD"
    }
}
print("\nTest 2: currency conversion for unsupported currency")
print("Conversion Request:", conversion_request)
conversion_response = send_request(conversion_request)
print("Conversion Response:", conversion_response)

# Test retrieval of exchange rates
retrieval_request = {
    "request_type": "retrieval",
    "data": {}
}
print("\nTest 3: retrieval of exchange rates")
print("Retrieval Request:", retrieval_request)
retrieval_response = send_request(retrieval_request)
print("Retrieval Response:", retrieval_response)
