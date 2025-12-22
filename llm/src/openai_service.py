# OpenAI LLM Service - FastAPI HTTP Server
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn

from .config import (
    SERVICE_HOST, SERVICE_PORT, OPENAI_MODEL, CONTEXT_MAX_FIELDS, LOG_LEVEL
)
from .models import StructuredGenerationRequest, StructuredGenerationResponse
from .validator import validate_schema, generate_fix_suggestion

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="OpenAI LLM Service", version="1.0.0")


@app.post("/generate_structured", response_model=StructuredGenerationResponse)
async def generate_structured_data(request: StructuredGenerationRequest):
    """Generate structured data using OpenAI API"""
    try:
        logger.info(f"Processing structured generation request")

        # Validate context length
        if len(request.context) > CONTEXT_MAX_FIELDS:
            error_msg = f"Context exceeds maximum allowed fields: {len(request.context)} > {CONTEXT_MAX_FIELDS}"
            logger.error(error_msg)
            return StructuredGenerationResponse(
                success=False,
                message=error_msg,
                error_code="CONTEXT_TOO_LARGE",
                fix_suggestion=f"Reduce context fields to {CONTEXT_MAX_FIELDS} or less"
            )

        from .openai_client import generate_structured

        try:
            result = generate_structured(
                prompt=request.prompt,
                context=request.context,
                schema=request.schema,
                pre_log_summary=request.pre_log_summary,
                user_input=request.user_input,
                model=request.model,
                stream=request.stream
            )

            # Validate result against schema
            validation_errors = validate_schema(result, request.schema)

            if validation_errors:
                logger.warning(f"Schema validation failed: {validation_errors}")
                return StructuredGenerationResponse(
                    success=False,
                    message="Generated data does not match required schema",
                    error_code="SCHEMA_VALIDATION_FAILED",
                    validation_errors=validation_errors,
                    fix_suggestion=generate_fix_suggestion(validation_errors)
                )

            logger.info("Structured generation completed successfully")
            return StructuredGenerationResponse(
                success=True,
                message="Generation completed",
                result=result
            )

        except ValueError as e:
            logger.error(f"JSON parsing failed: {e}")
            return StructuredGenerationResponse(
                success=False,
                message="Failed to parse LLM response as valid JSON",
                error_code="INVALID_JSON",
                fix_suggestion="LLM should respond with valid JSON only, no markdown or extra text"
            )
        except Exception as e:
            logger.exception(f"OpenAI API call failed: {e}")
            return StructuredGenerationResponse(
                success=False,
                message="LLM API call failed",
                error_code="API_ERROR",
                fix_suggestion="Please check API configuration and retry"
            )

    except Exception as e:
        logger.exception(f"Unexpected error in structured generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_structured_stream")
async def generate_structured_data_stream(request: StructuredGenerationRequest):
    """Generate structured data using OpenAI API with streaming"""
    try:
        if not request.stream:
            raise HTTPException(status_code=400, detail="This endpoint requires stream=true")

        # Validate context length
        if len(request.context) > CONTEXT_MAX_FIELDS:
            error_msg = f"Context exceeds maximum allowed fields: {len(request.context)} > {CONTEXT_MAX_FIELDS}"
            logger.error(error_msg)
            return StructuredGenerationResponse(
                success=False,
                message=error_msg,
                error_code="CONTEXT_TOO_LARGE",
                fix_suggestion=f"Reduce context fields to {CONTEXT_MAX_FIELDS} or less"
            )

        from .openai_client import generate_structured

        def stream_response():
            try:
                response_stream = generate_structured(
                    prompt=request.prompt,
                    context=request.context,
                    schema=request.schema,
                    pre_log_summary=request.pre_log_summary,
                    user_input=request.user_input,
                    model=request.model,
                    stream=True
                )

                for chunk in response_stream:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if delta and hasattr(delta, 'content') and delta.content:
                            yield f"data: {delta.content}\n\n"

            except Exception as e:
                logger.exception(f"Streaming failed: {e}")
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

        return StreamingResponse(
            stream_response(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in streaming generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model": OPENAI_MODEL,
        "service": "openai-llm",
        "context_max_fields": CONTEXT_MAX_FIELDS
    }


def main():
    uvicorn.run(app, host=SERVICE_HOST, port=SERVICE_PORT)


if __name__ == "__main__":
    main()