import asyncio
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
from mcp.client.stdio import stdio_client
import asyncio
from typing import Optional
from contextlib import AsyncExitStack



from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class MyMcpClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
    # methods will go here

    async def connect_to_server(self, url: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        http_server_headers ={'Accepts':'text/event-stream'} 
        http_server_headers = None


        streamable_http_transport = await self.exit_stack.enter_async_context(
            streamablehttp_client(
                url=url,
                headers=http_server_headers
                )
            )
        self.rx_stream, self.tx_stream, get_session_id_callback = streamable_http_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.rx_stream, self.rx_stream))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def test_tool_stub(self):
        tool_name = 'generate'
        tool_args = {
            "index_name" : "index1",
            "chat_name" : "testChat",
            "role" : "user",
            "content" : "Tell me the story about the donkey.",
            "temperature" : "1",
            "max" : "500"}

        result = await self.session.call_tool(tool_name, tool_args)
        return
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
        
async def main():
    
    mcp_server_endpoint = "http://127.0.0.1:3003/mcp/"


    client = MyMcpClient()
    try:
        await client.connect_to_server(mcp_server_endpoint)
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

