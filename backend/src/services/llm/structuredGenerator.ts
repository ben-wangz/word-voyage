import { SchemaField, ContextField, PreLogSummary } from '../../types/index.ts';
import { llmClient } from './llmClient.ts';
import { buildUserPrompt } from './promptBuilder.ts';
import { extractAndParseJson } from './jsonExtractor.ts';
import { validateSchema, generateFixSuggestion } from '../validation/index.ts';
import type { ValidationError } from '../validation/index.ts';
import { estimateTokens } from './tokenEstimator.ts';
import { logger } from '../../utils/logger.ts';
import { config } from '../../config.ts';

/**
 * Structured generation result
 */
export type StructuredGenerationResult = {
  success: boolean;
  message: string;
  result?: Record<string, any>;
  errorCode?: string;
  validationErrors?: ValidationError[];
  fixSuggestion?: string;
};

/**
 * Generate structured data using LLM
 */
export async function generateStructured(
  systemPrompt: string,
  context: { [key: string]: ContextField },
  schema: { [key: string]: SchemaField },
  preLogSummary?: PreLogSummary,
  userInput?: string,
  model?: string
): Promise<StructuredGenerationResult> {
  try {
    logger.info('[StructuredGenerator] Processing structured generation request');

    // Validate context length
    const contextFieldCount = Object.keys(context).length;
    if (contextFieldCount > config.llm.contextMaxFields) {
      const errorMsg = `Context exceeds maximum allowed fields: ${contextFieldCount} > ${config.llm.contextMaxFields}`;
      logger.error(`[StructuredGenerator] ${errorMsg}`);
      return {
        success: false,
        message: errorMsg,
        errorCode: 'CONTEXT_TOO_LARGE',
        fixSuggestion: `Reduce context fields to ${config.llm.contextMaxFields} or less`,
      };
    }

    // Build user prompt with dynamic content only
    const userPrompt = buildUserPrompt(context, preLogSummary, userInput);

    // Estimate token counts
    const modelName = model || config.openai.model;
    const systemTokens = estimateTokens(systemPrompt, modelName);
    const userTokens = estimateTokens(userPrompt, modelName);
    const totalInputTokens = systemTokens + userTokens;

    logger.debug(`[StructuredGenerator] System prompt: ${systemPrompt}`);
    logger.debug(`[StructuredGenerator] User prompt: ${userPrompt}`);
    logger.debug(
      `[StructuredGenerator] Token estimation - System: ${systemTokens}, User: ${userTokens}, Total input: ${totalInputTokens}, Max output: ${config.llm.maxTokens}`
    );
    logger.info(`[StructuredGenerator] Calling LLM with model=${modelName}, max_tokens=${config.llm.maxTokens}`);

    // Call LLM service
    try {
      const llmResponse = await llmClient.complete({
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt },
        ],
        model: modelName,
        max_tokens: config.llm.maxTokens,
        base_url: config.openai.baseUrl,
        api_key: config.openai.apiKey,
        response_format: { type: 'json_object' },
      });

      // Extract and parse JSON
      const result = extractAndParseJson(llmResponse.content, llmResponse.reasoning_content);

      // Validate result against schema
      const validationErrors = validateSchema(result, schema);

      if (validationErrors.length > 0) {
        logger.warn(`[StructuredGenerator] Schema validation failed: ${JSON.stringify(validationErrors)}`);
        return {
          success: false,
          message: 'Generated data does not match required schema',
          errorCode: 'SCHEMA_VALIDATION_FAILED',
          validationErrors,
          fixSuggestion: generateFixSuggestion(validationErrors),
        };
      }

      logger.info('[StructuredGenerator] Structured generation completed successfully');
      return {
        success: true,
        message: 'Generation completed',
        result,
      };
    } catch (error) {
      if (error instanceof Error && error.message.includes('Invalid JSON')) {
        logger.error(`[StructuredGenerator] JSON parsing failed: ${error.message}`);
        return {
          success: false,
          message: 'Failed to parse LLM response as valid JSON',
          errorCode: 'INVALID_JSON',
          fixSuggestion: 'LLM should respond with valid JSON only, no markdown or extra text',
        };
      }
      throw error;
    }
  } catch (error) {
    logger.error(`[StructuredGenerator] LLM API call failed: ${error}`);
    return {
      success: false,
      message: 'LLM API call failed',
      errorCode: 'API_ERROR',
      fixSuggestion: 'Please check API configuration and retry',
    };
  }
}
