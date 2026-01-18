import { BaseNode, PluginNodeMetadata } from '../core/pluginNode.ts';
import { Context, Event, ContextField, SchemaField } from '../types/index.ts';
import { generateStructured } from '../services/llm/index.ts';
import { estimateTokens } from '../services/llm/tokenEstimator.ts';
import { getI18n } from '../i18n/index.ts';
import { logger } from '../utils/logger.ts';
import { config } from '../config.ts';

/**
 * LLM Core Node
 * Assemble LLM call parameters, parse response, apply context changes
 */
export class LLMCoreNode extends BaseNode {
  metadata: PluginNodeMetadata = {
    id: 'llm-core-node',
    name: 'LLMCoreNode',
    version: '1.0.0',
  };

  async process(request: unknown, context: Context, next: () => Promise<unknown>): Promise<unknown> {
    const req = request as any;
    logger.info(`[LLMCoreNode] Generating event for input: ${req.userInput}`);
    logger.debug(`[LLMCoreNode] Input type: ${req.inputType}, Language: ${req.language || 'en'}`);

    try {
      const language = req.language || 'en';
      const event = await this.generateEvent(
        req.userInput,
        req.inputType,
        context,
        req.preLogSummary,
        language
      );

      logger.info(`[LLMCoreNode] Event generated successfully`);
      logger.debug(`[LLMCoreNode] Event description: ${event.description.substring(0, 100)}...`);
      logger.debug(`[LLMCoreNode] Context changes keys: ${Object.keys(event.contextChanges).join(', ')}`);

      // Apply context changes
      this.applyContextChanges(context, event.contextChanges);

      // Save generated event to request for later use
      req.event = event;

      return next();
    } catch (error) {
      logger.error(`[LLMCoreNode] LLM generation failed:`, error);
      throw new Error(`Failed to generate event: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Generate event using LLM service
   */
  private async generateEvent(
    userInput: string,
    inputType: 'action' | 'question',
    context: Context,
    preLogSummary: { summary: string; recentEvents: string[] } | undefined,
    language: string
  ): Promise<Event> {
    // Validate user input token count
    const estimatedTokens = estimateTokens(userInput, config.llm.model);
    const tokenLimit = config.llm.userInputTokensLimit;

    if (estimatedTokens > tokenLimit) {
      const charLimit = config.userInputLimits[language as 'en' | 'zh']?.chars || config.userInputLimits.en.chars;
      logger.error(`[LLMCoreNode] User input exceeds token limit: ${estimatedTokens} > ${tokenLimit}`);
      throw new Error(
        `User input is too long. Estimated ${estimatedTokens} tokens, limit is ${tokenLimit} tokens (approximately ${charLimit} characters for ${language}). Please shorten your input.`
      );
    }

    logger.debug(`[LLMCoreNode] User input token estimation: ${estimatedTokens} / ${tokenLimit}`);

    // Get prompt template for current language with interpolation
    const i18n = getI18n();
    const eventDescriptionGuidance = config.eventDescriptionGuidance[language as 'en' | 'zh']?.description || config.eventDescriptionGuidance.en.description;
    const basePrompt = i18n.t('prompts:llmCore.system', {
      lng: language,
      eventDescriptionGuidance,
    });

    // Build user-specific prompt instruction
    const userPromptInstruction = this.buildUserPromptInstruction(inputType);
    const fullPrompt = `${basePrompt}\n\n${userPromptInstruction}`;

    // Define output schema for event generation
    const schema = this.buildEventSchema();

    // Convert preLogSummary format
    const preLogSummaryForService = preLogSummary
      ? {
          summary: preLogSummary.summary,
          recentEvents: preLogSummary.recentEvents,
          generatedAt: Date.now(),
        }
      : undefined;

    // Call structured generator
    const response = await generateStructured(
      fullPrompt,
      context.state,
      schema,
      preLogSummaryForService,
      userInput,
      config.llm.model
    );

    // Handle error responses
    if (!response.success) {
      throw new Error(`LLM generation failed: ${response.message} (${response.errorCode})`);
    }

    // Parse result
    if (!response.result) {
      throw new Error('LLM response missing result field');
    }

    const { event_description, context_changes } = response.result;

    if (!event_description) {
      throw new Error('LLM response missing event_description');
    }

    // Convert context_changes to proper format
    const contextChanges: Record<string, ContextField | null> = {};
    if (context_changes && typeof context_changes === 'object') {
      for (const [key, value] of Object.entries(context_changes)) {
        if (value === null) {
          contextChanges[key] = null;
        } else if (typeof value === 'object' && 'value' in value) {
          // Validate required fields
          const field = value as any;
          if (!('type' in field)) {
            throw new Error(`LLM response: field "${key}" missing required property "type"`);
          }
          if (!('name' in field)) {
            throw new Error(`LLM response: field "${key}" missing required property "name"`);
          }
          contextChanges[key] = value as ContextField;
        }
      }
    }

    return {
      description: event_description,
      contextChanges,
    };
  }

  /**
   * Build user-specific prompt instruction based on input type
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
        description: 'Object containing only the context fields that changed. Each field MUST have {value, type, name, description}. Optional: min, max for numeric bounds. Use null to remove a field.',
      },
    };
  }

  /**
   * Apply context changes
   */
  private applyContextChanges(context: Context, changes: Record<string, ContextField | null>): void {
    for (const [key, value] of Object.entries(changes)) {
      if (value === null) {
        // Delete field
        delete context.state[key];
        logger.debug(`[LLMCoreNode] Removed field: ${key}`);
      } else {
        // Update or create field
        context.state[key] = value;
        logger.debug(`[LLMCoreNode] Updated field: ${key} = ${JSON.stringify(value.value)}`);
      }
    }
  }
}
