import React, { useState } from 'react';
import './LoginPage.css';
import { api } from '../services/api';

function LoginPage({ onLogin, onSwitchToRegister }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            console.log('Логин с:', { email, password });
            const response = await api.login(email, password);
            console.log('Ответ от сервера:', response); 
            
            if (response.access_token) {
                api.setToken(response.access_token);
                
                try {
                    const profile = await api.getProfile();
                    onLogin(profile);
                } catch (profileErr) {
                    onLogin({ email, name: email.split('@')[0] });
                }
            } else {
                throw new Error('Неверный ответ от сервера');
            }
        } catch (err) {
            console.error('Ошибка при входе:', err);
            setError('Неверный email или пароль');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <h2>Вход в систему</h2>
                
                {error && (
                    <div className="error-message">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            placeholder="Введите ваш email"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Пароль</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="Введите пароль"
                        />
                    </div>

                    <button 
                        type="submit" 
                        className="login-button"
                        disabled={loading}
                    >
                        {loading ? 'Вход...' : 'Войти'}
                    </button>
                </form>

                <div className="login-footer">
                    <p>Нет аккаунта?</p>
                    <button 
                        className="switch-button"
                        onClick={onSwitchToRegister}
                    >
                        Зарегистрироваться
                    </button>
                </div>
            </div>
        </div>
    );
}

export default LoginPage;