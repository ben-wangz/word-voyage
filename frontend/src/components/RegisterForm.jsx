import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export function RegisterForm({ onSubmit, onSwitchToLogin }) {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email || !password || !confirmPassword) {
      setError(t('auth.errors.allFieldsRequired', 'All fields are required'));
      return;
    }

    if (!validateEmail(email)) {
      setError(t('auth.errors.invalidEmail', 'Invalid email format'));
      return;
    }

    if (password.length < 6) {
      setError(t('auth.errors.passwordTooShort', 'Password must be at least 6 characters'));
      return;
    }

    if (password !== confirmPassword) {
      setError(t('auth.errors.passwordMismatch', 'Passwords do not match'));
      return;
    }

    try {
      setLoading(true);
      await onSubmit(email, password);
    } catch (err) {
      setError(t(`auth.errors.${err.message}`, err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form">
      <h2 className="auth-form-title">{t('auth.register', 'Register')}</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">{t('auth.email', 'Email')}</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder={t('auth.emailPlaceholder', 'Enter your email')}
            disabled={loading}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">{t('auth.password', 'Password')}</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder={t('auth.passwordPlaceholder', 'Enter your password')}
            disabled={loading}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="confirmPassword">{t('auth.confirmPassword', 'Confirm Password')}</label>
          <input
            id="confirmPassword"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder={t('auth.confirmPasswordPlaceholder', 'Confirm your password')}
            disabled={loading}
            required
          />
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? t('auth.registering', 'Registering...') : t('auth.register', 'Register')}
        </button>
      </form>

      <div className="auth-form-footer">
        <span>{t('auth.hasAccount', 'Already have an account?')}</span>
        <button type="button" className="btn-link" onClick={onSwitchToLogin}>
          {t('auth.login', 'Login')}
        </button>
      </div>
    </div>
  );
}
