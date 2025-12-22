import { BaseNode, PluginNodeMetadata } from '../core/pluginNode.ts';
import { Context, Event } from '../types/index.ts';

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
    console.log(`[LLMCoreNode] Generating event for input: ${req.userInput}`);

    // MVP phase: Mock LLM response
    // Phase 2 will implement real LLM calls
    const mockEvent = this.generateMockEvent(req.userInput, context);

    console.log(`[LLMCoreNode] Event generated: ${mockEvent.description}`);

    // Apply context changes
    this.applyContextChanges(context, mockEvent.contextChanges);

    // Save generated event to request for later use
    req.event = mockEvent;

    return next();
  }

  /**
 * Generate mock event (MVP phase)
 */
  private generateMockEvent(input: string, context: Context): Event {
    return {
      description: `You ${input}. The environment responds accordingly.`,
      contextChanges: {},
    };
  }

  /**
 * Apply context changes
 */
  private applyContextChanges(context: Context, changes: Record<string, any>): void {
    for (const [key, value] of Object.entries(changes)) {
      if (value === null) {
        // Delete field
        delete context.state[key];
        console.log(`[LLMCoreNode] Removed field: ${key}`);
      } else {
        // Update or create field
        context.state[key] = value;
        console.log(`[LLMCoreNode] Updated field: ${key}`);
      }
    }
  }
}
