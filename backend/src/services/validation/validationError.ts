/**
 * Validation error result
 */
export type ValidationError = {
  field: string;
  expected: string;
  received: string;
};
