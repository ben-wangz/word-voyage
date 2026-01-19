import { useTranslation } from 'react-i18next';

export function EventDisplay({ event, isLoading, gameTime }) {
  const { t } = useTranslation();

  const formatGameTime = (seconds) => {
    if (seconds === undefined || seconds === null) return '0 hours';
    const hours = Math.floor(seconds / 3600);
    return `${hours} ${hours === 1 ? 'hour' : 'hours'}`;
  };

  if (!event) {
    return (
      <div className="event-display empty">
        <p>{t('event.waiting')}</p>
        {gameTime !== undefined && (
          <div className="game-time">
            <span className="game-time-label">{t('context.gameTime')}</span>
            <span className="game-time-value">{formatGameTime(gameTime)}</span>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="event-display">
      {gameTime !== undefined && (
        <div className="game-time">
          <span className="game-time-label">{t('context.gameTime')}:</span>
          <span className="game-time-value">{formatGameTime(gameTime)}</span>
        </div>
      )}
      <div className="event-content">
        <p>{event.description}</p>
      </div>
      {isLoading && (
        <div className="loading">
          <span className="spinner"></span> {t('event.thinking')}
        </div>
      )}
    </div>
  );
}
