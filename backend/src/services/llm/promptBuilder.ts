import { SchemaField, ContextField, PreLogSummary } from '../../types/index.ts';

/**
 * Build system prompt with schema requirements
 */
export function buildSystemPrompt(schema: { [key: string]: SchemaField }): string {
  let schemaDescription = 'You must respond with ONLY valid JSON that follows this exact schema:\n';

  for (const [fieldName, fieldDef] of Object.entries(schema)) {
    schemaDescription += `- ${fieldName}: ${fieldDef.description} (type: ${fieldDef.type})\n`;
  }

  schemaDescription += `
CRITICAL RULES:
1. Return ONLY the JSON object, nothing else
2. NO thinking process, NO explanations, NO markdown
3. Ensure all JSON strings are properly closed with quotes
4. Do NOT use control characters or special symbols in strings
5. Your entire response must be valid JSON starting with opening brace and ending with closing brace
`;

  return schemaDescription;
}

/**
 * Build user prompt with all context information
 */
export function buildUserPrompt(
  prompt: string,
  context: { [key: string]: ContextField },
  preLogSummary?: PreLogSummary,
  userInput?: string
): string {
  let userPrompt = `${prompt}\n\n`;

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
