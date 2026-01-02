import { useTranslation } from 'react-i18next';

export function EventHistory({ events, onRollback }) {
  const { t } = useTranslation();

  if (!events || events.length === 0) {
    return <div className="event-history empty">{t('history.empty')}</div>;
  }

  const handleRollback = (index) => {
    if (window.confirm(t('history.rollbackConfirm', { step: index + 1 }))) {
      onRollback(index);
    }
  };

  return (
    <div className="event-history">
      <h3>{t('history.title')}</h3>
      <div className="history-list">
        {events.map((step, index) => (
          <div key={step.id} className="history-item">
            <div className="input-label">{t('history.you')}{step.userInput}</div>
            <div className="event-summary">
              {step.event.description.substring(0, 100)}...
            </div>
            <button 
              className="rollback-button" 
              onClick={() => handleRollback(index)}
              title={t('history.rollback')}
            >
              {t('history.rollback')}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
