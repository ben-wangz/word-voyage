import { BaseNode, PluginNodeMetadata } from '../core/pluginNode.ts';
import { Context, ContextField } from '../types/index.ts';

const MAX_CONTEXT_FIELDS = 16;

/**
 * State Management Node
 * Load/save context, validate field count
 */
export class StateManagementNode extends BaseNode {
  metadata: PluginNodeMetadata = {
    id: 'state-management-node',
    name: 'StateManagementNode',
    version: '1.0.0',
  };

  async process(request: unknown, context: Context, next: () => Promise<unknown>): Promise<unknown> {
    console.log(`[StateManagementNode] Current context fields: ${Object.keys(context.state).length}`);

    // Validate field count
    const fieldCount = Object.keys(context.state).length;
    if (fieldCount > MAX_CONTEXT_FIELDS) {
      throw new Error(
        `Context field limit exceeded: ${fieldCount} > ${MAX_CONTEXT_FIELDS}. Please remove some fields using mechanism questioning.`,
      );
    }

    // Log current state for debugging
    console.log(`[StateManagementNode] Context state keys:`, Object.keys(context.state));

    return next();
  }
}
