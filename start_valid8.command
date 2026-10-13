#!/bin/bash
cd "$(dirname "$0")"
# --- Backend Setup ---
echo "Cleaning up ports..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null
echo "Setting up Backend..."
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate
echo "Installing Python dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "Starting Backend Server..."
python3 main.py &
BACKEND_PID=$!

# --- Frontend Setup ---
echo "Setting up Frontend..."
echo "Installing Node dependencies..."
npm install > /dev/null 2>&1
echo "Starting Frontend Server..."
npm run dev &
FRONTEND_PID=$!

# --- Launch ---
echo "Waiting for servers to initialize..."
sleep 5
echo "Opening Browser..."
open http://localhost:5173

# --- Cleanup ---
echo "App is running. Close this window to stop."
wait
