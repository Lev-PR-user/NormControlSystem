import React, { useState } from 'react';
import './RegisterPage.css';
import { api } from '../services/api';

function RegisterPage({ onRegister, onSwitchToLogin }) {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.confirmPassword) {
            setError('Пароли не совпадают');
            return;
        }

        if (formData.password.length < 6) {
            setError('Пароль должен быть не менее 6 символов');
            return;
        }

        setLoading(true);

        try {
            const { confirmPassword, ...userData } = formData;
            
            console.log('Отправка данных:', userData);
            
            await api.register(userData);
            setSuccess(true);
            
            setTimeout(async () => {
                try {
                    const response = await api.login(formData.email, formData.password);
                    console.log('Ответ от сервера при логине:', response); 
                    api.setToken(response.access_token);
                    onRegister(response.user || { name: formData.name, email: formData.email });
                } catch (loginErr) {
                    console.error('Ошибка при логине:', loginErr);
                    onSwitchToLogin();
                }
            }, 2000);
            
        } catch (err) {
            console.error('Ошибка при регистрации:', err);
            setError(err.message || 'Ошибка при регистрации');
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className="register-container">
                <div className="register-card success">
                    <h2>Регистрация успешна!</h2>
                    <p>Вы будете автоматически перенаправлены...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="register-container">
            <div className="register-card">
                <h2>Регистрация</h2>
                
                {error && (
                    <div className="error-message">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="name">Имя</label>
                        <input
                            type="text"
                            id="name"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            required
                            placeholder="Введите ваше имя"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                            placeholder="Введите ваш email"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Пароль</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            placeholder="Придумайте пароль (минимум 6 символов)"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="confirmPassword">Подтверждение пароля</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            required
                            placeholder="Повторите пароль"
                        />
                    </div>

                    <button 
                        type="submit" 
                        className="register-button"
                        disabled={loading}
                    >
                        {loading ? 'Регистрация...' : 'Зарегистрироваться'}
                    </button>
                </form>

                <div className="register-footer">
                    <p>Уже есть аккаунт?</p>
                    <button 
                        className="switch-button"
                        onClick={onSwitchToLogin}
                    >
                        Войти
                    </button>
                </div>
            </div>
        </div>
    );
}

export default RegisterPage;