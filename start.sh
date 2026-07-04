#!/bin/bash

# Start the backend in the background
# Replace 'main:app' with your actual backend file and app instance
uvicorn backend:app --host 0.0.0.0 --port 8080 &

# Start the Streamlit frontend
streamlit run frontend.py --server.port 7860 --server.address 0.0.0.0