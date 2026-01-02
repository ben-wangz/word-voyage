import { BaseNode, PluginNodeMetadata } from '../core/pluginNode.ts';
import { Context } from '../types/index.ts';

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
      const req = request as any;
      const t = req.t;
      const errorMessage = t
        ? t('common:errors.contextLimitExceeded', `Context field limit exceeded: {{current}} > {{max}}. Please remove some fields using mechanism questioning.`, {
            current: fieldCount,
            max: MAX_CONTEXT_FIELDS,
          })
        : `Context field limit exceeded: ${fieldCount} > ${MAX_CONTEXT_FIELDS}. Please remove some fields using mechanism questioning.`;
      throw new Error(errorMessage);
    }

    // Log current state for debugging
    console.log(`[StateManagementNode] Context state keys:`, Object.keys(context.state));

    return next();
  }
}
