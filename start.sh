#!/bin/bash

# Start the backend (using the exact command that works locally)
echo "Starting backend..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8080 > backend.log 2>&1 &

# Wait for the backend to be ready
echo "Waiting for backend to start..."
until curl -s http://localhost:8080 > /dev/null; do
  echo "Backend not ready yet, waiting..."
  sleep 2
done

# Start the frontend
echo "Backend is up! Starting frontend..."
streamlit run frontend.py --server.port 7860 --server.address 0.0.0.0