import socket
import json
from flask import Flask, request, jsonify, abort, render_template
import requests

# UDP IP and Port for the AS
UDP_IP = "localhost"
UDP_PORT = 53533

# DNS Records Storage
dns_records = {}


def register_record(data):
    """ Register a DNS record """
    # Extract data from the received message
    lines = data.split('\n')
    record = {line.split('=')[0]: line.split('=')[1] for line in lines if line}
    # Store the record
    dns_records[record['NAME']] = record
    print(f"Registered {record['NAME']} with IP {record['VALUE']}")


def query_record(name):
    """ Query a DNS record by name """
    # Retrieve the record
    record = dns_records.get(name)
    if record:
        return f"TYPE={record['TYPE']}\nNAME={record['NAME']}\nVALUE={record['VALUE']}\nTTL={record['TTL']}\n"
    else:
        return "NOT FOUND"
    print(f"Query result: \nTYPE={record['TYPE']}\nNAME={record['NAME']}\nVALUE={record['VALUE']}\nTTL={record['TTL']}\n")


# Setup the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print(f"Authoritative Server running on {UDP_IP}:{UDP_PORT}")
while True:
    data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
    data = data.decode()
    print("Received")
    if 'TYPE=A' in data and 'NAME=' in data:
        if 'VALUE=' in data:
            # Registration request
            register_record(data)
            response = "201 Created"
        else:
            # DNS query
            name = data.split('\n')[1].split('=')[1]  # Extract NAME from query
            response = query_record(name)
    else:
        response = "400 Bad Request"

    sock.sendto(response.encode(), addr)

# app = Flask(__name__)
#
# @app.route('/register', methods=['PUT'])
# def register():
#     data = request.json
#     dns_records[data['hostname']] = data['ip']
#     return '', 201
#
# @app.route('/query')
# def query():
#     name = request.args.get('name')
#     record = dns_records.get(name)
#     if record:
#         return jsonify({'TYPE': 'A', 'NAME': name, 'VALUE': record, 'TTL': 10}), 200
#     else:
#         return 'Record not found', 404
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=UDP_PORT, debug=True)