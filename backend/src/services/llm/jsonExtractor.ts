import { logger } from '../../utils/logger.ts';

/**
 * Extract JSON from mixed content (thoughts + JSON)
 */
export function extractJsonFromText(text: string): string {
  text = text.trim();

  // Method 1: Find JSON code blocks
  if (text.includes('```json')) {
    const start = text.indexOf('```json') + 7;
    const end = text.indexOf('```', start);
    if (end !== -1) {
      return text.substring(start, end).trim();
    }
  } else if (text.includes('```')) {
    const start = text.indexOf('```') + 3;
    const end = text.indexOf('```', start);
    if (end !== -1) {
      return text.substring(start, end).trim();
    }
  }

  // Method 2: Find JSON object boundaries
  let jsonStart = -1;
  let braceCount = 0;
  let inString = false;
  let escapeNext = false;

  for (let i = 0; i < text.length; i++) {
    const char = text[i];

    if (escapeNext) {
      escapeNext = false;
      continue;
    }

    if (char === '\\') {
      escapeNext = true;
      continue;
    }

    if (char === '"' && !escapeNext) {
      inString = !inString;
      continue;
    }

    if (!inString) {
      if (char === '{') {
        if (jsonStart === -1) {
          jsonStart = i;
        }
        braceCount++;
      } else if (char === '}') {
        if (jsonStart !== -1) {
          braceCount--;
          if (braceCount === 0) {
            return text.substring(jsonStart, i + 1);
          }
        }
      }
    }
  }

  // Method 3: Try to find simple JSON patterns
  const lines = text.split('\n');
  const jsonLines: string[] = [];
  let inJson = false;

  for (const line of lines) {
    const trimmedLine = line.trim();
    if (trimmedLine.startsWith('{')) {
      inJson = true;
      jsonLines.push(line);
    } else if (inJson) {
      jsonLines.push(line);
      if (trimmedLine.endsWith('}')) {
        break;
      }
    }
  }

  if (jsonLines.length > 0) {
    const potentialJson = jsonLines.join('\n');
    try {
      JSON.parse(potentialJson);
      return potentialJson;
    } catch {
      // Continue to method 4
    }
  }

  // Method 4: Try the whole text as last resort
  return text;
}

/**
 * Clean JSON string by removing/escaping control characters
 */
export function cleanJsonString(jsonStr: string): string {
  // Remove control characters except \n, \r, \t
  // Control chars are 0x00-0x1F except tab(0x09), newline(0x0A), carriage return(0x0D)
  const cleaned = jsonStr.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, '');
  return cleaned;
}

/**
 * Extract and parse JSON from LLM response
 */
export function extractAndParseJson(content: string, reasoningContent?: string): any {
  try {
    // Strategy 1: Try to extract from content first (most reliable)
    let jsonContent = extractJsonFromText(content);
    logger.debug(`[JsonExtractor] Extracted JSON from content: ${jsonContent.substring(0, 200)}...`);

    // Validate it's actually JSON-like (starts with { or [)
    const jsonContentStripped = jsonContent.trim();
    if (!jsonContentStripped.startsWith('{') && !jsonContentStripped.startsWith('[')) {
      logger.warn('[JsonExtractor] Extracted content doesn\'t look like JSON, trying with reasoning...');
      // Strategy 2: If content extraction failed, try full text including reasoning
      if (reasoningContent) {
        const fullText = `${reasoningContent}\n\n${content}`;
        jsonContent = extractJsonFromText(fullText);
        logger.debug(`[JsonExtractor] Extracted JSON from full text: ${jsonContent.substring(0, 200)}...`);
      }
    }

    // Clean control characters
    const jsonContentCleaned = cleanJsonString(jsonContent);
    if (jsonContent !== jsonContentCleaned) {
      logger.warn('[JsonExtractor] Control characters found and removed from JSON');
      logger.debug(`[JsonExtractor] Cleaned JSON content: ${jsonContentCleaned.substring(0, 200)}...`);
    }

    const result = JSON.parse(jsonContentCleaned);
    logger.debug(`[JsonExtractor] Parsed result: ${JSON.stringify(result)}`);
    return result;
  } catch (error) {
    logger.error(`[JsonExtractor] Failed to parse JSON response: ${error}`);
    logger.error(`[JsonExtractor] Full content: ${content.substring(0, 500)}...`);
    if (reasoningContent) {
      logger.error(`[JsonExtractor] Reasoning content: ${reasoningContent.substring(0, 500)}`);
    }
    throw new Error(`Invalid JSON response: ${error}`);
  }
}
