#!/bin/bash
# Render startup script
export PORT=${PORT:-10000}
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
