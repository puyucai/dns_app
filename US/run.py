from flask import Flask, request, jsonify, abort
import datetime
import socket
import requests
import json

app = Flask(__name__)

@app.route('/fibonacci', methods=['GET'])
def fibonacci():
    # Extract query parameters
    hostname = request.args.get('hostname')
    fs_port = request.args.get('fs_port')
    number = request.args.get('number')
    as_ip = request.args.get('as_ip')
    as_port = int(request.args.get('as_port'))

    # Validate query parameters
    if not all([hostname, fs_port, number, as_ip, as_port]):
        abort(400, description="Bad Request: Missing parameters")

    dns_message = f"TYPE=A\nNAME={hostname}\n"


    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(dns_message.encode(), (as_ip, as_port))
        data, _ = sock.recvfrom(1024)
        response = data.decode()

    lines = response.split('\n')
    record = {line.split('=')[0]: line.split('=')[1] for line in lines if line}
    fs_ip = record["VALUE"]
    if not fs_ip:
        return 'Fibonacci Server not found', 404

    # Request Fibonacci number from FS
    fs_response = requests.get(f'http://{fs_ip}:{fs_port}/fibonacci?number={number}')
    if fs_response.status_code == 200:
        return jsonify(fs_response.json()), 200
    else:
        return 'Error contacting Fibonacci Server', fs_response.status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

