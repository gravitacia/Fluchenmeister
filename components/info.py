import platform
import psutil
import socket
import datetime
import os
import GPUtil
import requests
import wmi

os_name = platform.system() + " " + platform.release()
build_number = platform.version()
architecture = platform.machine()
kernel_version = platform.version()

boot_timestamp = psutil.boot_time()
boot_time = datetime.datetime.fromtimestamp(boot_timestamp).strftime("%Y-%m-%d %H:%M:%S")

uptime_seconds = (datetime.datetime.now() - datetime.datetime.fromtimestamp(boot_timestamp)).total_seconds()
uptime_days = int(uptime_seconds // (24 * 3600))
uptime_hours = int((uptime_seconds % (24 * 3600)) // 3600)
uptime_minutes = int((uptime_seconds % 3600) // 60)
system_uptime = f"{uptime_days} days, {uptime_hours} hours, {uptime_minutes} minutes"

cpu = platform.processor()
cpu_cores = psutil.cpu_count(logical=False)
cpu_threads = psutil.cpu_count(logical=True)

ram = psutil.virtual_memory()
ram_total_gb = round(ram.total / (1024 ** 3), 1)
ram_used_gb = round(ram.used / (1024 ** 3), 1)

disk = psutil.disk_usage(os.path.expanduser("~"))
disk_total_gb = round(disk.total / (1024 ** 3))
disk_used_gb = round(disk.used / (1024 ** 3))
disk_percentage_used = disk.percent

gpus = GPUtil.getGPUs()
gpu_name = gpus[0].name if gpus else None

c = wmi.WMI()
motherboard = c.Win32_BaseBoard()[0].Product

hostname = socket.gethostname()
private_ip = socket.gethostbyname(hostname)
public_ip = requests.get('https://api.ipify.org').text.strip()
ip_info = requests.get(f'https://ipinfo.io/{public_ip}/json').json()

storage_devices = []
for partition in psutil.disk_partitions():
    try:
        usage = psutil.disk_usage(partition.mountpoint)
        storage_devices.append({
            'device': partition.device,
            'mountpoint': partition.mountpoint,
            'total_gb': round(usage.total / (1024 ** 3)),
            'used_gb': round(usage.used / (1024 ** 3)),
            'percent_used': usage.percent
        })
    except PermissionError:
        continue
