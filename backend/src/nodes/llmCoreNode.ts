import { BaseNode, PluginNodeMetadata } from '../core/pluginNode.ts';
import { Context, Event, ContextField } from '../types/index.ts';
import { llmClient } from '../services/llmClient.ts';
import { getI18n } from '../i18n/index.ts';
import { logger } from '../utils/logger.ts';

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
    // Get prompt template for current language
    const i18n = getI18n();
    const basePrompt = i18n.t('prompts:llmCore.system', { lng: language });

    // Convert preLogSummary to snake_case for LLM service
    const preLogSummaryForService = preLogSummary
      ? {
          summary: preLogSummary.summary,
          recent_events: preLogSummary.recentEvents,
        }
      : undefined;

    // Build LLM request
    const llmRequest = llmClient.buildRequest(
      basePrompt,
      context,
      userInput,
      inputType,
      preLogSummaryForService
    );

    // Call LLM service
    const response = await llmClient.generateStructured(llmRequest);

    // Handle error responses
    if (!response.success) {
      throw new Error(`LLM generation failed: ${response.message} (${response.error_code})`);
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
