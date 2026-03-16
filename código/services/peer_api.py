# 专门放 peer 之间通信
import requests
import time

from app.config import DEFAULT_PORT
from app.state import ip_time, list_ping, lock

def ping(ip: str, msg: dict):
    url = f"http://{ip}:{DEFAULT_PORT}/buzon"

    try:
        r = requests.post(url, json=msg, timeout=5)

        if r.status_code == 200:
            with lock:
                ip_time[ip] = time.time()
                list_ping.discard(ip)
            return r.json()

    except requests.exceptions.RequestException:
        pass

    return None