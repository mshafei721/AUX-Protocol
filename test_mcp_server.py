"""Test script for AUX Protocol MCP server."""

import asyncio
import json
import subprocess
import sys
from typing import Dict, Any


class MCPTestClient:
    """Simple MCP client for testing."""
    
    def __init__(self):
        self.process = None
        self.request_id = 0
        
    async def start_server(self):
        """Start the MCP server process."""
        self.process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "aux_protocol.server",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Send initialization
        init_request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "aux-test-client",
                    "version": "0.1.0"
                }
            }
        }
        
        await self._send_request(init_request)
        response = await self._read_response()
        print("Initialization response:", json.dumps(response, indent=2))
        
    async def stop_server(self):
        """Stop the MCP server."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            
    async def list_tools(self):
        """List available tools."""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list"
        }
        
        await self._send_request(request)
        return await self._read_response()
        
    async def call_tool(self, name: str, arguments: Dict[str, Any]):
        """Call a tool."""
        request = {
            "jsonrpc": "2.0", 
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            }
        }
        
        await self._send_request(request)
        return await self._read_response()
        
    async def list_resources(self):
        """List available resources."""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(), 
            "method": "resources/list"
        }
        
        await self._send_request(request)
        return await self._read_response()
        
    def _next_id(self):
        """Get next request ID."""
        self.request_id += 1
        return self.request_id
        
    async def _send_request(self, request: Dict[str, Any]):
        """Send JSON-RPC request."""
        message = json.dumps(request) + "\n"
        self.process.stdin.write(message.encode())
        await self.process.stdin.drain()
        
    async def _read_response(self):
        """Read JSON-RPC response."""
        line = await self.process.stdout.readline()
        return json.loads(line.decode().strip())


async def test_mcp_server():
    """Test the AUX Protocol MCP server."""
    
    client = MCPTestClient()
    
    try:
        print("Starting AUX Protocol MCP server...")
        await client.start_server()
        
        # Test listing tools
        print("\n1. Testing tool listing...")
        tools_response = await client.list_tools()
        
        if "result" in tools_response:
            tools = tools_response["result"]["tools"]
            print(f"Found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
        else:
            print("Error listing tools:", tools_response)
            
        # Test listing resources
        print("\n2. Testing resource listing...")
        resources_response = await client.list_resources()
        
        if "result" in resources_response:
            resources = resources_response["result"]["resources"]
            print(f"Found {len(resources)} resources:")
            for resource in resources:
                print(f"  - {resource['uri']}: {resource['name']}")
        else:
            print("Error listing resources:", resources_response)
            
        # Test starting browser
        print("\n3. Testing browser startup...")
        start_response = await client.call_tool("aux_start_browser", {"headless": True})
        
        if "result" in start_response:
            print("Browser started:", start_response["result"]["content"][0]["text"])
        else:
            print("Error starting browser:", start_response)
            return
            
        # Test navigation
        print("\n4. Testing navigation...")
        nav_response = await client.call_tool("aux_navigate", {
            "url": "https://example.com"
        })
        
        if "result" in nav_response:
            print("Navigation result:", nav_response["result"]["content"][0]["text"])
        else:
            print("Error navigating:", nav_response)
            
        # Test observation
        print("\n5. Testing page observation...")
        observe_response = await client.call_tool("aux_observe", {})
        
        if "result" in observe_response:
            result_text = observe_response["result"]["content"][0]["text"]
            print("Observation result:")
            print(result_text[:500] + "..." if len(result_text) > 500 else result_text)
        else:
            print("Error observing:", observe_response)
            
        # Test element query
        print("\n6. Testing element query...")
        query_response = await client.call_tool("aux_query", {
            "element_type": "link",
            "limit": 3
        })
        
        if "result" in query_response:
            print("Query result:", query_response["result"]["content"][0]["text"])
        else:
            print("Error querying:", query_response)
            
        # Test stopping browser
        print("\n7. Testing browser shutdown...")
        stop_response = await client.call_tool("aux_stop_browser", {})
        
        if "result" in stop_response:
            print("Browser stopped:", stop_response["result"]["content"][0]["text"])
        else:
            print("Error stopping browser:", stop_response)
            
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await client.stop_server()


if __name__ == "__main__":
    print("AUX Protocol MCP Server Test")
    print("=" * 40)
    asyncio.run(test_mcp_server())