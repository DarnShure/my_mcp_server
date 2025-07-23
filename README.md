# my_mcp_server

This project provides an end-to-end testable MCP (Model Context Protocol) server environment, including a FastAPI-based chatbot generation stub, an MCP server, and a client stub for testing the `generate` tool. The main focus is on enabling easy local testing of the chatbot generation workflow.


## TLDR: This package is responsible for end-to-end pdf preprocessing for llm ingestion.
It adds several features onto pdfplumber

MCP Server Feedback Mechanism
Agentic adaptive pdf parsing.
Iterative evolutionary framework.

## Project Structure

```
my_mcp_server/
├── [`chatbot_generation_stub.py`](chatbot_generation_stub.py )
├── [`client_stub.py`](client_stub.py )
├── common/
│   └── [`common/config.py`](common/config.py )
├── config/
│   └── [`config/custom_config.toml`](config/custom_config.toml )
├── [`main.py`](main.py )
├── [`run_all_test.sh`](run_all_test.sh )
├── [`run_inspector.sh`](run_inspector.sh )
├── [`run_mcp_server.sh`](run_mcp_server.sh )
├── [`server.py`](server.py )
├── [`pyproject.toml`](pyproject.toml )
└── ...
```

## Quick Start: End-to-End Testing

The recommended way to test the full pipeline, including the `generate` tool, is to use the [`run_all_test.sh`](run_all_test.sh) script. This script will:

1. Read the chatbot API port from [`config/custom_config.toml`](config/custom_config.toml).
2. Wait for the chatbot API to be available at the configured port.
3. Start the chatbot API stub ([`chatbot_generation_stub.py`](chatbot_generation_stub.py)).
4. Start the MCP server ([`server.py`](server.py)).
5. Start the MCP inspector ([`run_inspector.sh`](run_inspector.sh)).
6. Optionally, run the client stub ([`client_stub.py`](client_stub.py)) to test the `generate` tool.
7. Clean up all background processes after testing.

### How to Run

1. **Install dependencies**  
   Make sure you have Python 3.10+ and Node.js installed.  
   Install Python dependencies:
   ```sh
   pip install -r requirements.txt
   ```
   Or, if using Poetry or PDM, install via your preferred tool.

2. **Run the test script**  
   From the project root, execute:
   ```sh
   bash run_all_test.sh
   ```

   The script will:
   - Wait for the chatbot API to be available at `http://127.0.0.1:<port>/` (port from config).
   - Start all required services.
   - Prompt you to continue after setup.
   - (Optionally) Run the client stub to test the [`generate`](server.py ) tool.

3. **Test the [`generate`](server.py ) tool**  
   The client stub ([`client_stub.py`](client_stub.py )) connects to the MCP server and calls the [`generate`](server.py ) tool, which in turn calls the chatbot API stub and prints the results.

## Configuration

- The chatbot API port and other settings are configured in [`config/custom_config.toml`](config/custom_config.toml ).
- The MCP server reads its configuration from this file via [`common/config.py`](common/config.py ).

## Components

- **[`chatbot_generation_stub.py`](chatbot_generation_stub.py )**: FastAPI app simulating the chatbot generation endpoint.
- **[`server.py`](server.py )**: MCP server exposing the [`generate`](server.py ) tool.
- **[`client_stub.py`](client_stub.py )**: Example client that connects to the MCP server and tests the [`generate`](server.py ) tool.
- **[`run_all_test.sh`](run_all_test.sh )**: Orchestrates the full end-to-end test environment.

## Notes

- The script assumes all commands (`uv`, `npx`, etc.) are available in your PATH.
- For custom configuration, edit [`config/custom_config.toml`](config/custom_config.toml ).

---

For more details on each component, see