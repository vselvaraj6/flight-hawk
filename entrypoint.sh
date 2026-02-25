#!/bin/bash
set -e

echo "Starting Flight Tracker..."

# Start the background price checker
echo "Starting price checker scheduler..."
python main.py &

# Start the Streamlit dashboard (foreground)
echo "Starting Streamlit dashboard on port 8501..."
exec streamlit run app.py --server.headless true --server.port 8501 --server.address 0.0.0.0
