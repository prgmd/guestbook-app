#!/bin/bash

# outbox_poller.py를 백그라운드에서 실행 (&)
echo "Starting Outbox Poller in the background..."
python outbox_poller.py &

# FastAPI 서버를 포그라운드에서 실행 (컨테이너가 종료되지 않도록)
echo "Starting FastAPI server in the foreground..."
uvicorn main:app --host 0.0.0.0 --port 8000