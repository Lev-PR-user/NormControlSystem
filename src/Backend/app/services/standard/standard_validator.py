import re
from typing import List, Dict
import spacy
import traceback

from app.db.database import SessionLocal
from app.models.models import Standard as StandardModel

class StandardValidator:
    def __init__(self):
        """Загрузка модели для обработки русского языка"""
        try:
            self.nlp_ru = spacy.load("ru_core_news_sm")
        except OSError:
            self.nlp_ru = None

    async def validate_document(self, txt: str, standarts: List[str]) -> List[Dict]:
        """Проверка документа на соответствие стандартам"""
        try:
            violations = []
            terminology_violations = await self.check_terminology(txt)
            violations.extend(terminology_violations)

            reference_violations = await self.check_references(txt)
            violations.extend(reference_violations)

            return violations
        except Exception as e:
            print(f"Ошибка при проверке документа: {e}")
            print(f"Ошибка при проверке документа: {traceback.format_exc()}")
            return []

    async def check_terminology(self, txt: str) -> List[Dict]:
        """Проверка терминологии"""
        violations = []

        incorrect_terminology = {
            "чертёжник": "инженер-конструктор",
            "конструктор": "инженер-конструктор",
            "технолог": "инженер-технолог",
            "схемка": "схема",
            "расчетчик": "инженер-расчетчик",
            "экономист": "экономист-менеджер"
        }

        for incorrect, correct in incorrect_terminology.items():
            pattern = r'\b' + re.escape(incorrect) + r'\b'
            matches = re.finditer(pattern, txt.lower())
            
            for match in matches:
                violations.append({
                    'type': 'terminology', 
                    'severity': 'medium', 
                    'message': f'Некорректный термин: "{incorrect}"', 
                    'suggestion': f'Замените на: "{correct}"', 
                    'position': match.start()
                })
        return violations

    async def check_references(self, txt: str) -> List[Dict]:
        """Проверка ссылок на нормативные документы"""
        
        violations = []
        
        patterns = [
            r'\b(ГОСТ(?:\s+Р)?\s*[\d\.\-]+\s*(?:\d{4})?)',
            r'\b(ОСТ\s*[\d\.\-]+\s*(?:\d{4})?)',
            r'\b(НП[\s\-]*[\d\.\-]+)',
            r'\b(РД[\s\-]*[\d\.\-]+)',
            r'\b(СТО\s*[\d\.\-]+)',
            r'\b(ISO[\s\-]*[\d\.\-]+)',
        ]
        
        found_standards = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, txt, re.IGNORECASE)
            for match in matches:
                standard_ref = match.group(0).strip()
                found_standards.append(standard_ref)
        
        unique_standards = list(set(found_standards))
        
        for standard_ref in unique_standards:
            standard_ref = standard_ref.upper()
            standard_ref = re.sub(r'\s+', ' ', standard_ref)
            standard_ref = re.sub(r'[^\w\s\.\-]', '', standard_ref)
            
            is_actual = await self.check_standard(standard_ref)
            
            if not is_actual:
                violations.append({
                    'type': 'reference', 
                    'severity': 'high', 
                    'message': f'Устаревший или недействующий стандарт: "{standard_ref}"', 
                    'suggestion': 'Замените на актуальную версию (Посмотрите в базе Росатома)',
                })
        
        return violations

    async def check_standard(self, standard_ref: str) -> bool:
        """Проверка актуальности стандарта"""
        db = SessionLocal()
        try:
            search_patterns = [
                f"%{standard_ref}%",
                f"%{standard_ref.replace(' ', '')}%",
                f"%{re.sub(r'[^\w]', '', standard_ref)}%",
            ]
            
            for pattern in search_patterns:
                standard = db.query(StandardModel).filter(
                    StandardModel.code.ilike(pattern),
                    StandardModel.is_active == True
                ).first()
                
                if standard:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Ошибка при проверке актуальности стандарта: {e}")
            print(f"Ошибка при проверке актуальности стандарта: {traceback.format_exc()}")
            return False
        finally:
            db.close()