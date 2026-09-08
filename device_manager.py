from flask import Flask, jsonify, request
import json

app = Flask(__name__)

devices = [
    {'id': '1', 'name': 'Device 1', 'status': 'infected', 'ip': '192.168.1.2'},
    {'id': '2', 'name': 'Device 2', 'status': 'infected', 'ip': '192.168.1.3'},
]

@app.route('/')
def index():
    return 'Device Manager API is running.'

@app.route('/devices', methods=['GET'])
def get_devices():
    return jsonify(devices)

@app.route('/command', methods=['POST'])
def send_command():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    device_id = data.get('deviceId')
    command = data.get('command')
    for device in devices:
        if device['id'] == device_id:
            if command == 'encrypt':
                device['status'] = 'encrypting'
            elif command == 'beacon':
                device['status'] = 'beaconing'
            return jsonify({'success': True})
    return jsonify({'error': 'Device not found'}), 404

# NEW: Add /beacon endpoint
    @app.route('/beacon', methods=['GET', 'POST'])
def beacon():
    return jsonify({'status': 'beacon received'})
