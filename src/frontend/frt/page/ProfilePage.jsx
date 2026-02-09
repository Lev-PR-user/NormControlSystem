import React, { useState, useEffect } from 'react';
import './ProfilePage.css';
import { api } from '../services/api';

function ProfilePage({ user, onLogout }) {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        loadProfile();
    });

    const loadProfile = async () => {
        try {
            const profileData = await api.getProfile();
            console.log('Профиль получен:', profileData);
            setProfile(profileData);
        } catch (err) {
            console.error('Ошибка загрузки профиля:', err);
            if (user) {
                setProfile(user);
            } else {
                setError('Не удалось загрузить профиль. Попробуйте войти заново.');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        api.removeToken();
        onLogout();
    };

    if (loading) {
        return (
            <div className="profile-page-container">
                <div className="profile-content">
                    <div className="loading-spinner">
                        <div className="spinner"></div>
                        <p>Загрузка профиля...</p>
                    </div>
                </div>
            </div>
        );
    }

    const displayProfile = profile || user;

    return (
        <div className="profile-page-container">
            <div className="profile-content">
                {error && (
                    <div className="info-message">
                        <span>ℹ️</span>
                        <p>{error}</p>
                    </div>
                )}

                <div className="profile-header-card">
                    <div className="profile-avatar-section">
                        <div className="avatar-circle">
                            {displayProfile?.name ? displayProfile.name.charAt(0).toUpperCase() : 'U'}
                        </div>
                        <div className="avatar-info">
                            <h2 className="profile-name">{displayProfile?.name || 'Пользователь'}</h2>
                            <p className="profile-email">{displayProfile?.email || 'Email не указан'}</p>
                        </div>
                    </div>
                    
                    <button onClick={handleLogout} className="logout-button-profile">
                        Выйти
                    </button>
                </div>

                <div className="profile-info-section">
                    <h3 className="section-title">Информация об аккаунте</h3>
                    
                    <div className="info-grid">
                        <div className="info-row">
                            <span className="info-label">Имя пользователя:</span>
                            <span className="info-value">{displayProfile?.name || 'Не указано'}</span>
                        </div>
                        
                        <div className="info-row">
                            <span className="info-label">Email:</span>
                            <span className="info-value">{displayProfile?.email || 'Не указан'}</span>
                        </div>
                    </div>
                </div>

                <div className="profile-footer-section">
                    <p className="account-date">
                        Аккаунт создан: {displayProfile?.created_at ? 
                            new Date(displayProfile.created_at).toLocaleDateString('ru-RU') : 
                            new Date().toLocaleDateString('ru-RU')}
                    </p>
                </div>
            </div>
        </div>
    );
}

export default ProfilePage;