"""Debug MCP parameter validation issues."""

import asyncio
import json
import sys


async def test_specific_tool_calls():
    """Test specific tool calls to identify parameter issues."""
    
    print("🔍 Debugging MCP Parameter Validation")
    print("-" * 50)
    
    try:
        # Start the server process
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "aux_protocol.server",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        print("✅ Server process started")
        
        # Give server time to initialize
        await asyncio.sleep(1)
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "aux-debug-test",
                    "version": "0.1.0"
                }
            }
        }
        
        # Send request
        message = json.dumps(init_request) + "\n"
        process.stdin.write(message.encode())
        await process.stdin.drain()
        
        # Read response
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
        response = json.loads(response_line.decode().strip())
        print("✅ Initialization successful")
        
        # Test aux_start_browser with explicit parameters
        print("\n🧪 Testing aux_start_browser...")
        browser_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "aux_start_browser",
                "arguments": {
                    "headless": True
                }
            }
        }
        
        message = json.dumps(browser_request) + "\n"
        process.stdin.write(message.encode())
        await process.stdin.drain()
        
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
        response = json.loads(response_line.decode().strip())
        
        if "result" in response:
            print("✅ aux_start_browser successful")
        else:
            print(f"❌ aux_start_browser failed: {response}")
            return False
        
        # Test aux_navigate with required parameters
        print("\n🧪 Testing aux_navigate...")
        nav_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "aux_navigate",
                "arguments": {
                    "url": "https://httpbin.org/html"
                }
            }
        }
        
        message = json.dumps(nav_request) + "\n"
        process.stdin.write(message.encode())
        await process.stdin.drain()
        
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=15.0)
        response = json.loads(response_line.decode().strip())
        
        if "result" in response:
            print("✅ aux_navigate successful")
        else:
            print(f"❌ aux_navigate failed: {response}")
            return False
        
        # Test aux_observe with no parameters
        print("\n🧪 Testing aux_observe...")
        observe_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "aux_observe",
                "arguments": {}
            }
        }
        
        message = json.dumps(observe_request) + "\n"
        process.stdin.write(message.encode())
        await process.stdin.drain()
        
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
        response = json.loads(response_line.decode().strip())
        
        if "result" in response:
            print("✅ aux_observe successful")
        else:
            print(f"❌ aux_observe failed: {response}")
            return False
        
        # Test aux_stop_browser
        print("\n🧪 Testing aux_stop_browser...")
        stop_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "aux_stop_browser",
                "arguments": {}
            }
        }
        
        message = json.dumps(stop_request) + "\n"
        process.stdin.write(message.encode())
        await process.stdin.drain()
        
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
        response = json.loads(response_line.decode().strip())
        
        if "result" in response:
            print("✅ aux_stop_browser successful")
        else:
            print(f"❌ aux_stop_browser failed: {response}")
            return False
        
        print("\n🎉 All basic MCP tool calls successful!")
        return True
        
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if 'process' in locals():
            process.terminate()
            await process.wait()


if __name__ == "__main__":
    success = asyncio.run(test_specific_tool_calls())
    sys.exit(0 if success else 1)