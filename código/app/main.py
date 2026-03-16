# FastAPI app，只负责组装
from fastapi import FastAPI
from app.routes.buzon import router as buzon_router

app = FastAPI()
app.include_router(buzon_router)