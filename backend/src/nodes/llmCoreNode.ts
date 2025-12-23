import { BaseNode, PluginNodeMetadata } from '../core/pluginNode.ts';
import { Context, Event, ContextField } from '../types/index.ts';
import { llmClient } from '../services/llmClient.ts';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

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

  private basePrompt: string;

  constructor() {
    super();
    this.basePrompt = this.loadPromptTemplate();
  }

  async process(request: unknown, context: Context, next: () => Promise<unknown>): Promise<unknown> {
    const req = request as any;
    console.log(`[LLMCoreNode] Generating event for input: ${req.userInput}`);

    try {
      const event = await this.generateEvent(
        req.userInput,
        req.inputType,
        context,
        req.preLogSummary
      );

      console.log(`[LLMCoreNode] Event generated: ${event.description}`);

      // Apply context changes
      this.applyContextChanges(context, event.contextChanges);

      // Save generated event to request for later use
      req.event = event;

      return next();
    } catch (error) {
      console.error(`[LLMCoreNode] LLM generation failed:`, error);
      throw new Error(`Failed to generate event: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Load prompt template from file
   */
  private loadPromptTemplate(): string {
    try {
      const promptPath = join(import.meta.dir, '../prompts/llmCore.txt');
      return readFileSync(promptPath, 'utf-8');
    } catch (error) {
      console.error('[LLMCoreNode] Failed to load prompt template:', error);
      throw new Error('Failed to load prompt template');
    }
  }

  /**
   * Generate event using LLM service
   */
  private async generateEvent(
    userInput: string,
    inputType: 'action' | 'question',
    context: Context,
    preLogSummary?: { summary: string; recentEvents: string[] }
  ): Promise<Event> {
    // Convert preLogSummary to snake_case for LLM service
    const preLogSummaryForService = preLogSummary
      ? {
          summary: preLogSummary.summary,
          recent_events: preLogSummary.recentEvents,
        }
      : undefined;

    // Build LLM request
    const llmRequest = llmClient.buildRequest(
      this.basePrompt,
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
        console.log(`[LLMCoreNode] Removed field: ${key}`);
      } else {
        // Update or create field
        context.state[key] = value;
        console.log(`[LLMCoreNode] Updated field: ${key} = ${value.value}`);
      }
    }
  }
}
