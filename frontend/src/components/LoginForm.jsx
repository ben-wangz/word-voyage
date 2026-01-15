import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export function LoginForm({ onSubmit, onSwitchToRegister }) {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError(t('auth.errors.emailPasswordRequired', 'Email and password required'));
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
      <h2 className="auth-form-title">{t('auth.login', 'Login')}</h2>
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

        {error && <div className="error-message">{error}</div>}

        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? t('auth.loggingIn', 'Logging in...') : t('auth.login', 'Login')}
        </button>
      </form>

      <div className="auth-form-footer">
        <span>{t('auth.noAccount', "Don't have an account?")}</span>
        <button type="button" className="btn-link" onClick={onSwitchToRegister}>
          {t('auth.register', 'Register')}
        </button>
      </div>
    </div>
  );
}
