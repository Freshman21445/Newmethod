# device_manager.py
import json
import random

devices = [
    {'id': '1', 'name': 'Device 1', 'status': 'infected', 'ip': '192.168.1.2'},
    {'id': '2', 'name': 'Device 2', 'status': 'infected', 'ip': '192.168.1.3'},
    # Add more devices as needed
]

def get_devices():
    return json.dumps(devices)

def send_command(device_id, command):
    for device in devices:
        if device['id'] == device_id:
            if command == 'encrypt':
                device['status'] = 'encrypting'
            elif command == 'beacon':
                device['status'] = 'beaconing'
            break
    return json.dumps({'success': True})

if __name__ == '__main__':
    from http.server import SimpleHTTPRequestHandler, HTTPServer

    class DeviceHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/devices':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(get_devices().encode('utf-8'))
            else:
                return super().do_GET()

        def do_POST(self):
            if self.path == '/command':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                device_id = data['deviceId']
                command = data['command']
                response = send_command(device_id, command)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.encode('utf-8'))
            else:
                return super().do_POST()

    def run(server_class=HTTPServer, handler_class=DeviceHandler, port=8000):
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        print(f'Starting httpd server on port {port}')
        httpd.serve_forever()

    run()
