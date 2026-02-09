from typing import List, Dict
from fastapi import HTTPException
from pathlib import Path

from .checkerDOCX import checkerDOCX
from .checkerPDF import checkerPDF
from .checkerXLSX import checkerXLSX
from .CheckerCSV import checkerCSV

class DocumentChecker:
    def __init__(self):
        self.checkers = {
            'docx': checkerDOCX(),
            'pdf': checkerPDF(),
            'xlsx': checkerXLSX(),
            'csv': checkerCSV(),
        }

    async def check(self, file_content: bytes, file_name: str) -> List[Dict]:
        """Проверка документа"""
        try:
            file_extension = Path(file_name).suffix.lower().lstrip('.')
            if file_extension not in self.checkers:
                raise HTTPException(400, f"формат: .{file_extension} не поддерживается")
            checker = self.checkers[file_extension]
            result = await checker.check(file_content, file_name)
            return result
        except Exception as e:
            raise HTTPException(500, detail=f"Ошибка при проверке документа: {e}")