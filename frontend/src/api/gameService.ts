const API_BASE = '/api/game';

export interface Step {
  id: string;
  timestamp: number;
  userInput: string;
  inputType: 'action' | 'question';
  context: {
    state: Record<string, any>;
    gameTime: number;
  };
  event: {
    description: string;
    contextChanges: Record<string, any>;
  };
  preLogSummary: {
    summary: string;
    recentEvents: string[];
    generatedAt: number;
  };
}

export interface GameResponse {
  step: Step;
  sessionId: string;
}

class GameService {
  async startGame(language?: string): Promise<GameResponse> {
    const url = new URL(`${window.location.origin}${API_BASE}/start`);
    if (language) {
      url.searchParams.append('lang', language);
    }

    const response = await fetch(url.toString(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to start game: ${response.statusText}`);
    }

    return response.json();
  }

  async processStep(input: string, sessionId: string, language?: string): Promise<GameResponse> {
    const url = new URL(`${window.location.origin}${API_BASE}/step`);
    if (language) {
      url.searchParams.append('lang', language);
    }

    const response = await fetch(url.toString(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ input, sessionId }),
    });

    if (!response.ok) {
      throw new Error(`Failed to process step: ${response.statusText}`);
    }

    return response.json();
  }

  async getContext(sessionId: string): Promise<any> {
    const response = await fetch(`${API_BASE}/context/${sessionId}`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`Failed to get context: ${response.statusText}`);
    }

    return response.json();
  }

  async getHistory(sessionId: string): Promise<{ steps: Step[] }> {
    const response = await fetch(`${API_BASE}/history/${sessionId}`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`Failed to get history: ${response.statusText}`);
    }

    return response.json();
  }
}

export default new GameService();
