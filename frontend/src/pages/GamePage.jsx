import { useState, useEffect } from 'react';
import gameService from '../api/gameService';
import { EventDisplay } from '../components/EventDisplay';
import { ContextDisplay } from '../components/ContextDisplay';
import { InputForm } from '../components/InputForm';
import { EventHistory } from '../components/EventHistory';

export function GamePage() {
  const [sessionId, setSessionId] = useState(null);
  const [currentStep, setCurrentStep] = useState(null);
  const [context, setContext] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    initializeGame();
  }, []);

  const initializeGame = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await gameService.startGame();
      setSessionId(response.sessionId);
      setCurrentStep(response.step);
      setContext(response.step.context);
      setHistory([response.step]);
    } catch (err) {
      setError(err.message);
      console.error('Failed to initialize game:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitInput = async (input) => {
    if (!sessionId) return;

    try {
      setLoading(true);
      setError(null);
      const response = await gameService.processStep(input, sessionId);
      setCurrentStep(response.step);
      setContext(response.step.context);
      setHistory((prev) => [...prev, response.step]);
    } catch (err) {
      setError(err.message);
      console.error('Failed to process step:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="game-page">
      <header className="game-header">
        <h1>WordVoyage</h1>
        <p>A text-based sandbox adventure powered by AI</p>
      </header>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      <main className="game-main">
        <div className="left-panel">
          <EventDisplay event={currentStep?.event} isLoading={loading} />
          <InputForm onSubmit={handleSubmitInput} disabled={loading} />
        </div>

        <aside className="right-panel">
          <ContextDisplay context={context} />
          <EventHistory events={history.slice(0, -1)} />
        </aside>
      </main>
    </div>
  );
}
