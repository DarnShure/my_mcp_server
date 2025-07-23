from mcp.server.fastmcp import FastMCP
import requests
from string import Template

from src.common.config import set_config_path, get_config_value
from src.index.core import Index
from typing import Dict

# Initialize config (only needed once, e.g., at app startup)
set_config_path('config/custom_config.toml')

# Access the [api] port value
port = get_config_value(['api', 'port'], 5005)  # 5005 is the default if not found
mcp_port = get_config_value(['mcp', 'port'], 3003)

# Access the [RAG] index file
index_path = get_config_value(['rag', 'db_path'], 'chunking_study/processed_sources/index0.db')

# Initialize the MCP server with a name
mcp = FastMCP("Retrieval Server", host="0.0.0.0", port=mcp_port, 
              
              # Encountered problems with SSE(text/event-stream) on client side.
              json_response=True  
              )

# Template for chatbot request
api_format = """{
  "messages": [
    {
      "role": "$user",
      "content": "$content"
    }
  ],
  "temperature": $t,
  "max_tokens": $max
}"""
generate_request_template = Template(api_format)

@mcp.tool()
async def retrieve() -> str:
    """
    Use when customer requests to be reminded about payment at a later time.
    Retrieves a tool response corresponding to the RemindLater intent.
    
    Returns:
        str: A JSON string containing nodes.
    """
    data = {
      
    }
    # requests.post("url")

    return "嗨 \n-Darren"

@mcp.tool()
async def index(doc_path:str) -> str:
    """
    Use when customer requests to be reminded about payment at a later time.
    Retrieves a tool response corresponding to the RemindLater intent.
    
    Returns:
        str: A JSON string containing nodes.
    """
    doc_path = doc_path or 'formatting_study/primary_sources/0_新進同仁入職指南.pdf'
    cur = Index(index_path)
    cur.index_doc(doc_path)
    # requests.post("url")

    return "嗨 \n-Darren"

@mcp.tool()
async def generate(input: Dict) -> str:
    """
    Calls the chatbot FastApi to generate text.
    
    Returns:
        str: A JSON string containing the answer.
    """

    # Prepare payload.
    payload = {
        "messages": [
            {
                "role": input.get('role', 'user'),
                "content": input.get('content')
            }
        ],
        "temperature": input.get('temperature', 1.0),
        "max_tokens": input.get('max', 1000)
    }

    index = input.get('index_name', 'index1')

    # Hard-coded path operation to call chatbot_api
    cb_generate_endpoint = f"http://127.0.0.1:{port}/api/v1/{index}/chats/{input.get('chat_name', 'testChat1')}/generate"
    
    try:
        response = requests.post(cb_generate_endpoint, json=payload)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    
    # Start the MCP server using http transport
    mcp.run(transport="streamable-http")
