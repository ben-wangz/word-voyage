const API_BASE = '/api/game';

export interface ContextField {
  value: any;
  type: 'int' | 'double' | 'string' | 'boolean' | 'object' | 'array';
  name: string;
  description?: string;
  min?: number;
  max?: number;
}

export interface Step {
  id: string;
  timestamp: number;
  userInput: string;
  inputType: 'action' | 'question';
  context: {
    state: Record<string, ContextField>;
    gameTime: number;
  };
  event: {
    description: string;
    contextChanges: Record<string, ContextField | null>;
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
  private readonly SESSION_KEY = 'wordvoyage_session_id';

  saveSessionId(sessionId: string): void {
    localStorage.setItem(this.SESSION_KEY, sessionId);
  }

  getSavedSessionId(): string | null {
    return localStorage.getItem(this.SESSION_KEY);
  }

  clearSessionId(): void {
    localStorage.removeItem(this.SESSION_KEY);
  }

  private handleError(response: Response): never {
    if (response.status === 401) {
      throw new Error('SESSION_EXPIRED');
    }
    if (response.status === 403) {
      throw new Error('ACCESS_DENIED');
    }
    throw new Error(`Request failed: ${response.statusText}`);
  }

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
      credentials: 'include',
    });

    if (!response.ok) {
      this.handleError(response);
    }

    return response.json();
  }

  async processStep(input: string, language?: string): Promise<GameResponse> {
    const url = new URL(`${window.location.origin}${API_BASE}/step`);
    if (language) {
      url.searchParams.append('lang', language);
    }

    const response = await fetch(url.toString(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ input }),
    });

    if (!response.ok) {
      this.handleError(response);
    }

    return response.json();
  }

  async rollback(stepIndex: number, language?: string): Promise<GameResponse> {
    const url = new URL(`${window.location.origin}${API_BASE}/rollback`);
    if (language) {
      url.searchParams.append('lang', language);
    }

    const response = await fetch(url.toString(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ stepIndex }),
    });

    if (!response.ok) {
      this.handleError(response);
    }

    return response.json();
  }

  async getContext(): Promise<any> {
    const response = await fetch(`${API_BASE}/context`, {
      method: 'GET',
      credentials: 'include',
    });

    if (!response.ok) {
      this.handleError(response);
    }

    return response.json();
  }

  async getHistory(): Promise<{ steps: Step[] }> {
    const response = await fetch(`${API_BASE}/history`, {
      method: 'GET',
      credentials: 'include',
    });

    if (!response.ok) {
      this.handleError(response);
    }

    return response.json();
  }

  async resumeGame(): Promise<{ context: any; history: Step[] } | null> {
    try {
      const [contextData, historyData] = await Promise.all([
        this.getContext(),
        this.getHistory(),
      ]);

      if (!contextData || !historyData || !historyData.steps || historyData.steps.length === 0) {
        return null;
      }

      return {
        context: contextData.context,
        history: historyData.steps,
      };
    } catch (error) {
      console.error('Failed to resume game:', error);
      return null;
    }
  }
}

export default new GameService();
