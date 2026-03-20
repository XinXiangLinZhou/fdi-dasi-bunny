# 全局共享状态
import threading

ip_time = {}
list_ip = set()
list_ping = set()

chat_history = {}
chat_status = {}
post_objects = {}

lock = threading.Lock()