#!/bin/bash

# 1. Start the backend in the background
echo "Starting backend..."
uvicorn backend:app --host 0.0.0.0 --port 8080 > backend.log 2>&1 &

# 2. Wait for the backend to be ready
echo "Waiting for backend to start..."
# This loop checks if port 8080 is accepting connections
until curl -s http://localhost:8080 > /dev/null; do
  echo "Backend not ready yet, waiting..."
  sleep 2
done

# 3. Now start the frontend
echo "Backend is up! Starting frontend..."
streamlit run frontend.py --server.port 7860 --server.address 0.0.0.0