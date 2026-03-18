# 全局共享状态
import threading

ip_time: dict[str, float] = {}
list_ip: set[str] = set()
list_ping: set[str] = set()
lock = threading.Lock()