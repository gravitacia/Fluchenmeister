import psutil

processes = []

for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
    try:
        memory_mb = proc.info['memory_info'].rss / 1024 / 1024
        processes.append((proc.info['name'], proc.info['pid'], round(memory_mb, 1)))
    except:
        continue

processes.sort(key=lambda x: x[2], reverse=True)
