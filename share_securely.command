#!/bin/bash
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}      ${GREEN}Valid8 Pro - Quick Share${NC}                          ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    kill $TUNNEL_PID 2>/dev/null
    echo -e "${GREEN}✓ All services stopped.${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM

# --- Backend Setup ---
echo -e "${BLUE}[1/3]${NC} Starting Backend Server..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
python3 main.py > /dev/null 2>&1 &
BACKEND_PID=$!
echo -e "  ${GREEN}✓${NC} Backend started (PID: $BACKEND_PID)"

# --- Frontend Setup ---
echo -e "${BLUE}[2/3]${NC} Starting Frontend Server..."
npm install > /dev/null 2>&1
npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!
echo -e "  ${GREEN}✓${NC} Frontend started (PID: $FRONTEND_PID)"

echo ""
echo -e "${YELLOW}Waiting for servers to initialize...${NC}"
sleep 6

# --- Tunnel Setup ---
echo -e "${BLUE}[3/3]${NC} Creating Public Tunnel..."
echo ""

# Use localtunnel via npx (no installation required)
echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
echo -e "  ${GREEN}Your app is being shared publicly!${NC}"
echo ""
echo -e "  ${YELLOW}Look for the URL starting with https://...${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
echo ""

# Create tunnel using localtunnel - more reliable than localhost.run
npx --yes localtunnel --port 5173 &
TUNNEL_PID=$!

# Wait for tunnel to be ready and show the URL
sleep 3

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  SHARING ACTIVE - Press Ctrl+C to stop                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Note: Visitors may need to click 'Continue' on the first page${NC}"
echo ""

# Keep script running
wait $TUNNEL_PID
