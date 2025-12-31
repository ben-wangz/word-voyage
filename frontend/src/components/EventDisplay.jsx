import { useTranslation } from 'react-i18next';

export function EventDisplay({ event, isLoading }) {
  const { t } = useTranslation();

  if (!event) {
    return (
      <div className="event-display empty">
        <p>{t('event.waiting')}</p>
      </div>
    );
  }

  return (
    <div className="event-display">
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
