import React, { useState } from 'react';
import './StandardPage.css';

const StandardPage = () => {
  const [searchType, setSearchType] = useState('id');
  const [searchValue, setSearchValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleSearch = async () => {
    if (!searchValue.trim()) {
      setError('Введите значение для поиска');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let url;
      if (searchType === 'id') {
        const id = parseInt(searchValue);
        if (isNaN(id)) {
          throw new Error('ID должен быть числом');
        }
        url = `http://localhost:8000/${id}`;
      } else if (searchType === 'code') {
        url = `http://localhost:8000/by-code/${encodeURIComponent(searchValue)}`;
      } else if (searchType === 'name') {
        url = `http://localhost:8000/by-name/${encodeURIComponent(searchValue)}`;
      }

      const response = await fetch(url);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || `Ошибка: ${response.status}`);
      }

      const formattedResult = {
        id: data.id,
        code: data.code || `ID: ${data.id}`,
        name: data.name || 'Не указано',
        description: data.description || 'Описание отсутствует',
        category: data.category || 'Не указана',
        is_active: data.is_active,
        requirements: parseRequirements(data.requirements),
        message: data.message
      };

      setResult(formattedResult);
      
    } catch (err) {
      setError(err.message || 'Ошибка при поиске стандарта');
    } finally {
      setLoading(false);
    }
  };

  const parseRequirements = (requirements) => {
    if (!requirements) return null;
    
    try {
      if (typeof requirements === 'string') {
        return JSON.parse(requirements);
      }
      if (typeof requirements === 'object') {
        return requirements;
      }
      return null;
    } catch (e) {
      return requirements;
    }
  };

  const handleClear = () => {
    setSearchValue('');
    setError(null);
    setResult(null);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const getStatusInfo = (isActive) => {
    if (isActive === true) {
      return {
        text: 'Активен',
        className: 'active',
        description: 'Стандарт активен и используется'
      };
    } else if (isActive === false) {
      return {
        text: 'Неактивен',
        className: 'inactive',
        description: 'Стандарт не активен'
      };
    } else {
      return {
        text: 'Статус не определен',
        className: 'unknown',
        description: 'Статус не указан'
      };
    }
  };

  return (
    <div className="standard-page">
      <div className="page-header">
        <h1>Поиск стандартов</h1>
        <p className="page-subtitle">
          Поиск стандартов по ID, коду или названию в базе данных
        </p>
      </div>
      
      <div className="search-container">
        <div className="search-card">
          <div className="search-type-selector">
            <div className="selector-label">
              <span className="selector-icon"></span>
              <span>Тип поиска:</span>
            </div>
            <div className="radio-group">
              <label className={`radio-option ${searchType === 'id' ? 'selected' : ''}`}>
                <input
                  type="radio"
                  value="id"
                  checked={searchType === 'id'}
                  onChange={(e) => setSearchType(e.target.value)}
                />
                <span className="radio-text">По ID</span>
              </label>
              <label className={`radio-option ${searchType === 'code' ? 'selected' : ''}`}>
                <input
                  type="radio"
                  value="code"
                  checked={searchType === 'code'}
                  onChange={(e) => setSearchType(e.target.value)}
                />
                <span className="radio-text">По коду</span>
              </label>
              <label className={`radio-option ${searchType === 'name' ? 'selected' : ''}`}>
                <input
                  type="radio"
                  value="name"
                  checked={searchType === 'name'}
                  onChange={(e) => setSearchType(e.target.value)}
                />
                <span className="radio-text">По названию</span>
              </label>
            </div>
          </div>
          
          <div className="search-input-group">
            <div className="input-wrapper">
              <span className="input-icon">
                {searchType === 'id' ? '№' : searchType === 'code' ? '#' : '@'}
              </span>
              <input
                type="text"
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                placeholder={getPlaceholder(searchType)}
                onKeyPress={handleKeyPress}
                disabled={loading}
                className="search-input-field"
              />
            </div>
            
            <div className="action-buttons">
              <button 
                onClick={handleSearch}
                disabled={loading || !searchValue.trim()}
                className="btn-primary"
              >
                  <>
                    <span className="btn-icon"></span>
                    Найти стандарт
                  </>
              </button>
              <button 
                onClick={handleClear}
                disabled={loading}
                className="btn-secondary"
              >
                <span className="btn-icon"></span>
                Очистить
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="error-alert">
            <span className="alert-icon"></span>
            <div className="alert-content">
              <strong>Ошибка поиска:</strong>
              <p>{error}</p>
            </div>
          </div>
        )}

        {result && (
          <div className="standard-card">
            <div className="card-header">
              <div className="standard-badge">
                <span className="badge-icon"></span>
                <span className="badge-code">{result.code}</span>
              </div>
              <div className={`status-indicator ${getStatusInfo(result.is_active).className}`}>
                {getStatusInfo(result.is_active).text}
              </div>
            </div>
            
            <div className="card-body">
              <div className="standard-title-section">
                <h2 className="standard-name">{result.name}</h2>
                <div className="standard-meta">
                  <span className="meta-item">
                    <span className="meta-icon">№</span>
                    <span className="meta-label">ID:</span>
                    <span className="meta-value">{result.id}</span>
                  </span>
                  <span className="meta-item">
                    <span className="meta-icon"></span>
                    <span className="meta-label">Категория:</span>
                    <span className="meta-value">{result.category}</span>
                  </span>
                </div>
              </div>
              
              <div className="standard-description">
                <h3 className="section-title">
                  <span className="title-icon"></span>
                  Описание стандарта
                </h3>
                <div className="description-text">
                  {result.description}
                </div>
              </div>
              
              <div className="requirements-section">
                <h3 className="section-title">
                  <span className="title-icon"></span>
                  Требования стандарта
                </h3>
                
                {result.requirements ? (
                  <div className="requirements-content">
                    {renderRequirements(result.requirements)}
                  </div>
                ) : (
                  <div className="no-requirements">
                    <span className="no-data-icon"></span>
                    <p>Требования не указаны</p>
                  </div>
                )}
              </div>
              
              <div className="status-info-card">
                <div className="status-card-header">
                  <span className="status-icon">!</span>
                  <span>Информация о статусе</span>
                </div>
                <p className="status-description">
                  {getStatusInfo(result.is_active).description}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const renderRequirements = (requirements) => {
  if (Array.isArray(requirements)) {
    return (
      <ul className="requirements-list">
        {requirements.map((req, index) => (
          <li key={index} className="requirement-item">
            <span className="requirement-marker"></span>
            <span className="requirement-text">
              {typeof req === 'object' ? JSON.stringify(req) : req}
            </span>
          </li>
        ))}
      </ul>
    );
  } else if (typeof requirements === 'object') {
    return (
      <div className="requirements-object">
        {Object.entries(requirements).map(([key, value]) => (
          <div key={key} className="requirement-group">
            <h4 className="requirement-group-title">
              <span className="group-icon"></span>
              {key}
            </h4>
            {Array.isArray(value) ? (
              <ul className="nested-list">
                {value.map((item, index) => (
                  <li key={index} className="nested-item">
                    <span className="nested-marker">→</span>
                    <span className="nested-text">{item}</span>
                  </li>
                ))}
              </ul>
            ) : typeof value === 'object' ? (
              <pre className="json-view">{JSON.stringify(value, null, 2)}</pre>
            ) : (
              <p className="requirement-text">{value}</p>
            )}
          </div>
        ))}
      </div>
    );
  } else {
    return <p className="requirements-text">{String(requirements)}</p>;
  }
};

function getPlaceholder(type) {
  switch (type) {
    case 'id': return 'Введите ID стандарта (например: 2)';
    case 'code': return 'Введите код стандарта (например: НП-001-97)';
    case 'name': return 'Введите название стандарта';
    default: return 'Введите значение для поиска';
  }
}

export default StandardPage;