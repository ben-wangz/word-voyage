# LLM Proxy Service - FastAPI HTTP Server
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

from .config import SERVICE_HOST, SERVICE_PORT, LOG_LEVEL
from . import proxy

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Proxy Service", version="1.0.0")


class Message(BaseModel):
    role: str
    content: str


class CompletionRequest(BaseModel):
    messages: List[Message]
    model: str
    max_tokens: int
    response_format: Optional[Dict[str, str]] = None


class CompletionResponse(BaseModel):
    content: str
    reasoning_content: Optional[str] = None


@app.post("/complete", response_model=CompletionResponse)
async def complete_endpoint(request: CompletionRequest):
    """Complete using OpenAI API (non-streaming)"""
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        result = proxy.complete(
            messages=messages,
            model=request.model,
            max_tokens=request.max_tokens,
            response_format=request.response_format
        )

        return CompletionResponse(
            content=result['content'],
            reasoning_content=result.get('reasoning_content')
        )
    except Exception as e:
        logger.exception(f"Completion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/complete_stream")
async def complete_stream_endpoint(request: CompletionRequest):
    """Complete using OpenAI API (streaming)"""
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        def stream_response():
            try:
                response_stream = proxy.complete_stream(
                    messages=messages,
                    model=request.model,
                    max_tokens=request.max_tokens,
                    response_format=request.response_format
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
        logger.exception(f"Streaming setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "llm-proxy"
    }


def main():
    uvicorn.run(app, host=SERVICE_HOST, port=SERVICE_PORT)


if __name__ == "__main__":
    main()
