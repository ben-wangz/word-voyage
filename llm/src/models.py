from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class ContextField(BaseModel):
    value: Any
    type: str  # 'number' | 'string' | 'object' | 'array'
    description: Optional[str] = None


class PreLogSummary(BaseModel):
    summary: str
    recent_events: List[str]


class SchemaField(BaseModel):
    type: str
    description: str


class StructuredGenerationRequest(BaseModel):
    prompt: str
    context: Dict[str, ContextField]
    pre_log_summary: Optional[PreLogSummary] = None
    user_input: Optional[str] = None
    schema: Dict[str, SchemaField]
    stream: Optional[bool] = False
    model: Optional[str] = None


class ContextChange(BaseModel):
    value: Any
    type: str
    description: Optional[str] = None


class ValidationResult(BaseModel):
    field: str
    expected: str
    received: str


class StructuredGenerationResponse(BaseModel):
    success: bool
    message: str
    result: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    validation_errors: Optional[List[ValidationResult]] = None
    fix_suggestion: Optional[str] = None