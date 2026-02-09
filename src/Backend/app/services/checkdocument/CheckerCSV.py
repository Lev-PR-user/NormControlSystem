import io
import csv
from datetime import datetime
from typing import Dict, List, Any
from fastapi.responses import JSONResponse
import pandas as pd
import chardet

from app.models.models import Document as DocumentModel
from ..standard.standard_validator import StandardValidator
from app.db.database import SessionLocal


class checkerCSV:
    def __init__(self):
        self.standard_validator = StandardValidator()

    async def check(self, file_content: bytes, file_name: str) -> JSONResponse:
        """Проверка документов формата .csv"""
        try: 
            encoding = self.detect_encoding(file_content)
            
            text_content, csv_data = await self.read_csv(file_content, encoding)
            
            structure_analysis = self.analyze_structure(csv_data)
            
            file_type = file_name.split('.')[-1].lower()
            file_size = len(file_content)
            
            standards = await self.standard_validator.check_references(text_content)      
            violations = await self.standard_validator.validate_document(text_content, standards)
            
            structure_violations = self.check_csv_structure(csv_data, text_content)
            violations.extend(structure_violations)
            
            result = {
                "document_info": {
                    "filename": file_name,
                    "original_name": file_name,
                    "file_type": file_type,
                    "file_size": file_size,
                    "upload_date": datetime.now().isoformat(),
                    "encoding": encoding
                },
                "content_analysis": {
                    "total_characters": len(text_content),
                    "total_rows": structure_analysis.get('total_rows', 0),
                    "total_columns": structure_analysis.get('total_columns', 0),
                    "empty_cells": structure_analysis.get('empty_cells', 0),
                    "empty_cells_percentage": structure_analysis.get('empty_cells_percentage', 0),
                    "delimiter": structure_analysis.get('delimiter', ','),
                    "has_header": structure_analysis.get('has_header', False)
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

    def detect_encoding(self, file_content: bytes) -> str:
        """Определение кодировки файла"""
        try:
            result = chardet.detect(file_content)
            encoding = result['encoding'] if result['encoding'] else 'utf-8'
            
            if encoding.lower() == 'windows-1251':
                return 'cp1251'
            elif encoding.lower() == 'maccyrillic':
                return 'mac_cyrillic'
            elif encoding.lower() in ['iso-8859-5', 'koi8-r']:
                return encoding.lower()
            
            return encoding
        except:
            return 'utf-8'

    async def read_csv(self, file_content: bytes, encoding: str) -> tuple[str, List[List[str]]]:
        """Чтение CSV файла и извлечение текста"""
        all_text = []
        csv_data = []
        
        try:
            delimiters = [',', ';', '\t', '|']
            detected_delimiter = ','
            
            for delim in delimiters:
                try:
                    decoded_content = file_content.decode(encoding, errors='ignore')
                    
                    string_io = io.StringIO(decoded_content)
                    
                    sample = []
                    reader = csv.reader(string_io, delimiter=delim)
                    for i, row in enumerate(reader):
                        if i < 5:
                            sample.append(row)
                        else:
                            break
                    
                    if len(sample) > 1 and any(len(row) > 1 for row in sample):
                        detected_delimiter = delim
                        break
                        
                except:
                    continue
            
            decoded_content = file_content.decode(encoding, errors='ignore')
            string_io = io.StringIO(decoded_content)
            
            reader = csv.reader(string_io, delimiter=detected_delimiter)
            
            for row in reader:
                csv_data.append(row)
                
                row_text = " | ".join([str(cell).strip() for cell in row if cell and str(cell).strip()])
                if row_text:
                    all_text.append(row_text)
            
            text_content = "\n".join(all_text)
            
        except Exception as e:
            print(f"Ошибка при чтении CSV: {e}")
            
            try:
                df = pd.read_csv(io.BytesIO(file_content), encoding=encoding, sep=None, engine='python')
                csv_data = df.values.tolist()
                text_content = df.to_string(index=False)
            except Exception as pd_error:
                print(f"Ошибка при чтении CSV через pandas: {pd_error}")
                csv_data = []
                text_content = ""
        
        return text_content, csv_data

    def analyze_structure(self, csv_data: List[List[str]]) -> Dict[str, Any]:
        """Анализ структуры CSV файла"""
        try:
            if not csv_data:
                return {}
            
            total_rows = len(csv_data)
            
            total_columns = max(len(row) for row in csv_data) if csv_data else 0
            
            total_cells = sum(len(row) for row in csv_data)
            empty_cells = 0
            
            for row in csv_data:
                for cell in row:
                    if not cell or not str(cell).strip():
                        empty_cells += 1
            
            empty_cells_percentage = (empty_cells / total_cells * 100) if total_cells > 0 else 0
            
            delimiter = ','
            
            has_header = False
            if csv_data and len(csv_data) > 0:
                first_row = csv_data[0]
                text_cells = sum(1 for cell in first_row if cell and any(c.isalpha() for c in str(cell)))
                if text_cells > len(first_row) / 2:
                    has_header = True
            
            return {
                'total_rows': total_rows,
                'total_columns': total_columns,
                'total_cells': total_cells,
                'empty_cells': empty_cells,
                'empty_cells_percentage': round(empty_cells_percentage, 2),
                'delimiter': delimiter,
                'has_header': has_header
            }
            
        except Exception as e:
            print(f"Ошибка при анализе структуры CSV: {e}")
            return {}

    def check_csv_structure(self, csv_data: List[List[str]], text_content: str) -> List[Dict]:
        """Проверка структуры CSV файла"""
        violations = []
        
        try:
            if not csv_data:
                violations.append({
                    'type': 'csv_structure',
                    'severity': 'high',
                    'message': 'CSV файл пустой или не содержит данных',
                    'suggestion': 'Проверьте содержимое файла'
                })
                return violations
            
            if len(csv_data) < 2:
                violations.append({
                    'type': 'csv_structure',
                    'severity': 'medium',
                    'message': 'CSV файл содержит слишком мало строк',
                    'suggestion': 'Добавьте данные в файл'
                })
            
            column_counts = [len(row) for row in csv_data]
            min_cols = min(column_counts)
            max_cols = max(column_counts)
            
            if min_cols != max_cols:
                violations.append({
                    'type': 'csv_structure',
                    'severity': 'high',
                    'message': f'Несогласованное количество колонок: от {min_cols} до {max_cols}',
                    'suggestion': 'Убедитесь, что все строки имеют одинаковое количество колонок'
                })
            
            for i, row in enumerate(csv_data[:50]): 
                for j, cell in enumerate(row):
                    if cell and len(str(cell)) > 1000:
                        violations.append({
                            'type': 'csv_structure',
                            'severity': 'low',
                            'message': f'Слишком длинное значение в строке {i+1}, колонке {j+1}',
                            'suggestion': 'Разделите длинные текстовые значения',
                            'row': i + 1,
                            'column': j + 1
                        })
            
            special_chars = ['\x00', '\x01', '\x02', '\x03', '\x04']
            for i, row in enumerate(csv_data[:50]):
                for j, cell in enumerate(row):
                    if cell:
                        cell_str = str(cell)
                        for char in special_chars:
                            if char in cell_str:
                                violations.append({
                                    'type': 'csv_structure',
                                    'severity': 'medium',
                                    'message': f'Найден непечатаемый символ в строке {i+1}, колонке {j+1}',
                                    'suggestion': 'Удалите непечатаемые символы',
                                    'row': i + 1,
                                    'column': j + 1
                                })
                                break
            
            quote_count = text_content.count('"') + text_content.count("'")
            if quote_count > 100 and len(csv_data) > 0:
                violations.append({
                    'type': 'csv_structure',
                    'severity': 'low',
                    'message': 'Обнаружено много кавычек в данных',
                    'suggestion': 'Убедитесь, что кавычки правильно экранированы'
                })
                
        except Exception as e:
            print(f"Ошибка при проверке структуры CSV: {e}")
        
        return violations

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