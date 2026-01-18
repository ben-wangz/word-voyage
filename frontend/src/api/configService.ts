const API_BASE = '/api/config';

export interface UserInputLimits {
  zh: { chars: number };
  en: { chars: number };
}

export interface ConfigResponse {
  userInputLimits: UserInputLimits;
}

class ConfigService {
  private config: ConfigResponse | null = null;

  async fetchConfig(): Promise<ConfigResponse> {
    if (this.config) {
      return this.config;
    }

    const response = await fetch(`${window.location.origin}${API_BASE}`, {
      method: 'GET',
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch config: ${response.statusText}`);
    }

    this.config = await response.json();
    return this.config;
  }

  getUserInputLimit(language: string): number {
    if (!this.config) {
      // Fallback values if config not loaded
      return language === 'zh' ? 150 : 1200;
    }

    const lang = language.startsWith('zh') ? 'zh' : 'en';
    return this.config.userInputLimits[lang].chars;
  }

  clearCache(): void {
    this.config = null;
  }
}

export default new ConfigService();
