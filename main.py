from server import mcp

def main():
    print("Hello from my mcp server!")
    
    # Start the MCP server using http transport
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    main()
