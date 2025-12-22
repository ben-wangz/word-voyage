import { BaseNode, PluginNodeMetadata } from '../core/pluginNode.ts';
import { Context } from '../types/index.ts';

/**
 * Pre-log Summary Node
 * Generate PreLogSummary from historical Steps
 */
export class PreLogSummaryNode extends BaseNode {
  metadata: PluginNodeMetadata = {
    id: 'pre-log-summary-node',
    name: 'PreLogSummaryNode',
    version: '1.0.0',
  };

  async process(request: unknown, context: Context, next: () => Promise<unknown>): Promise<unknown> {
    console.log(`[PreLogSummaryNode] Generating pre-log summary...`);

    // MVP phase: Mock implementation
    // Phase 2 will load history from StepStorage and call LLM to generate summary
    const mockPreLogSummary = {
      summary: 'Game just started. Player is exploring the crashed spaceship.',
      recentEvents: [],
      generatedAt: Date.now(),
    };

    (request as any).preLogSummary = mockPreLogSummary;

    console.log(`[PreLogSummaryNode] Summary generated`);

    return next();
  }
}
