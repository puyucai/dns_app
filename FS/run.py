from flask import Flask, request, jsonify, abort, render_template
import socket
import json
import requests

app = Flask(__name__)


# Function to calculate Fibonacci number
def fibonacci(n):
    if n < 0:
        abort(400, "Negative numbers are not allowed.")
    elif n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

@app.route('/')
def home():
    return render_template('index.html')

# Endpoint to register FS with AS
@app.route('/register', methods=['PUT'])
def register():
    data = request.json
    hostname = data.get('hostname')
    ip = data.get('ip')
    as_ip = data.get('as_ip')
    as_port = int(data.get('as_port'))

    # Form the DNS message
    dns_message = f"TYPE=A\nNAME={hostname}\nVALUE={ip}\nTTL=10\n"

    # Send the DNS message to AS via UDP
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(dns_message.encode(), (as_ip, as_port))
        response, _ = sock.recvfrom(1024)
    # Register with AS
    # requests.put(f'http://{as_ip}:{as_port}/register', json={
    #     'hostname': hostname,
    #     'ip': ip
    # })

    return jsonify({"message": "Registration successful"}), 201


# Endpoint to calculate Fibonacci number
@app.route('/fibonacci')
def get_fibonacci():
    number = request.args.get('number', type=int)
    if number is None:
        abort(400, "Invalid input format.")

    result = fibonacci(number)
    return jsonify({"fibonacci": result}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090, debug=True)