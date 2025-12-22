#!/bin/bash

set -e

echo "OpenAI LLM Service - Starting..."
echo "Checking Python installation..."

if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found"
    exit 1
fi

python3 --version

echo "Starting OpenAI LLM service..."
exec python3 -m src.main