import React, { useState } from 'react';
import HomePage from './page/HomePage';
import StandardPage from './page/StandardPage';
import DocumentUploadPage from './page/DocumentUploadPage';
import './App.css';

function App() {
  const [activePage, setActivePage] = useState('home');
  const [backendHealth, setBackendHealth] = useState(null);

  const checkBackend = async () => {
    try {
      const response = await fetch('http://localhost:8000/');
      const data = await response.json();
      setBackendHealth(data);
    } catch (error) {
      setBackendHealth({ error: 'Бэкенд не отвечает' });
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Система контроля нормативных документов</h1>
        
        <div className="navigation">
          <button 
            className={`nav-button ${activePage === 'home' ? 'active' : ''}`}
            onClick={() => setActivePage('home')}
          >
            Главная
          </button>
          <button 
            className={`nav-button ${activePage === 'standards' ? 'active' : ''}`}
            onClick={() => setActivePage('standards')}
          >
            Стандарты
          </button>
          <button 
            className={`nav-button ${activePage === 'documents' ? 'active' : ''}`}
            onClick={() => setActivePage('documents')}
          >
            Проверка документов
          </button>
        </div>

        <div className="backend-check">
          <button onClick={checkBackend} className="check-button">
            Проверить подключение к серверу
          </button>
          {backendHealth && (
            <div className="backend-status">
              {backendHealth.message ? (
                <p className="status-success">Сервер работает: {backendHealth.message}</p>
              ) : (
                <p className="status-error">Ошибка: {backendHealth.error}</p>
              )}
            </div>
          )}
        </div>

        <div className="page-content">
          {activePage === 'home' && <HomePage />}
          {activePage === 'standards' && <StandardPage />}
          {activePage === 'documents' && <DocumentUploadPage />}
        </div>
      </header>
    </div>
  );
}

export default App;