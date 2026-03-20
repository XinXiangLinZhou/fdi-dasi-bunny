# 固定配置
import os

# ===== Server config =====
SERVER_URL = os.getenv("SERVER_URL", "http://172.16.82.142:7719/")

# ===== Ollama =====
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ministral-3:8b")

# ===== Agent config =====
MY_ALIAS = os.getenv("ALIAS", "test")
MY_PORT = int(os.getenv("PORT", "7720"))
MY_HOST = os.getenv("HOST", "127.0.0.1")

# ===== Timing =====
SLEEP_TIME = int(os.getenv("SLEEP_TIME", "30"))
PING_TIME = int(os.getenv("PING_TIME", "60"))
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "12"))