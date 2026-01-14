#!/bin/bash

# Start FastAPI on 8000
uvicorn main:app --host 127.0.0.1 --port 8000 &

# Start Streamlit on 8502 (internal)
streamlit run admin.py --server.port 8502 --server.address 127.0.0.1 &

# Start Nginx using local config
nginx -c /app/nginx.conf &

# Keep container running
wait
