from fastapi import HTTPException
import json
from sqlalchemy import asc, desc
from typing import List, Optional, Dict, Any

from app.db.database import SessionLocal
from app.models.models import Standard as StandardModel

def create_standard(standard_data: dict):    
    db = SessionLocal()
    try:
        existing = db.query(StandardModel).filter(
            StandardModel.code == standard_data["code"]
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"Стандарт с кодом '{standard_data['code']}' уже существует"
            )
        
        requirements = standard_data.get("requirements", {})
        if isinstance(requirements, dict):
            requirements_json = json.dumps(requirements)
        else:
            requirements_json = "{}"
        
        db_standard = StandardModel(
            code=standard_data["code"],
            name=standard_data["name"],
            description=standard_data.get("description", ""),
            category=standard_data.get("category", ""),
            requirements=requirements_json, 
            is_active=standard_data.get("is_active", True)
        )
        
        db.add(db_standard)
        db.commit()
        db.refresh(db_standard)
        
        return {
            "message": "Standard Created Successfully",
            "id": db_standard.id,
            "code": db_standard.code,
            "name": db_standard.name
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

def get_by_id(id: int) -> Dict[str, any]:
    db = SessionLocal()
    try: 
        standard = db.query(StandardModel).filter(StandardModel.id == id).first()
        if not standard:
            raise HTTPException(status_code=404, detail="Стандарта с таким {id} не сущестует")
        return {
            "id": standard.id,
            "code": standard.code,
            "name": standard.name,
            "description": standard.description,
            "category": standard.category,
            "is_active": standard.is_active,
            "requirements": standard.requirements
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

def get_by_code(code: str) -> Dict[str, any]:
    """Получение стандарта по коду"""
    db = SessionLocal()
    try:
        standard = db.query(StandardModel).filter(
            StandardModel.code.ilike(code)
        ).first()
        
        if not standard:
            raise HTTPException(
                status_code=404, 
                detail=f"Стандарт с кодом '{code}' не найден"
            )
            
        return {
            "id": standard.id,
            "code": standard.code,
            "name": standard.name,
            "description": standard.description,
            "category": standard.category,
            "is_active": standard.is_active,
            "requirements": standard.requirements
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()


def get_by_name(name: str) -> Dict[str, any]:
    """Получение стандарта по названию"""
    db = SessionLocal()
    try:
        standard = db.query(StandardModel).filter(
            StandardModel.name.ilike(f"%{name}%")
        ).first()
        
        if not standard:
            raise HTTPException(
                status_code=404, 
                detail=f"Стандарт с названием '{name}' не найден"
            )
            
        return {
            "id": standard.id,
            "code": standard.code,
            "name": standard.name,
            "description": standard.description,
            "category": standard.category,
            "is_active": standard.is_active,
            "requirements": standard.requirements
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()


def update_standard(id: int, standard_data: dict) -> Dict[str, Any]:
    """Обновление стандарта"""
    db = SessionLocal()
    try:
        standard = db.query(StandardModel).filter(StandardModel.id == id).first()
        
        if not standard:
            raise HTTPException(status_code=404, detail=f"Стандарт с ID {id} не найден")
        
        if "code" in standard_data and standard_data["code"] != standard.code:
            existing = db.query(StandardModel).filter(
                StandardModel.code == standard_data["code"]
            ).first()
            if existing:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Стандарт с кодом '{standard_data['code']}' уже существует"
                )
        
        update_fields = {}
        
        if "code" in standard_data:
            update_fields["code"] = standard_data["code"]
        if "name" in standard_data:
            update_fields["name"] = standard_data["name"]
        if "description" in standard_data:
            update_fields["description"] = standard_data["description"]
        if "category" in standard_data:
            update_fields["category"] = standard_data["category"]
        if "is_active" in standard_data:
            update_fields["is_active"] = standard_data["is_active"]
        
        if "requirements" in standard_data:
            requirements = standard_data.get("requirements", {})
            if isinstance(requirements, dict):
                update_fields["requirements"] = json.dumps(requirements, ensure_ascii=False)
            else:
                update_fields["requirements"] = "{}"
        
        for field, value in update_fields.items():
            setattr(standard, field, value)
        
        db.commit()
        db.refresh(standard)
        
        return {
            "message": "Standard Updated Successfully",
            "id": standard.id,
            "code": standard.code,
            "name": standard.name,
            "updated_fields": list(update_fields.keys())
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

def delete_standard(id: int) -> Dict[str, Any]:
    """Удаление стандарта"""
    db = SessionLocal()
    try:
        standard = db.query(StandardModel).filter(StandardModel.id == id).first()
        
        if not standard:
            raise HTTPException(status_code=404, detail=f"Стандарт с ID {id} не найден")
        
        standard_info = {
            "id": standard.id,
            "code": standard.code,
            "name": standard.name
        }
        
        db.delete(standard)
        db.commit()
        
        return {
            "message": "Standard Deleted Successfully",
            "deleted_standard": standard_info
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()