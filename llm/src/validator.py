import logging
from typing import Dict, Any, List
from .models import ValidationResult, SchemaField

logger = logging.getLogger(__name__)


def validate_schema(
    result: Dict[str, Any],
    schema: Dict[str, SchemaField]
) -> List[ValidationResult]:
    """
    Validate generated result against schema

    Args:
        result: Generated data to validate
        schema: Expected schema definition

    Returns:
        List of validation errors
    """
    errors = []

    for field_name, field_def in schema.items():
        if field_name not in result:
            errors.append(ValidationResult(
                field=field_name,
                expected=f"{field_def.type} (required)",
                received="missing"
            ))
            continue

        value = result[field_name]

        # Check type compatibility
        expected_type = field_def.type
        actual_type = type(value).__name__

        if not _is_type_compatible(value, expected_type):
            errors.append(ValidationResult(
                field=field_name,
                expected=expected_type,
                received=actual_type
            ))

    return errors


def _is_type_compatible(value: Any, expected_type: str) -> bool:
    """Check if value matches expected type"""
    type_mapping = {
        'string': str,
        'number': (int, float),
        'object': dict,
        'array': list,
        'boolean': bool
    }

    expected_python_type = type_mapping.get(expected_type)
    if not expected_python_type:
        logger.warning(f"Unknown type: {expected_type}")
        return True  # Allow unknown types

    return isinstance(value, expected_python_type)


def generate_fix_suggestion(errors: List[ValidationResult]) -> str:
    """Generate fix suggestion based on validation errors"""
    if not errors:
        return ""

    suggestions = []
    for error in errors:
        if error.received == "missing":
            suggestions.append(f"Add required field '{error.field}' with type '{error.expected}'")
        else:
            suggestions.append(f"Change field '{error.field}' from {error.received} to {error.expected}")

    return "Please fix the following issues: " + "; ".join(suggestions)