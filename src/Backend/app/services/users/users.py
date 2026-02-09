from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.db.database import SessionLocal
from app.models.models import Users as UserModel, Roles as RoleModel
from app.core.security import get_password_hash, verify_password, create_access_token
from app.services.users.user_validator import UserValidator  

def create_user(user_data: dict) -> Dict[str, Any]:
    UserValidator.validate_registration_data(user_data)
    
    db = SessionLocal()
    try:
        existing_user = db.query(UserModel).filter(
            UserModel.email == user_data["email"].lower().strip()
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        
        role_id = user_data.get("role_id", 1)
        role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
        
        if not role:
            if role_id == 1:
                new_role = RoleModel(
                    role_name="user"
                )
                db.add(new_role)
                db.commit()
                db.refresh(new_role)
                role = new_role
                print(f"Создана новая роль: {role.role_name} (id={role.id})")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Указанная роль не существует"
                )
        
        hashed_password = get_password_hash(user_data["password"])
        
        db_user = UserModel(
            name=user_data["name"].strip(),
            email=user_data["email"].lower().strip(),
            password=hashed_password,
            role_id=role.id
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        access_token = create_access_token(
            data={"sub": str(db_user.id)}
        )
        
        return {
            "message": "Пользователь успешно зарегистрирован",
            "user": {
                "id": db_user.id,
                "name": db_user.name,
                "email": db_user.email,
                "role_id": db_user.role_id
            },
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных: {str(e)}"
        )
    finally:
        db.close()

def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    UserValidator.validate_login_data({"email": email, "password": password})
    
    db = SessionLocal()
    try:
        normalized_email = email.lower().strip()
        
        user = db.query(UserModel).filter(UserModel.email == normalized_email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        
        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        
        access_token = create_access_token(
            data={"sub": str(user.id)}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role_id": user.role_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных: {str(e)}"
        )
    finally:
        db.close()

def get_user_profile(user_id: int) -> Dict[str, Any]:
    UserValidator.validate_user_id(user_id)
    
    db = SessionLocal()
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        role = db.query(RoleModel).filter(RoleModel.id == user.role_id).first()
        
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": {
                "id": role.id,
                "name": role.role_name
            } if role else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных: {str(e)}"
        )
    finally:
        db.close()

def update_user_profile(user_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
    UserValidator.validate_user_id(user_id)
    UserValidator.validate_profile_update_data(update_data)
    
    db = SessionLocal()
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        if "name" in update_data:
            user.name = update_data["name"].strip()
        
        if "email" in update_data:
            new_email = update_data["email"].lower().strip()
            existing_user = db.query(UserModel).filter(
                UserModel.email == new_email,
                UserModel.id != user_id
            ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким email уже существует"
                )
            user.email = new_email
        
        if "password" in update_data:
            user.password = get_password_hash(update_data["password"])
        
        db.commit()
        db.refresh(user)
        
        return {
            "message": "Профиль успешно обновлен",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role_id": user.role_id
            }
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных: {str(e)}"
        )
    finally:
        db.close()