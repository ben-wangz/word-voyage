from typing import List, Optional, Any, Dict
from pydantic import BaseModel


class ContextField(BaseModel):
    value: Any
    type: str  # 'int' | 'double' | 'string' | 'boolean' | 'object' | 'array'
    name: str
    description: Optional[str] = None
    min: Optional[float] = None
    max: Optional[float] = None


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
    name: str
    description: Optional[str] = None
    min: Optional[float] = None
    max: Optional[float] = None


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