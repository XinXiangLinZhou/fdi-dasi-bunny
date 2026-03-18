# FastAPI app，只负责组装
from fastapi import FastAPI
from routes.buzon import router as buzon_router

app = FastAPI()
app.include_router(buzon_router)