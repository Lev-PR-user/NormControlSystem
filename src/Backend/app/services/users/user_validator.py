import re
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from app.core.security import verify_password, get_password_hash

class UserValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        """Валидация email"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_regex, email))
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """Валидация имени"""
        name_regex = r'^[a-zA-Zа-яА-ЯёЁ0-9\s\-_]{2,100}$'
        return bool(re.match(name_regex, name))
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, Optional[str]]:
        """Валидация пароля"""
        if len(password) < 8:
            return False, "Пароль должен содержать минимум 8 символов"
        
        if len(password) > 100:
            return False, "Пароль не должен превышать 100 символов"
        
        if not re.search(r'\d', password):
            return False, "Пароль должен содержать хотя бы одну цифру"
        
        if not re.search(r'[a-zA-Zа-яА-ЯёЁ]', password):
            return False, "Пароль должен содержать хотя бы одну букву"
        
        return True, None
    
    @staticmethod
    def validate_registration_data(user_data: Dict[str, Any]) -> None:
        """Валидация данных для регистрации"""
        required_fields = ["name", "email", "password"]
        
        for field in required_fields:
            if not user_data.get(field):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Поле '{field}' обязательно для заполнения"
                )
        
        name = user_data.get("name", "").strip()
        if not UserValidator.validate_name(name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя может содержать только буквы, цифры, пробелы, дефисы и подчеркивания (2-100 символов)"
            )
        
        email = user_data.get("email", "").strip().lower()
        if not UserValidator.validate_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некорректный формат email"
            )
        
        password = user_data.get("password", "")
        is_valid, error_msg = UserValidator.validate_password(password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        role_id = user_data.get("role_id")
        if role_id is not None:
            try:
                role_id_int = int(role_id)
                if role_id_int not in [1, 2]:  
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Некорректный role_id. Допустимые значения: 1 (user), 2 (admin)"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="role_id должен быть числом"
                )
    
    @staticmethod
    def validate_login_data(login_data: Dict[str, Any]) -> None:
        """Валидация данных для входа"""
        required_fields = ["email", "password"]
        
        for field in required_fields:
            if not login_data.get(field):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Поле '{field}' обязательно для заполнения"
                )
        
        email = login_data.get("email", "").strip().lower()
        if not UserValidator.validate_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некорректный формат email"
            )
        
        password = login_data.get("password", "")
        if len(password) < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пароль не может быть пустым"
            )
    
    @staticmethod
    def validate_profile_update_data(update_data: Dict[str, Any]) -> None:
        """Валидация данных для обновления профиля"""
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нет данных для обновления"
            )
        
        allowed_fields = ["name", "email", "password"]
        
        for field in update_data.keys():
            if field not in allowed_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Поле '{field}' не может быть изменено"
                )
        
        if "name" in update_data:
            name = update_data["name"].strip()
            if not UserValidator.validate_name(name):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Имя может содержать только буквы, цифры, пробелы, дефисы и подчеркивания (2-100 символов)"
                )
        
        if "email" in update_data:
            email = update_data["email"].strip().lower()
            if not UserValidator.validate_email(email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Некорректный формат email"
                )
        
        if "password" in update_data:
            password = update_data["password"]
            is_valid, error_msg = UserValidator.validate_password(password)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
    
    @staticmethod
    def validate_user_id(user_id: int) -> None:
        """Валидация ID пользователя"""
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID пользователя обязательно"
            )
        
        try:
            user_id_int = int(user_id)
            if user_id_int <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ID пользователя должен быть положительным числом"
                )
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID пользователя должен быть числом"
            )