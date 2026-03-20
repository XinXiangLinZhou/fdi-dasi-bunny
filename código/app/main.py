# FastAPI app，只负责组装
from fastapi import FastAPI
from routes.buzon import router as buzon_router
from app.config import MY_ALIAS

app = FastAPI(title=f"Agent {MY_ALIAS}")
app.include_router(buzon_router)



