import io
from datetime import datetime
from typing import Dict
from fastapi.responses import JSONResponse
import PyPDF2
import pdfplumber
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
import cv2
import numpy as np

from app.models.models import Document as DocumentModel
from ..standard.standard_validator import StandardValidator
from app.db.database import SessionLocal


class checkerPDF:
    def __init__(self):
        self.standard_validator = StandardValidator()

    async def check(self, file_content: bytes, file_name: str) -> JSONResponse:
        """Проверка документов формата .pdf"""
        try: 
            text_content = await self.extract_text(file_content)
            
            file_type = file_name.split('.')[-1].lower()
            file_size = len(file_content)
            
            standards = await self.standard_validator.check_references(text_content)      
            violations = await self.standard_validator.validate_document(text_content, standards)
            
            pdf_info = self.get_pdf_info(file_content)
            
            result = {
                "document_info": {
                    "filename": file_name,
                    "original_name": file_name,
                    "file_type": file_type,
                    "file_size": file_size,
                    "upload_date": datetime.now().isoformat()
                },
                "content_analysis": {
                    "total_characters": len(text_content),
                    "total_pages": pdf_info.get('total_pages', 0),
                    "is_scanned": pdf_info.get('is_scanned', False),
                    "extraction_method": pdf_info.get('extraction_method', 'unknown')
                },
                "validation_results": {
                    "is_compliant": len(violations) == 0,
                    "total_violations": len(violations),
                    "violations": violations
                }
            }
            
            await self.save_document(result, file_name)
            return JSONResponse(content=result, status_code=200)

        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)

    async def extract_text(self, file_content: bytes) -> str:
        """Извлечение текста из PDF документа"""
        text = ""
        
        try:
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        
        except Exception as e:
            print(f"Ошибка при извлечении текста pdfplumber: {e}")
        
        if len(text.strip()) < 100:
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            except Exception as e:
                print(f"Ошибка при извлечении текста PyPDF2: {e}")
        
        if len(text.strip()) < 100:
            ocr_text = await self.extract_text_with_ocr(file_content)
            if ocr_text:
                text = ocr_text
        
        return text.strip()

    async def extract_text_with_ocr(self, file_content: bytes) -> str:
        """Извлечение текста из сканированного PDF с помощью OCR"""
        text = ""
        try:
            images = convert_from_bytes(file_content, dpi=200)
            
            for i, image in enumerate(images):
                img_array = np.array(image)
                
                img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
                
                thresh_pil = Image.fromarray(thresh)
                
                page_text = pytesseract.image_to_string(thresh_pil, lang='rus+eng')
                text += page_text + "\n"
                
        except Exception as e:
            print(f"Ошибка при OCR обработке: {e}")
        
        return text
    
    def get_pdf_info(self, file_content: bytes) -> Dict:
        """Получение базовой информации о PDF файле"""
        info = {
            'total_pages': 0,
            'is_scanned': False,
            'extraction_method': 'direct'
        }
        
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            info['total_pages'] = len(pdf_reader.pages)
            
            test_text = ""
            for i in range(min(3, info['total_pages'])):
                try:
                    page = pdf_reader.pages[i]
                    page_text = page.extract_text() or ""
                    test_text += page_text
                except:
                    pass
            
            if len(test_text) < 50 and info['total_pages'] > 0:
                info['is_scanned'] = True
                info['extraction_method'] = 'ocr'
            elif len(test_text) > 0:
                info['extraction_method'] = 'direct'
            else:
                info['extraction_method'] = 'unknown'
                
        except Exception as e:
            print(f"Ошибка при получении информации о PDF: {e}")
        
        return info

    
    async def save_document(self, result: Dict, file_name: str):
        """Сохранение документа в базу данных"""
        try:   
            with SessionLocal() as db:
                document = DocumentModel(
                    filename=file_name,
                    original_name=file_name,
                    file_type=result["document_info"]["file_type"],
                    file_size=result["document_info"]["file_size"],
                    status="checked",
                    violations=result["validation_results"]["violations"],    
                    compliance_score=100 - len(result["validation_results"]["violations"]),
                    checked_by="system",
                    check_date=datetime.now()
                )
                db.add(document)
                db.commit()
                db.refresh(document)
        except Exception as e:
            print(f"Ошибка при сохранении документа {file_name} в базу данных: {e}")