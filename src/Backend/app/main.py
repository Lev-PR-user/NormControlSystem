from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.routes.router import router
from cache import cache, cached
from app.routes.user_routes import router as userrouter
from app.models.models import create_all_tables

try:
    from cache.redis_client import cache
    print("Cache imported from redis_client")
except ImportError:
    print("Could not import cache from redis_client")
    cache = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

app.include_router(router)
app.include_router(userrouter)

try:
    create_all_tables()
    print("Таблицы успешно созданы")
except Exception as e:
    print(f"Ошибка при создании таблиц в базе данных: {e}")

    