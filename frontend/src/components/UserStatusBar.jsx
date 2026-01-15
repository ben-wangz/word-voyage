import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../utils/authContext';
import './UserStatusBar.css';

export function UserStatusBar() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { user, isGuest, logout } = useAuth();

  const handleGuestClick = () => {
    navigate('/', { state: { mode: 'register' } });
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  if (!user) {
    return null;
  }

  return (
    <div className="user-status-bar">
      {isGuest ? (
        <div className="user-status guest-mode" onClick={handleGuestClick}>
          <span className="user-icon">👤</span>
          <span className="user-label">{t('auth.guestMode', 'Guest Mode')}</span>
          <div className="guest-tooltip">
            {t('auth.guestModeWarning', 'Guest mode cannot save progress long-term. Click to register.')}
          </div>
        </div>
      ) : (
        <div className="user-status authenticated">
          <span className="user-icon">👤</span>
          <span className="user-email">{user.email}</span>
          <button className="btn-logout" onClick={handleLogout}>
            {t('auth.logout', 'Logout')}
          </button>
        </div>
      )}
    </div>
  );
}
