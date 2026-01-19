import { ContextField, PreLogSummary } from '../../types/index.ts';

/**
 * Build user prompt with dynamic game state and user input
 */
export function buildUserPrompt(
  context: { [key: string]: ContextField },
  preLogSummary?: PreLogSummary,
  userInput?: string
): string {
  let userPrompt = '';

  // Add context
  if (context && Object.keys(context).length > 0) {
    userPrompt += 'Current game state:\n';
    for (const [fieldName, fieldValue] of Object.entries(context)) {
      const value = fieldValue.value ?? '';
      const description = fieldValue.description ?? '';
      userPrompt += `- ${fieldName}: ${value} (${description})\n`;
    }
    userPrompt += '\n';
  }

  // Add pre-log summary if provided
  if (preLogSummary) {
    userPrompt += `Recent events summary: ${preLogSummary.summary}\n`;
    if (preLogSummary.recentEvents && preLogSummary.recentEvents.length > 0) {
      userPrompt += 'Recent events:\n';
      for (const event of preLogSummary.recentEvents) {
        userPrompt += `- ${event}\n`;
      }
    }
    userPrompt += '\n';
  }

  // Add user input if provided
  if (userInput) {
    userPrompt += `User action: ${userInput}\n\n`;
  }

  return userPrompt;
}
