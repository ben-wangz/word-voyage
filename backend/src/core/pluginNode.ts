import { Context } from '../types/index.ts';

/**
 * Base interface for plugin nodes
 */
export interface PluginNodeMetadata {
  id: string;
  name: string;
  version: string;
}

/**
 * Plugin node interface
 */
export interface PluginNode {
  metadata: PluginNodeMetadata;
  process(request: unknown, context: Context, next: () => Promise<unknown>): Promise<unknown>;
}

/**
 * Abstract base class for convenient extension
 */
export abstract class BaseNode implements PluginNode {
  abstract metadata: PluginNodeMetadata;

  abstract process(request: unknown, context: Context, next: () => Promise<unknown>): Promise<unknown>;
}
