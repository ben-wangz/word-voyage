import { config } from '../../config.ts';
import { logger } from '../../utils/logger.ts';

/**
 * Message format for LLM API
 */
export type LLMMessage = {
  role: 'system' | 'user' | 'assistant';
  content: string;
};

/**
 * LLM completion request
 */
export type LLMCompletionRequest = {
  messages: LLMMessage[];
  model?: string;
  max_tokens?: number;
  response_format?: { type: 'json_object' | 'text' };
};

/**
 * LLM completion response
 */
export type LLMCompletionResponse = {
  content: string;
  reasoning_content?: string;
};

/**
 * LLM Client Service
 * Encapsulates HTTP communication with the LLM proxy service
 */
export class LLMClient {
  private serviceUrl: string;
  private timeout: number;

  constructor() {
    this.serviceUrl = config.llm.serviceUrl;
    this.timeout = config.llm.timeout;
  }

  /**
   * Complete using LLM proxy service
   */
  async complete(request: LLMCompletionRequest): Promise<LLMCompletionResponse> {
    try {
      logger.info(`[LLMClient] Sending request to ${this.serviceUrl}/complete`);
      logger.debug(`[LLMClient] Request details:`, {
        messageCount: request.messages.length,
        model: request.model,
        maxTokens: request.max_tokens,
      });

      const response = await fetch(`${this.serviceUrl}/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.timeout),
      });

      logger.info(`[LLMClient] Response status: ${response.status}`);

      if (!response.ok) {
        const responseText = await response.text();
        logger.error(`[LLMClient] Error response body: ${responseText}`);
        throw new Error(`LLM service returned ${response.status}: ${response.statusText}`);
      }

      const responseText = await response.text();
      logger.debug(`[LLMClient] Full raw response:`, responseText);

      let data: LLMCompletionResponse;
      try {
        data = JSON.parse(responseText);
      } catch (parseError) {
        logger.error(`[LLMClient] Failed to parse JSON response: ${parseError}`);
        logger.error(`[LLMClient] Response text: ${responseText}`);
        throw parseError;
      }

      logger.info(`[LLMClient] Response received successfully`);
      logger.debug(`[LLMClient] Content length: ${data.content?.length || 0}`);

      return data;
    } catch (error) {
      if (error instanceof Error) {
        logger.error(`[LLMClient] LLM service call failed: ${error.message}`);
        throw new Error(`LLM service call failed: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Health check with LLM service
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.serviceUrl}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000),
      });

      return response.ok;
    } catch {
      return false;
    }
  }
}

/**
 * Singleton instance
 */
export const llmClient = new LLMClient();
