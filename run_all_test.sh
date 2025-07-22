#!/bin/bash
# Run all components for end-to-end testing

# Read API port from config/custom_config.toml
API_PORT=$(grep -E '^port\s*=' config/custom_config.toml | head -n1 | awk -F'=' '{gsub(/[ \t]/,"",$2); print $2}')

# Remove quotes if present
API_PORT=${API_PORT//\'/}

# Ping the chatbot API until it responds
echo "Waiting for chatbot API to be available at http://127.0.0.1:$API_PORT/ ..."
until curl -s "http://127.0.0.1:$API_PORT/" > /dev/null; do
    printf '.'
    sleep 1
done
echo "Chatbot API is up!"

# Start the API stub (chatbot_generation_stub.py) in the background
uv chatbot_generation_stub.py &
API_PID=$!
echo "Started API stub (PID $API_PID)"

# Wait a bit to ensure the API stub is up
sleep 2

# Start the MCP server in the background
bash run_mcp_server.sh &
MCP_PID=$!
echo "Started MCP server (PID $MCP_PID)"

# Run inspector
bash run_inspector.sh &
INSPECT_PID=$!
echo "Started MCP inspector (PID $MCP_PID)"

# Wait a bit to ensure the MCP server is up
# Keep the script polling until you press 'n'.
read -p "Press 'n' to continue: " key
while [[ "$key" != "n" ]]; do
    read -p "Please press 'n' to continue: " key
done

# # (Optional)
# # Run the client stub (this will block until done)
# uv client_stub.py


# Kill background processes after client is done
echo "Killing inspector (PID $INSPECT_PID) and MCP server