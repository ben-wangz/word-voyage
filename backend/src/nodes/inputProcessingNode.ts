import { BaseNode, PluginNodeMetadata } from '../core/pluginNode.ts';
import { Context } from '../types/index.ts';

/**
 * Input Processing Node
 * Classify user input (action/thought vs mechanism questioning)
 */
export class InputProcessingNode extends BaseNode {
  metadata: PluginNodeMetadata = {
    id: 'input-processing-node',
    name: 'InputProcessingNode',
    version: '1.0.0',
  };

  async process(request: unknown, context: Context, next: () => Promise<unknown>): Promise<unknown> {
    const req = request as { input: string };
    console.log(`[InputProcessingNode] Processing input: ${req.input}`);

    // MVP phase: simple heuristic rules
    const inputType = this.classifyInput(req.input);

    // Add input info to context (session-level, not persisted)
    (request as any).inputType = inputType;
    (request as any).userInput = req.input;

    console.log(`[InputProcessingNode] Input type: ${inputType}`);

    return next();
  }

  /**
 * Simple input classification logic
 */
  private classifyInput(input: string): 'action' | 'question' {
    // MVP phase: simple rules
    // If contains keywords like "I think", "should", "rules", consider it mechanism questioning
    // Otherwise consider it action/thought
    const questionKeywords = ['I think', 'should', 'rules', 'mechanism', 'change'];
    const isQuestion = questionKeywords.some((keyword) => input.includes(keyword));

    return isQuestion ? 'question' : 'action';
  }
}
