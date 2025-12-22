import { Context } from '../types/index.ts';
import { PluginNode } from './pluginNode.ts';

/**
 * Processing Chain Manager
 * Execute nodes on the chain in order, supporting middleware-style next() calls
 */
export class ProcessingChain {
  private nodes: PluginNode[] = [];

  /**
   * Register a node
   */
  register(node: PluginNode): void {
    this.nodes.push(node);
  }

  /**
   * Execute the processing chain
   */
  async execute(request: unknown, context: Context): Promise<unknown> {
    let currentIndex = 0;

    const next = async (): Promise<unknown> => {
      if (currentIndex >= this.nodes.length) {
        return undefined;
      }

      const node = this.nodes[currentIndex];
      currentIndex++;

      try {
        return await node.process(request, context, next);
      } catch (error) {
        // Unrecoverable error: immediately interrupt the processing chain
        throw error;
      }
    };

    return next();
  }

  /**
   * Get all registered nodes
   */
  getNodes(): PluginNode[] {
    return [...this.nodes];
  }

  /**
   * Clear all nodes
   */
  clear(): void {
    this.nodes = [];
  }
}
