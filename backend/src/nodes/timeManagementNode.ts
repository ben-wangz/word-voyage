import { BaseNode, PluginNodeMetadata } from '../core/pluginNode.ts';
import { Context } from '../types/index.ts';

/**
 * Time Management Node
 * Calculate current game time and update to context
 */
export class TimeManagementNode extends BaseNode {
  metadata: PluginNodeMetadata = {
    id: 'time-management-node',
    name: 'TimeManagementNode',
    version: '1.0.0',
  };

  async process(request: unknown, context: Context, next: () => Promise<unknown>): Promise<unknown> {
    console.log(`[TimeManagementNode] Current game time: ${context.gameTime}`);

    // MVP phase: simple time increment
    // Increment game time by 1 hour per step (3600 seconds)
    const timeIncrement = 3600;
    context.gameTime += timeIncrement;

    console.log(`[TimeManagementNode] Updated game time: ${context.gameTime}`);

    return next();
  }
}
