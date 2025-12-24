import { config } from '../config.ts';
import { LLMGenerationRequest, LLMGenerationResponse, SchemaField, ContextField, Context } from '../types/index.ts';

/**
 * LLM Client Service
 * Encapsulates HTTP communication with the LLM service
 */
export class LLMClient {
  private serviceUrl: string;
  private timeout: number;

  constructor() {
    this.serviceUrl = config.llm.serviceUrl;
    this.timeout = config.llm.timeout;
  }

  /**
   * Generate structured data using LLM service
   */
  async generateStructured(request: LLMGenerationRequest): Promise<LLMGenerationResponse> {
    try {
      console.log(`[LLMClient] Sending request to ${this.serviceUrl}/generate_structured`);
      console.log(`[LLMClient] Request context fields: ${Object.keys(request.context).length}`);
      console.log(`[LLMClient] Request user_input: ${request.user_input}`);

      const response = await fetch(`${this.serviceUrl}/generate_structured`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.timeout),
      });

      console.log(`[LLMClient] Response status: ${response.status}`);

      if (!response.ok) {
        const responseText = await response.text();
        console.error(`[LLMClient] Error response body: ${responseText}`);
        throw new Error(`LLM service returned ${response.status}: ${response.statusText}`);
      }

      const responseText = await response.text();
      console.log(`[LLMClient] Raw response: ${responseText.substring(0, 500)}`);

      let data: LLMGenerationResponse;
      try {
        data = JSON.parse(responseText);
      } catch (parseError) {
        console.error(`[LLMClient] Failed to parse JSON response: ${parseError}`);
        console.error(`[LLMClient] Response text: ${responseText}`);
        throw parseError;
      }

      console.log(`[LLMClient] Response success: ${data.success}`);
      if (!data.success) {
        console.error(`[LLMClient] LLM error: ${data.error_code} - ${data.message}`);
      }

      return data;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`LLM service call failed: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Build LLM request from game context
   */
  buildRequest(
    basePrompt: string,
    context: Context,
    userInput: string,
    inputType: 'action' | 'question',
    preLogSummary?: { summary: string; recent_events: string[] }
  ): LLMGenerationRequest {
    // Build user-specific prompt instruction
    const userPromptInstruction = this.buildUserPromptInstruction(inputType);
    const fullPrompt = `${basePrompt}\n\n${userPromptInstruction}`;

    // Define output schema for event generation
    const schema = this.buildEventSchema();

    // Convert TypeScript camelCase to snake_case for Python service
    const preLogSummaryForService = preLogSummary
      ? {
          summary: preLogSummary.summary,
          recent_events: preLogSummary.recent_events,
        }
      : undefined;

    return {
      prompt: fullPrompt,
      context: context.state,
      pre_log_summary: preLogSummaryForService,
      user_input: userInput,
      schema,
      stream: false,
    };
  }

  /**
   * Build user-specific prompt instruction based on input type
   * Note: userInput placeholder will be filled by the LLM service from request
   */
  private buildUserPromptInstruction(inputType: 'action' | 'question'): string {
    if (inputType === 'action') {
      return `Generate an event describing what happens in the game world as a result of the player's action. Update only the context fields that change.`;
    } else {
      // 'question' type - mechanism questioning
      return `Understand the player's feedback about game mechanics and generate an event that reflects the adjustment to the game world. Update context fields according to the player's suggestions.`;
    }
  }

  /**
   * Build schema definition for event generation output
   */
  private buildEventSchema(): { [key: string]: SchemaField } {
    return {
      event_description: {
        type: 'string',
        description: 'Narrative description of what happens in the game world. Should be 3-5 sentences, vivid and immersive, directly responding to the player action.',
      },
      context_changes: {
        type: 'object',
        description: 'Object containing only the context fields that changed. Each field should have {value, type, description}. Use null to remove a field.',
      },
    };
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
