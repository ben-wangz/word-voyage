import { Tiktoken, encodingForModel } from 'js-tiktoken';
import { logger } from '../../utils/logger.ts';

/**
 * Estimate token count for given text
 */
export function estimateTokens(text: string, model: string = 'gpt-4'): number {
  try {
    // Map common model names to tiktoken encodings
    // Qwen models typically use cl100k_base encoding (same as GPT-4)
    const encodingMap: Record<string, string> = {
      'gpt-4': 'cl100k_base',
      'gpt-4o': 'o200k_base',
      'gpt-3.5-turbo': 'cl100k_base',
      'qwen': 'cl100k_base', // Qwen uses similar tokenization
    };

    // Determine encoding based on model name
    let encodingName = 'cl100k_base'; // default
    for (const [modelPrefix, enc] of Object.entries(encodingMap)) {
      if (model.toLowerCase().includes(modelPrefix)) {
        encodingName = enc;
        break;
      }
    }

    // Get encoding and count tokens
    let encoding: Tiktoken;
    try {
      encoding = encodingForModel(model as any);
    } catch {
      // Fallback to encoding name if model not recognized
      encoding = encodingForModel(encodingName as any);
    }

    const tokens = encoding.encode(text);
    encoding.free();
    return tokens.length;
  } catch (error) {
    logger.warn(`[TokenEstimator] Failed to estimate tokens with tiktoken: ${error}, using fallback`);
    // Fallback: rough estimation
    // Chinese: ~1.5 chars/token, English: ~4 chars/token
    // Use conservative estimate of 2 chars/token for mixed content
    return Math.ceil(text.length / 2);
  }
}
