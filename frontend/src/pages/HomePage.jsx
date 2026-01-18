import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../utils/authContext';
import { LoginForm } from '../components/LoginForm';
import { RegisterForm } from '../components/RegisterForm';
import { LanguageSwitcher } from '../components/LanguageSwitcher';
import './HomePage.css';

export function HomePage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { login, register, isAuthenticated } = useAuth();
  const [mode, setMode] = useState('login');

  useEffect(() => {
    if (location.state?.mode === 'register') {
      setMode('register');
    }
  }, [location.state]);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/game');
    }
  }, [isAuthenticated, navigate]);

  const handleLogin = async (email, password) => {
    await login(email, password);
    navigate('/game');
  };

  const handleRegister = async (email, password) => {
    await register(email, password);
    navigate('/game');
  };

  const handleAnonymousPlay = () => {
    navigate('/game');
  };

  return (
    <div className="home-page">
      <div className="home-header">
        <h1 className="home-title">
          <img src="/vite.svg" alt="WordVoyage Logo" className="title-logo" />
          {t('app.title', 'Word Voyage')}
        </h1>
        <LanguageSwitcher />
      </div>

      <div className="home-content">
        <div className="auth-container">
          {mode === 'login' ? (
            <LoginForm
              onSubmit={handleLogin}
              onSwitchToRegister={() => setMode('register')}
            />
          ) : (
            <RegisterForm
              onSubmit={handleRegister}
              onSwitchToLogin={() => setMode('login')}
            />
          )}

          <div className="anonymous-play-section">
            <div className="divider">
              <span>{t('auth.or', 'OR')}</span>
            </div>
            <button className="btn-secondary btn-anonymous" onClick={handleAnonymousPlay}>
              {t('auth.anonymousPlay', 'Play as Guest')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
