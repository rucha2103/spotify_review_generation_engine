#!/bin/bash

# Remove the '> backend.log 2>&1' part so it prints directly to the console
echo "Starting backend..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8080 &

# Wait for backend to start
echo "Waiting for backend..."
until curl -s http://localhost:8080/health > /dev/null; do
  sleep 2
done

echo "Backend is up! Starting frontend..."
streamlit run frontend.py --server.port 7860 --server.address 0.0.0.0