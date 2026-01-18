import { SchemaField } from '../../types/index.ts';
import type { ValidationError } from './validationError.ts';
import { logger } from '../../utils/logger.ts';

/**
 * Check if value matches expected type
 */
function isTypeCompatible(value: any, expectedType: string): boolean {
  const typeMapping: Record<string, string> = {
    'string': 'string',
    'number': 'number',
    'object': 'object',
    'array': 'array',
    'boolean': 'boolean',
  };

  const expectedJsType = typeMapping[expectedType];
  if (!expectedJsType) {
    logger.warn(`[SchemaValidator] Unknown type: ${expectedType}`);
    return true; // Allow unknown types
  }

  if (expectedJsType === 'array') {
    return Array.isArray(value);
  }

  if (expectedJsType === 'number') {
    return typeof value === 'number' || typeof value === 'bigint';
  }

  return typeof value === expectedJsType;
}

/**
 * Validate generated result against schema
 */
export function validateSchema(
  result: Record<string, any>,
  schema: Record<string, SchemaField>
): ValidationError[] {
  const errors: ValidationError[] = [];

  for (const [fieldName, fieldDef] of Object.entries(schema)) {
    if (!(fieldName in result)) {
      errors.push({
        field: fieldName,
        expected: `${fieldDef.type} (required)`,
        received: 'missing',
      });
      continue;
    }

    const value = result[fieldName];

    // Check type compatibility
    const expectedType = fieldDef.type;
    const actualType = Array.isArray(value) ? 'array' : typeof value;

    if (!isTypeCompatible(value, expectedType)) {
      errors.push({
        field: fieldName,
        expected: expectedType,
        received: actualType,
      });
    }
  }

  return errors;
}

/**
 * Generate fix suggestion based on validation errors
 */
export function generateFixSuggestion(errors: ValidationError[]): string {
  if (errors.length === 0) {
    return '';
  }

  const suggestions: string[] = [];
  for (const error of errors) {
    if (error.received === 'missing') {
      suggestions.push(`Add required field '${error.field}' with type '${error.expected}'`);
    } else {
      suggestions.push(`Change field '${error.field}' from ${error.received} to ${error.expected}`);
    }
  }

  return 'Please fix the following issues: ' + suggestions.join('; ');
}
