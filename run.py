"""
STARK LinkedIn Automation - Direct Runner
Run this file directly via: py run.py
"""
import os
import sys

# Prevent Windows console charmap encoding crashes (cp1252)
if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if sys.stderr:
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import subprocess

CONFIG_FILE = "user_config.txt"

def check_config():
    if not os.path.exists(CONFIG_FILE):
        if os.path.exists("user_config.example.txt"):
            import shutil
            shutil.copy("user_config.example.txt", CONFIG_FILE)
        print(f"[!] {CONFIG_FILE} not found!")
        print(">> Launching setup form to configure your LinkedIn credentials...")
        subprocess.call([sys.executable, "app.py"])
        return False
    
    # Read and verify credentials exist
    config = {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                key, val = line.split(":", 1)
                config[key.strip()] = val.strip()
    
    user_id = config.get("USER_ID", "")
    password = config.get("PASSWORD", "")
    
    if not user_id or not password:
        print("[!] LinkedIn USER_ID or PASSWORD is empty in user_config.txt!")
        print(">> Launching setup form to fill your credentials...")
        subprocess.call([sys.executable, "app.py"])
        return False
        
    return True

def main():
    print("=" * 60)
    print("      [*] STARK LINKEDIN AUTO APPLICANT - DIRECT RUN       ")
    print("=" * 60)
    
    if check_config():
        print(">> Config verified.")
        print(">> Starting LinkedIn Automation directly (bypassing web form)...")
        print("-" * 60)
        
        # Execute job_apply.py directly with unbuffered output
        result = subprocess.call([sys.executable, "-u", "job_apply.py"])
        if result == 0:
            print("\n>> Bot execution completed successfully.")
        else:
            print(f"\n>> Bot exited with code {result}.")

if __name__ == "__main__":
    main()
