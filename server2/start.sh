#!/bin/bash
echo "Starting Kafka Consumer in the background..."
python consumer.py &

echo "Starting FastAPI server in the foreground..."
uvicorn main:app --host 0.0.0.0 --port 8000