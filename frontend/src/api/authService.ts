const API_BASE = '/api/auth';

export interface User {
  userId: string;
  email?: string;
  type: 'guest' | 'registered';
}

export interface LoginResponse {
  user: {
    userId: string;
    email: string;
  };
  accessToken: string;
  refreshToken: string;
}

export interface RegisterResponse {
  user: {
    userId: string;
    email: string;
  };
  accessToken: string;
  refreshToken: string;
}

class AuthService {
  private handleError(error: any): never {
    if (error.response) {
      const errorData = error.response;
      throw new Error(errorData.error?.code || errorData.error?.message || 'UNKNOWN_ERROR');
    }
    throw new Error(error.message || 'NETWORK_ERROR');
  }

  async login(email: string, password: string): Promise<LoginResponse> {
    try {
      const response = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw { response: errorData };
      }

      return await response.json();
    } catch (error) {
      return this.handleError(error);
    }
  }

  async register(email: string, password: string): Promise<RegisterResponse> {
    try {
      const response = await fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw { response: errorData };
      }

      return await response.json();
    } catch (error) {
      return this.handleError(error);
    }
  }

  async logout(): Promise<void> {
    try {
      const response = await fetch(`${API_BASE}/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw { response: errorData };
      }
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      const response = await fetch(`${API_BASE}/me`, {
        method: 'GET',
        credentials: 'include',
      });

      if (!response.ok) {
        return null;
      }

      const data = await response.json();

      if (data.user) {
        return {
          userId: data.user.userId,
          email: data.user.email,
          type: data.user.email ? 'registered' : 'guest',
        };
      }

      return null;
    } catch (error) {
      console.error('Failed to get current user:', error);
      return null;
    }
  }
}

export default new AuthService();
