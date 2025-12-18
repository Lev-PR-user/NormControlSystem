import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# одключения к PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

# Создание движка базы данных
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  
    echo=False  
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"Подключение к базе данных успешно: {version}")
            return True
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return False
