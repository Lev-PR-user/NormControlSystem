import React, { useState } from 'react';
import './DocumentUploadPage.css';

const DocumentUploadPage = () => {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      validateAndSetFile(droppedFile);
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };

  const validateAndSetFile = (file) => {
    const allowedExtensions = ['.txt', '.doc', '.docx', '.pdf'];
    const maxSize = 10 * 1024 * 1024;

    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedExtensions.includes(fileExtension)) {
      setError('Неподдерживаемый формат файла. Поддерживаются: .txt, .doc, .docx, .pdf');
      return;
    }

    if (file.size > maxSize) {
      setError('Файл слишком большой. Максимальный размер: 10MB');
      return;
    }

    setFile(file);
    setError(null);
    setResult(null);
    setSuccess(false);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Пожалуйста, выберите файл');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);
    setSuccess(false);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/uploaddocument/', {
        method: 'POST',
        body: formData,
      });

      const resultData = await response.json();
      
      if (!response.ok) {
        throw new Error(resultData.detail || `Ошибка сервера: ${response.status}`);
      }

      setResult(resultData);
      setSuccess(true);
      
    } catch (error) {
      setError(`Ошибка: ${error.message}`);
      setSuccess(false);
    } finally {
      setIsLoading(false);
    }
  };

  const removeFile = () => {
    setFile(null);
    setError(null);
    setResult(null);
    setSuccess(false);
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' байт';
    else if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getViolationsFromResult = (resultData) => {
    if (resultData.validation_results && resultData.validation_results.violations) {
      return resultData.validation_results.violations;
    } else if (resultData.violations) {
      return resultData.violations;
    } else if (resultData.validation_results && Array.isArray(resultData.validation_results)) {
      return resultData.validation_results;
    }
    return [];
  };

  const getDocumentInfo = (resultData) => {
    return resultData.document_info || null;
  };

  const getContentAnalysis = (resultData) => {
    return resultData.content_analysis || null;
  };

  const getIsCompliant = (resultData) => {
    if (resultData.validation_results && resultData.validation_results.is_compliant !== undefined) {
      return resultData.validation_results.is_compliant;
    }
    return resultData.is_compliant !== undefined ? resultData.is_compliant : true;
  };

  const getTotalViolations = (resultData) => {
    if (resultData.validation_results && resultData.validation_results.total_violations !== undefined) {
      return resultData.validation_results.total_violations;
    }
    if (resultData.total_violations !== undefined) {
      return resultData.total_violations;
    }
    return getViolationsFromResult(resultData).length;
  };

  return (
    <div className="document-upload-page">
      <h2>Проверка документа на соответствие стандартам</h2>
      
      <div className="upload-area">
        <div 
          className={`drop-zone ${isDragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => !file && document.getElementById('file-input').click()}
        >
          <input
            type="file"
            id="file-input"
            onChange={handleFileSelect}
            accept=".txt,.doc,.docx,.pdf"
            style={{ display: 'none' }}
          />
          
          {!file ? (
            <>
              <div className="upload-icon"></div>
              <p className="upload-text">Перетащите файл сюда или нажмите для выбора</p>
              <button className="file-input-label">
                Выбрать файл
              </button>
            </>
          ) : (
            <div className="file-info">
              <div className="file-icon"></div>
              <div className="file-details">
                <p className="file-name">{file.name}</p>
                <p className="file-size">{formatFileSize(file.size)}</p>
              </div>
              <button onClick={removeFile} className="remove-file-btn" type="button">
                X
              </button>
            </div>
          )}
        </div>

        {error && (
          <div className="error-message">
            <strong>Ошибка:</strong> {error}
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!file || isLoading}
          className="upload-button"
          type="button"
        >
          {isLoading ? (
            <>
              <div className="spinner"></div>
              Проверка...
            </>
          ) : 'Проверить документ'}
        </button>
      </div>

      {result && success && (
        <div className="result-container">
          <div className="result-header">
            <h3 style={{ 
              color: getIsCompliant(result) ? '#28a745' : '#dc3545'
            }}>
              {getIsCompliant(result) ? 'Документ соответствует стандартам' : 'Найдены нарушения стандартов'}
            </h3>
          </div>
          
          <div className="result-content">
            {getDocumentInfo(result) && (
              <div className="document-info-section">
                <h4> Информация о документе</h4>
                <div className="info-grid">
                  <div className="info-item">
                    <strong>Название файла:</strong>
                    <span>{getDocumentInfo(result).filename || getDocumentInfo(result).original_name || file.name}</span>
                  </div>
                  <div className="info-item">
                    <strong>Размер:</strong>
                    <span>{formatFileSize(getDocumentInfo(result).file_size || file.size)}</span>
                  </div>
                  <div className="info-item">
                    <strong>Тип файла:</strong>
                    <span>{getDocumentInfo(result).file_type || file.type || 'Не указан'}</span>
                  </div>
                </div>
              </div>
            )}

            {getContentAnalysis(result) && (
              <div className="content-analysis-section">
                <h4> Анализ содержимого</h4>
                <div className="analysis-grid">
                  <div className="analysis-item">
                    <strong>Всего символов:</strong>
                    <span>{getContentAnalysis(result).total_characters || 0}</span>
                  </div>
                  <div className="analysis-item">
                    <strong>Абзацев:</strong>
                    <span>{getContentAnalysis(result).paragraphs || 0}</span>
                  </div>
                  {getContentAnalysis(result).tables !== undefined && (
                    <div className="analysis-item">
                      <strong>Таблиц:</strong>
                      <span>{getContentAnalysis(result).tables}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            <div className={`compliance-status ${getIsCompliant(result) ? 'compliant' : 'non-compliant'}`}>
              <div className="status-content">
                <div className="status-text">
                  <h4>{getIsCompliant(result) ? 'СООТВЕТСТВУЕТ СТАНДАРТАМ' : 'НЕ СООТВЕТСТВУЕТ СТАНДАРТАМ'}</h4>
                  <p>Обнаружено нарушений: <strong>{getTotalViolations(result)}</strong></p>
                </div>
              </div>
            </div>
            
            {(() => {
              const violations = getViolationsFromResult(result);
              if (violations.length > 0) {
                return (
                  <div className="violations">
                    <h4> Нарушения ({violations.length}):</h4>
                    {violations.map((violation, index) => (
                      <div key={index} className="violation-item">
                        <div className="violation-message">
                          <strong>{index + 1}. {violation.message || `Нарушение стандарта`}</strong>
                        </div>
                        <div className="violation-details">
                          {violation.type && (
                            <span className="violation-type">Тип: {violation.type}</span>
                          )}
                          <span className={`violation-severity severity-${(violation.severity || 'medium').toLowerCase()}`}>
                            Критичность: {violation.severity || 'Средняя'}
                          </span>
                        </div>
                        {violation.suggestion && (
                          <div className="violation-suggestion">
                            <em>💡 Рекомендация: {violation.suggestion}</em>
                          </div>
                        )}
                        {violation.position && (
                          <div className="violation-position">
                            Позиция в тексте: символ {violation.position}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                );
              } else if (getIsCompliant(result)) {
                return (
                  <div className="success-message">
                    <p>Нарушений не обнаружено. Документ соответствует всем требованиям стандартов.</p>
                  </div>
                );
              }
              return null;
            })()}
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUploadPage;