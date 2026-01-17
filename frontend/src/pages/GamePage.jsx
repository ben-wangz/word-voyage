import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import gameService from '../api/gameService';
import { EventDisplay } from '../components/EventDisplay';
import { ContextDisplay } from '../components/ContextDisplay';
import { InputForm } from '../components/InputForm';
import { EventHistory } from '../components/EventHistory';
import { LanguageSwitcher } from '../components/LanguageSwitcher';
import { UserStatusBar } from '../components/UserStatusBar';

export function GamePage() {
  const { t, i18n } = useTranslation();
  const [currentStep, setCurrentStep] = useState(null);
  const [context, setContext] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    initializeGame();
  }, []);

  const handleError = (err) => {
    if (err.message === 'SESSION_EXPIRED') {
      setError(t('error.sessionExpired'));
    } else if (err.message === 'ACCESS_DENIED') {
      setError(t('error.accessDenied'));
    } else {
      setError(err.message);
    }
  };

  const initializeGame = async () => {
    try {
      setLoading(true);
      setError(null);

      const savedSessionId = gameService.getSavedSessionId();

      if (savedSessionId) {
        console.log('Found saved session, attempting to resume...');
        const resumeData = await gameService.resumeGame();

        if (resumeData && resumeData.history.length > 0) {
          console.log('Successfully resumed game');
          setHistory(resumeData.history);
          setCurrentStep(resumeData.history[resumeData.history.length - 1]);
          setContext(resumeData.context);
          return;
        } else {
          console.log('Resume failed, clearing saved session');
          gameService.clearSessionId();
        }
      }

      console.log('Starting new game...');
      const response = await gameService.startGame(i18n.language);
      gameService.saveSessionId(response.sessionId);
      setCurrentStep(response.step);
      setContext(response.step.context);
      setHistory([response.step]);
    } catch (err) {
      handleError(err);
      console.error('Failed to initialize game:', err);
      gameService.clearSessionId();
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitInput = async (input) => {
    try {
      setLoading(true);
      setError(null);
      const response = await gameService.processStep(input, i18n.language);
      gameService.saveSessionId(response.sessionId);
      setCurrentStep(response.step);
      setContext(response.step.context);
      setHistory((prev) => [...prev, response.step]);
    } catch (err) {
      handleError(err);
      console.error('Failed to process step:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const handleRollback = async (stepIndex) => {
    try {
      setLoading(true);
      setError(null);
      const response = await gameService.rollback(stepIndex, i18n.language);
      gameService.saveSessionId(response.sessionId);
      setCurrentStep(response.step);
      setContext(response.step.context);
      setHistory((prev) => prev.slice(0, stepIndex + 1));
    } catch (err) {
      handleError(err);
      console.error('Failed to rollback:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderContextGrid = () => {
    if (!context) return null;

    const stateEntries = Object.entries(context.state || {});

    const placeholderEntries = [
      ['─', '─'],
      ['•', '•'],
      ['◆', '◆'],
      ['▪', '▪']
    ];

    const totalSlots = Math.ceil(stateEntries.length / 4) * 4;
    const paddedEntries = [...stateEntries];
    let placeholderIndex = 0;

    while (paddedEntries.length < totalSlots) {
      paddedEntries.push(placeholderEntries[placeholderIndex % placeholderEntries.length]);
      placeholderIndex++;
    }

    return (
      <div className="context-display">
        <h3>{t('context.title')}</h3>
        <div className="context-grid">
          {paddedEntries.map((entry, index) => {
            const [key, field] = entry;
            const isPlaceholder = key === '─' || key === '•' || key === '◆' || key === '▪';

            if (isPlaceholder) {
              return (
                <div key={`${key}-${index}`} className="context-item placeholder">
                  <span className="context-key">{key}</span>
                  <span className="context-value">{typeof field === 'object' ? field.value : field}</span>
                </div>
              );
            }

            const isRichField = typeof field === 'object' && field !== null && 'value' in field;
            const value = isRichField ? field.value : field;
            const fieldName = isRichField ? field.name : key;
            const description = isRichField ? field.description : null;
            const min = isRichField && field.min !== undefined && field.min !== null ? field.min : null;
            const max = isRichField && field.max !== undefined && field.max !== null ? field.max : null;

            const hasRange = min !== null && max !== null && typeof value === 'number';
            const percentage = hasRange ? Math.max(0, Math.min(100, ((value - min) / (max - min)) * 100)) : 0;

            const formatValue = (val) => {
              if (val === null || val === undefined) return '';
              if (typeof val === 'object') {
                if (Array.isArray(val)) {
                  return val.join(', ');
                }
                return Object.entries(val)
                  .map(([k, v]) => `${k}: ${v}`)
                  .join(', ');
              }
              return String(val);
            };

            const displayValue = formatValue(value);

            return (
              <div
                key={`${key}-${index}`}
                className="context-item"
                title={description || undefined}
              >
                <span className="context-key">{fieldName}</span>
                {hasRange ? (
                  <div className="context-value-range">
                    <span className="range-min">{min}</span>
                    <div className="range-bar">
                      <div className="range-fill" style={{ width: `${percentage}%` }}></div>
                      <span className="range-value">{value}</span>
                    </div>
                    <span className="range-max">{max}</span>
                  </div>
                ) : (
                  <span className="context-value">{displayValue}</span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="game-page">
      <UserStatusBar />
      <header className="game-header">
        <div>
          <div>
            <h1>{t('app.title')}</h1>
            <p>{t('app.subtitle')}</p>
          </div>
          <LanguageSwitcher />
        </div>
      </header>

      {error && (
        <div className="error-message">
          <strong>{t('error.prefix')}</strong> {error}
        </div>
      )}

      <main className="game-main">
        <div className="left-panel">
          {renderContextGrid()}
          <EventDisplay event={currentStep?.event} isLoading={loading} gameTime={context?.gameTime} />
          <InputForm onSubmit={handleSubmitInput} disabled={loading} />
        </div>

        <aside className="right-panel">
          <EventHistory events={history.slice(0, -1)} onRollback={handleRollback} />
        </aside>
      </main>
    </div>
  );
}
