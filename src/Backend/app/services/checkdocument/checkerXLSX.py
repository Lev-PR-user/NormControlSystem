import io
from datetime import datetime
from typing import Dict, List, Any
from fastapi.responses import JSONResponse
import openpyxl
from openpyxl import load_workbook

from app.models.models import Document as DocumentModel
from ..standard.standard_validator import StandardValidator
from app.db.database import SessionLocal


class checkerXLSX:
    def __init__(self):
        self.standard_validator = StandardValidator()

    async def check(self, file_content: bytes, file_name: str) -> JSONResponse:
        """Проверка документов формата .xlsx"""
        try: 
            workbook = load_workbook(io.BytesIO(file_content), data_only=True)
            
            text_content = self.extract_text(workbook)
            
            structure_analysis = self.analyze_structure(workbook)
            
            file_type = file_name.split('.')[-1].lower()
            file_size = len(file_content)
            
            standards = await self.standard_validator.check_references(text_content)      
            violations = await self.standard_validator.validate_document(text_content, standards)
            
            structure_violations = self.check_excel_structure(workbook)
            violations.extend(structure_violations)
            
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
                    "total_sheets": structure_analysis.get('total_sheets', 0),
                    "total_rows": structure_analysis.get('total_rows', 0),
                    "total_columns": structure_analysis.get('total_columns', 0),
                    "total_cells": structure_analysis.get('total_cells', 0),
                    "empty_cells_percentage": structure_analysis.get('empty_cells_percentage', 0),
                    "sheets_info": structure_analysis.get('sheets_info', [])
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

    def extract_text(self, workbook: openpyxl.Workbook) -> str:
        """Извлечение текста из Excel файла"""
        try:
            all_text = []
            
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                sheet_text = []
                
                sheet_text.append(f"=== Лист: {sheet_name} ===")
                
                for row in sheet.iter_rows(values_only=True):
                    row_text = []
                    for cell in row:
                        if cell is not None:
                            cell_str = str(cell).strip()
                            if cell_str:
                                row_text.append(cell_str)
                    
                    if row_text:
                        sheet_text.append(" | ".join(row_text))
                
                if len(sheet_text) > 1:  
                    all_text.append("\n".join(sheet_text))
            
            return "\n\n".join(all_text)
            
        except Exception as e:
            print(f"Ошибка при извлечении текста из Excel: {e}")
            return ""

    def analyze_structure(self, workbook: openpyxl.Workbook) -> Dict[str, Any]:
        """Анализ структуры Excel файла"""
        try:
            total_rows = 0
            total_columns = 0
            total_cells = 0
            empty_cells = 0
            sheets_info = []
            
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                
                max_row = sheet.max_row
                max_column = sheet.max_column
                
                sheet_cells = max_row * max_column
                sheet_filled_cells = 0
                
                for row in sheet.iter_rows(min_row=1, max_row=min(max_row, 1000), values_only=True):
                    for cell in row:
                        if cell is not None and str(cell).strip():
                            sheet_filled_cells += 1
                
                sheet_empty_cells = sheet_cells - sheet_filled_cells
                
                sheet_info = {
                    "name": sheet_name,
                    "rows": max_row,
                    "columns": max_column,
                    "cells": sheet_cells,
                    "filled_cells": sheet_filled_cells,
                    "empty_cells": sheet_empty_cells,
                    "empty_percentage": (sheet_empty_cells / sheet_cells * 100) if sheet_cells > 0 else 0
                }
                sheets_info.append(sheet_info)
                
                total_rows += max_row
                total_columns = max(total_columns, max_column) 
                total_cells += sheet_cells
                empty_cells += sheet_empty_cells
            
            empty_cells_percentage = (empty_cells / total_cells * 100) if total_cells > 0 else 0
            
            return {
                'total_sheets': len(workbook.sheetnames),
                'total_rows': total_rows,
                'total_columns': total_columns,
                'total_cells': total_cells,
                'empty_cells': empty_cells,
                'empty_cells_percentage': round(empty_cells_percentage, 2),
                'sheets_info': sheets_info
            }
            
        except Exception as e:
            print(f"Ошибка при анализе структуры Excel: {e}")
            return {}

    def check_excel_structure(self, workbook: openpyxl.Workbook) -> List[Dict]:
        """Проверка структуры Excel файла"""
        violations = []
        
        try:
            if not workbook.sheetnames:
                violations.append({
                    'type': 'excel_structure',
                    'severity': 'high',
                    'message': 'Excel файл не содержит листов',
                    'suggestion': 'Добавьте хотя бы один лист с данными'
                })
                return violations
            
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                
                if sheet.max_row <= 1 and sheet.max_column <= 1:
                    violations.append({
                        'type': 'excel_structure',
                        'severity': 'medium',
                        'message': f'Лист "{sheet_name}" пустой или содержит только одну ячейку',
                        'suggestion': f'Добавьте данные на лист "{sheet_name}"',
                        'sheet': sheet_name
                    })
                    continue
                
                first_row_has_data = False
                first_row = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True), None)
                if first_row:
                    for cell in first_row:
                        if cell is not None and str(cell).strip():
                            first_row_has_data = True
                            break
                
                if not first_row_has_data:
                    violations.append({
                        'type': 'excel_structure',
                        'severity': 'medium',
                        'message': f'Лист "{sheet_name}" не имеет заголовков в первой строке',
                        'suggestion': f'Добавьте заголовки столбцов в первую строку листа "{sheet_name}"',
                        'sheet': sheet_name
                    })
                
                formulas_found = False
                for row in sheet.iter_rows(min_row=1, max_row=min(100, sheet.max_row)):
                    for cell in row:
                        if cell.data_type == 'f':  
                            formulas_found = True
                            break
                    if formulas_found:
                        break
                
                if not formulas_found and sheet.max_row > 10:
                    violations.append({
                        'type': 'excel_structure',
                        'severity': 'low',
                        'message': f'Лист "{sheet_name}" не содержит формул',
                        'suggestion': f'Рассмотрите добавление формул для автоматических расчетов на листе "{sheet_name}"',
                        'sheet': sheet_name
                    })
            
            hidden_sheets = []
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                if sheet.sheet_state == 'hidden':
                    hidden_sheets.append(sheet_name)
            
            if hidden_sheets:
                violations.append({
                    'type': 'excel_structure',
                    'severity': 'low',
                    'message': f'Найдены скрытые листы: {", ".join(hidden_sheets)}',
                    'suggestion': 'Рассмотрите необходимость скрытых листов. Для отчетности все данные должны быть видимыми.',
                    'hidden_sheets': hidden_sheets
                })
                
        except Exception as e:
            print(f"Ошибка при проверке структуры Excel: {e}")
        
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