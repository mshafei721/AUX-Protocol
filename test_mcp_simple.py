"""Simple MCP server test to debug communication issues."""

import asyncio
import json
import subprocess
import sys
import time


async def test_mcp_server_simple():
    """Test MCP server with simple JSON-RPC communication."""
    
    print("🔧 Testing MCP Server Communication")
    print("-" * 40)
    
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
                    "name": "aux-simple-test",
                    "version": "0.1.0"
                }
            }
        }
        
        # Send request
        message = json.dumps(init_request) + "\n"
        process.stdin.write(message.encode())
        await process.stdin.drain()
        print("✅ Initialization request sent")
        
        # Read response with timeout
        try:
            response_line = await asyncio.wait_for(
                process.stdout.readline(), 
                timeout=5.0
            )
            
            if response_line:
                response_text = response_line.decode().strip()
                print(f"📨 Raw response: {response_text[:200]}...")
                
                try:
                    response = json.loads(response_text)
                    print("✅ Valid JSON response received")
                    
                    if "result" in response:
                        print("✅ Initialization successful")
                        return True
                    else:
                        print(f"❌ Error in response: {response}")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response: {e}")
                    print(f"Raw response: {response_text}")
                    return False
            else:
                print("❌ No response received")
                return False
                
        except asyncio.TimeoutError:
            print("❌ Response timeout")
            return False
            
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False
        
    finally:
        if 'process' in locals():
            process.terminate()
            await process.wait()
            print("✅ Server process terminated")


async def test_server_startup():
    """Test if server can start without errors."""
    
    print("\n🚀 Testing Server Startup")
    print("-" * 40)
    
    try:
        # Start server and capture stderr for errors
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "aux_protocol.server",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait a bit and check if process is still running
        await asyncio.sleep(2)
        
        if process.returncode is None:
            print("✅ Server started successfully")
            
            # Check for any error messages
            try:
                stderr_data = await asyncio.wait_for(
                    process.stderr.read(1024), 
                    timeout=1.0
                )
                if stderr_data:
                    stderr_text = stderr_data.decode()
                    if stderr_text.strip():
                        print(f"⚠️ Server stderr: {stderr_text}")
            except asyncio.TimeoutError:
                pass  # No stderr output, which is good
            
            process.terminate()
            await process.wait()
            return True
        else:
            print(f"❌ Server exited with code: {process.returncode}")
            
            # Read stderr for error details
            stderr_data = await process.stderr.read()
            if stderr_data:
                print(f"Error output: {stderr_data.decode()}")
            
            return False
            
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 AUX Protocol MCP Server Simple Tests")
    print("=" * 50)
    
    async def run_tests():
        results = []
        
        # Test server startup
        startup_success = await test_server_startup()
        results.append(("Server Startup", startup_success))
        
        # Test MCP communication
        if startup_success:
            comm_success = await test_mcp_server_simple()
            results.append(("MCP Communication", comm_success))
        else:
            results.append(("MCP Communication", False))
        
        # Summary
        print(f"\n📊 Test Results:")
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} - {test_name}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        return passed == total
    
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)