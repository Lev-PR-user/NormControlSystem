import React, { useState, useEffect } from 'react';
import HomePage from './page/HomePage';
import StandardPage from './page/StandardPage';
import DocumentUploadPage from './page/DocumentUploadPage';
import LoginPage from './page/LoginPage';
import RegisterPage from './page/RegisterPage';
import ProfilePage from './page/ProfilePage';
import { api } from './services/api';
import './App.css';

function App() {
    const [activePage, setActivePage] = useState('home');
    const [authMode, setAuthMode] = useState('login');
    const [currentUser, setCurrentUser] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            api.getProfile()
                .then(user => {
                    setCurrentUser(user);
                    setAuthMode(null);
                })
                .catch(err => {
                    localStorage.removeItem('token');
                    setAuthMode('login');
                });
        } else {
            setAuthMode('login');
        }
    }, []);

    const handleLogin = (user) => {
        setCurrentUser(user);
        setAuthMode(null);
        setActivePage('home');
    };

    const handleRegister = (user) => {
        setCurrentUser(user);
        setAuthMode(null);
        setActivePage('home');
    };

    const handleLogout = () => {
        api.removeToken();
        setCurrentUser(null);
        setAuthMode('login');
        setActivePage('home');
    };

    const handleGoToHome = () => {
        if (currentUser) {
            setActivePage('home');
        } else {
            setAuthMode('login');
        }
    };

    if (!currentUser && (authMode === 'login' || authMode === 'register')) {
        return authMode === 'login' ? (
            <LoginPage 
                onLogin={handleLogin}
                onSwitchToRegister={() => setAuthMode('register')}
                onGoToHome={handleGoToHome}
            />
        ) : (
            <RegisterPage 
                onRegister={handleRegister}
                onSwitchToLogin={() => setAuthMode('login')}
                onGoToHome={handleGoToHome}
            />
        );
    }

    if (authMode === 'profile') {
        return (
            <ProfilePage 
                user={currentUser}
                onLogout={handleLogout}
                onGoToHome={handleGoToHome}
            />
        );
    }

    return (
        <div className="App">
            <div className="top-bar">
                <div className="top-bar-left">
                    <h1 className="app-title">Система нормоконтроля</h1>
                </div>
                
                <div className="top-bar-right">
                    {currentUser ? (
                        <div className="user-profile-mini" onClick={() => setActivePage('profile')}>
                            <div className="mini-avatar">
                                {currentUser.name ? currentUser.name.charAt(0).toUpperCase() : 'U'}
                            </div>
                            <span className="mini-username">{currentUser.name || 'Профиль'}</span>
                        </div>
                    ) : (
                        <button 
                            className="login-mini-button"
                            onClick={() => setAuthMode('login')}
                        >
                            Войти
                        </button>
                    )}
                </div>
            </div>

            <div className="main-content">                
                <div className="page-content">
                    {activePage === 'home' && <HomePage user={currentUser} />}
                    {activePage === 'standards' && <StandardPage user={currentUser} />}
                    {activePage === 'documents' && <DocumentUploadPage user={currentUser} />}
                    {activePage === 'profile' && <ProfilePage user={currentUser} onLogout={handleLogout} />}
                </div>
            </div>

            <nav className="bottom-nav">
                <button 
                    className={`nav-item ${activePage === 'home' ? 'active' : ''}`}
                    onClick={() => setActivePage('home')}
                >
                    <span className="nav-icon">🏠︎</span>
                    <span className="nav-label">Главная</span>
                </button>
                
                <button 
                    className={`nav-item ${activePage === 'standards' ? 'active' : ''}`}
                    onClick={() => setActivePage('standards')}
                >
                    <span className="nav-icon">📋</span>
                    <span className="nav-label">Стандарты</span>
                </button>
                
                <button 
                    className={`nav-item ${activePage === 'documents' ? 'active' : ''}`}
                    onClick={() => setActivePage('documents')}
                >
                    <span className="nav-icon">📄</span>
                    <span className="nav-label">Документы</span>
                </button>
                
                <button 
                    className={`nav-item ${activePage === 'profile' ? 'active' : ''}`}
                    onClick={() => setActivePage('profile')}
                >
                    <span className="nav-icon">👨‍💼</span>
                    <span className="nav-label">Профиль</span>
                </button>
            </nav>
        </div>
    );
}

export default App;