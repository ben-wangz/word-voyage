// ==========================================
// Data Model Types
// ==========================================

/**
 * Individual context field
 */
export interface ContextField {
  value: any;
  type: 'int' | 'double' | 'string' | 'boolean' | 'object' | 'array';
  name: string;
  description?: string;
  min?: number;
  max?: number;
}

/**
 * Game context (state)
 */
export interface Context {
  state: {
    [key: string]: ContextField;
  };
}

/**
 * Pre-log summary
 */
export interface PreLogSummary {
  summary: string;
  recentEvents: string[];
  generatedAt: number;
}

/**
 * LLM-generated event
 */
export interface Event {
  description: string;
  contextChanges: {
    [key: string]: ContextField | null;
  };
}

/**
 * Complete game step (atomic unit)
 */
export interface Step {
  id: string;
  timestamp: number;
  userInput: string;
  inputType: 'action' | 'question';

  // Complete triplet
  context: Context;
  event: Event;
  preLogSummary: PreLogSummary;
}

/**
 * API request body: process user input
 */
export interface ProcessStepRequest {
  input: string;
  sessionId?: string;
}

/**
 * API response body: return new Step
 */
export interface ProcessStepResponse {
  step: Step;
  sessionId: string;
}

/**
 * API request body: start new game
 */
export interface StartGameRequest {
  sessionId?: string;
}

/**
 * API response body: game started
 */
export interface StartGameResponse {
  step: Step;
  sessionId: string;
}

/**
 * Error response
 */
export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}

// ==========================================
// LLM Service Types
// ==========================================

/**
 * Schema field definition for LLM structured output
 */
export interface SchemaField {
  type: string;
  description: string;
}

/**
 * Validation error from LLM service
 */
export interface ValidationResult {
  field: string;
  expected: string;
  received: string;
}

/**
 * LLM service request body
 */
export interface LLMGenerationRequest {
  prompt: string;
  context: {
    [key: string]: ContextField;
  };
  pre_log_summary?: {
    summary: string;
    recent_events: string[];
  };
  user_input?: string;
  schema: {
    [key: string]: SchemaField;
  };
  stream?: boolean;
  model?: string;
}

/**
 * LLM service response body
 */
export interface LLMGenerationResponse {
  success: boolean;
  message: string;
  result?: {
    [key: string]: any;
  };
  error_code?: string;
  validation_errors?: ValidationResult[];
  fix_suggestion?: string;
}

// ==========================================
// i18n Types
// ==========================================

/**
 * i18n context variables for Hono
 */
export interface I18nContext {
  language: string;
  t: (key: string, defaultValue?: string, options?: Record<string, any>) => string;
}
