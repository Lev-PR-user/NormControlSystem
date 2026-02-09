from fastapi import APIRouter, Query, HTTPException
from app.db.database import  check_db_connection
from app.services.checkdocument.documents import DocumentChecker
from app.services.standard.standards import (
   create_standard,
   get_by_id,
   update_standard,
   delete_standard,
   get_by_code,
   get_by_name  )
from fastapi import UploadFile, File
from cache.redis_client import cache 

router = APIRouter()

@router.get("/test-cache")
async def test_cache():
    """Эндпоинт для тестирования кэша"""
    try:
        # Тест записи
        cache.set("test:endpoint", {"timestamp": "now", "test": True}, 60)
        
        # Тест чтения
        data = cache.get("test:endpoint")
        
        # Тест статистики
        stats = cache.get_stats() if hasattr(cache, 'get_stats') else {}
        
        return {
            "status": "success",
            "cache_test": "passed" if data else "failed",
            "cache_type": type(cache).__name__,
            "stats": stats,
            "test_data": data
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/")
async def root():
    return {"message": "Normal Control System"}

@router.get("/health")
async def health_check():
   return {"message": "OK"}

@router.get("/health-db")
async def health_db():
   if check_db_connection():
      return {"message": "OK"}
   else:
      raise HTTPException(status_code=500, detail="Database connection failed")
   
# Работа с стандартами
@router.get("/{id}")
async def get_standard_by_id_endpoint(id: int):
    return get_by_id(id)

@router.get("/by-code/{code}")
async def get_standard_by_code_endpoint(code: str):
    """Получение стандарта по коду"""
    return get_by_code(code)


@router.get("/by-name/{name}")
async def get_standard_by_name_endpoint(name: str):
    """Получение стандарта по названию"""
    return get_by_name(name)

@router.post("/uploadstandard")
async def uploadstandard(standard_data: dict):
   result = create_standard(standard_data)
   return result

@router.put("/{id}")
async def update_standard_endpoint(id: int, standard_data: dict):
    return update_standard(id, standard_data)

@router.delete("/{id}")
async def delete_standard_endpoint(id: int):
    return delete_standard(id)

# Работа с документами
@router.post("/uploaddocument/")
async def upload_document(file: UploadFile = File(...)):
   content = await file.read()
   checker = DocumentChecker()
   result = await checker.check(content, file.filename)
   return result

