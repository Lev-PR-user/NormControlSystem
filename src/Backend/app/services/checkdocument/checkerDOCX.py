import io
from docx import Document
from typing import Dict, List
from datetime import datetime
from fastapi.responses import JSONResponse


from app.models.models import Document as DocumentModel
from ..standard.standard_validator import StandardValidator
from app.db.database import SessionLocal


class checkerDOCX:
    def __init__(self):
        self.standard_validator = StandardValidator()

    async def check(self, file_content: bytes, file_name: str) -> List[Dict]:
        """Проверка документов формата .docx"""
        try: 
            doc = Document(io.BytesIO(file_content))
            text_content = self.extract_text(doc)
            file_type = file_name.split('.')[-1].lower()
            file_size = len(file_content)
            standarts = await self.standard_validator.check_references(text_content)      
            violations = await self.standard_validator.validate_document(text_content, standarts)
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
                    "paragraphs": len(doc.paragraphs),
                    "tables": len(doc.tables),
                    "sections": len(doc.sections),
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

    def extract_text(self, doc: Document) -> str:
        """Извлечение текста из документа"""
        try:
            text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)

            for table in doc.tables:
                for row in table.rows:
                    row_text = []   
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text)
                    if row_text:
                        text.append(" | ".join(row_text))
            return "\n".join(text)
        except Exception as e:
            print(f"Ошибка при извлечении текста из документа: {e}")

    async def save_document(self, result: Dict, file_name: str):
        """Сохранение документа в базу данных"""
        try:   
            with SessionLocal() as db:
                document = DocumentModel(
                    filename = file_name,
                    original_name = file_name,
                    file_type = result["document_info"]["file_type"],
                    file_size = result["document_info"]["file_size"],
                    status = "checked",
                    violations = result["validation_results"]["violations"],    
                    compliance_score = len(result["validation_results"]["violations"]),
                    checked_by = "system",
                    check_date = datetime.now()
                )
                db.add(document)
                db.commit()
                db.refresh(document)
        except Exception as e:
            print(f"Ошибка при сохранении документа {file_name} в базу данных: {e}")
