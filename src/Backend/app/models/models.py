from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base, engine
from sqlalchemy.types import Text, Boolean, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255))
    file_type = Column(String(50))
    file_size = Column(Integer)
    status = Column(String(50), default="uploaded")
    upload_date = Column(DateTime, default=datetime.utcnow)
    check_date = Column(DateTime)
    checked_by = Column(String(255))
    violations = Column(JSON)
    compliance_score = Column(Integer)
    

class Standard(Base):
    __tablename__ = "standards"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True)
    name = Column(String(255))
    description = Column(Text)  
    category = Column(String(255))
    requirements = Column(JSON)
    is_active = Column(Boolean, default=True)   

def create_all_tables():
    Base.metadata.create_all(bind=engine)