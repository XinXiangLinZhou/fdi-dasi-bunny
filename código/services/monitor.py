import time

from app.config import MY_ALIAS, PING_TIME, SLEEP_TIME
from app.state import ip_time, list_ip, list_ping, lock
from services.server_api import get_gente
from services.peer_api import ping

def update_ip():
    global list_ip, list_ping

    try:
        gente = get_gente()
        new_ips = {ip for alias, ip in gente.items() if alias != MY_ALIAS}

        with lock:
            list_ip.clear()
            list_ip.update(new_ips)

            for ip in new_ips:
                if ip not in ip_time:
                    list_ping.add(ip)

            old_ips = set(ip_time.keys()) - new_ips
            for ip in old_ips:
                ip_time.pop(ip, None)
                list_ping.discard(ip)

    except Exception as e:
        print("Error updating IP list:", e)

def check_inactive_ips():
    now = time.time()

    with lock:
        for ip in list_ip:
            last = ip_time.get(ip)

            if last is None or now - last > PING_TIME:
                list_ping.add(ip)

def loop(msg: dict):
    while True:
        try:
            update_ip()
            check_inactive_ips()

            with lock:
                current_ping_list = list(list_ping)

            for ip in current_ping_list:
                print(f"Ping a {ip}")
                ping(ip, msg)

        except Exception as e:
            print("Loop error:", e)

        time.sleep(SLEEP_TIME)