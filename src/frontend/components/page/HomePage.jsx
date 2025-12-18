import React from 'react';
import './HomePage.css';

const HomePage = () => {
  return (
    <div className="home-page">
      <h2>Добро пожаловать в систему контроля документов</h2>
      
      <div className="features">
        <div className="feature-card">
          <div className="feature-icon"></div>
          <h3>Проверка документов</h3>
          <p>Загрузите документ для автоматической проверки на соответствие стандартам</p>
        </div>
        
        <div className="feature-card">
          <div className="feature-icon"></div>
          <h3>Поиск стандартов</h3>
          <p>Найдите стандарт по ID, коду или названию в базе данных</p>
        </div>
        
        <div className="feature-card">
          <div className="feature-icon"></div>
          <h3>Контроль качества</h3>
          <p>Проверка терминологии и соответствия нормативным документам</p>
        </div>
      </div>
      
      <div className="instructions">
        <h3>Как пользоваться системой:</h3>
        <ol>
          <li>Перейдите в раздел "Проверка документов" для загрузки файла</li>
          <li>Выберите файл формата .txt, .doc, .docx или .pdf</li>
          <li>Дождитесь завершения проверки системы</li>
          <li>Просмотрите результаты проверки и рекомендации</li>
          <li>Используйте раздел "Стандарты" для поиска нормативных документов</li>
        </ol>
      </div>
    </div>
  );
};

export default HomePage;