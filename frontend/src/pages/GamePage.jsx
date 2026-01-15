import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import gameService from '../api/gameService';
import { EventDisplay } from '../components/EventDisplay';
import { ContextDisplay } from '../components/ContextDisplay';
import { InputForm } from '../components/InputForm';
import { EventHistory } from '../components/EventHistory';
import { LanguageSwitcher } from '../components/LanguageSwitcher';

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
      const response = await gameService.startGame(i18n.language);
      setCurrentStep(response.step);
      setContext(response.step.context);
      setHistory([response.step]);
    } catch (err) {
      handleError(err);
      console.error('Failed to initialize game:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitInput = async (input) => {
    try {
      setLoading(true);
      setError(null);
      const response = await gameService.processStep(input, i18n.language);
      setCurrentStep(response.step);
      setContext(response.step.context);
      setHistory((prev) => [...prev, response.step]);
    } catch (err) {
      handleError(err);
      console.error('Failed to process step:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRollback = async (stepIndex) => {
    try {
      setLoading(true);
      setError(null);
      const response = await gameService.rollback(stepIndex, i18n.language);
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

  return (
    <div className="game-page">
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
          <EventDisplay event={currentStep?.event} isLoading={loading} />
          <InputForm onSubmit={handleSubmitInput} disabled={loading} />
        </div>

        <aside className="right-panel">
          <ContextDisplay context={context} />
          <EventHistory events={history.slice(0, -1)} onRollback={handleRollback} />
        </aside>
      </main>
    </div>
  );
}
