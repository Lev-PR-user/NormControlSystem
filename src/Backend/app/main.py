from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.routes.router import router
from app.models.models import create_all_tables
app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

app.include_router(router)

try:
    create_all_tables()
    print("Таблицы успешно созданы")
except Exception as e:
    print(f"Ошибка при создании таблиц в базе данных: {e}")

    