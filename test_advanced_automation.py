"""Comprehensive test suite for AUX Protocol advanced automation tools."""

import asyncio
import json
import sys
from typing import Dict, Any


class AdvancedMCPTestClient:
    """Enhanced MCP client for testing advanced automation features."""
    
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
                    "name": "aux-advanced-test-client",
                    "version": "0.1.0"
                }
            }
        }
        
        await self._send_request(init_request)
        response = await self._read_response()
        return "result" in response
        
    async def stop_server(self):
        """Stop the MCP server."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            
    async def call_tool(self, name: str, arguments: Dict[str, Any]):
        """Call a tool and return the response."""
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
        
    async def list_tools(self):
        """List available tools."""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list"
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


async def test_basic_functionality():
    """Test basic browser operations."""
    print("🔧 Testing Basic Functionality")
    print("-" * 40)
    
    client = AdvancedMCPTestClient()
    
    try:
        # Start server
        await client.start_server()
        print("✅ Server started")
        
        # Start browser
        response = await client.call_tool("aux_start_browser", {"headless": True})
        if "result" in response:
            print("✅ Browser started")
        else:
            print("❌ Browser start failed:", response)
            return False
            
        # Navigate to test page
        response = await client.call_tool("aux_navigate", {
            "url": "https://httpbin.org/forms/post"
        })
        if "result" in response:
            print("✅ Navigation successful")
        else:
            print("❌ Navigation failed:", response)
            return False
            
        # Test observation
        response = await client.call_tool("aux_observe", {})
        if "result" in response:
            print("✅ Page observation successful")
        else:
            print("❌ Observation failed:", response)
            return False
            
        # Stop browser
        await client.call_tool("aux_stop_browser", {})
        print("✅ Browser stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False
        
    finally:
        await client.stop_server()


async def test_advanced_tools_availability():
    """Test that advanced tools are available after browser start."""
    print("\n🛠️ Testing Advanced Tools Availability")
    print("-" * 40)
    
    client = AdvancedMCPTestClient()
    
    try:
        await client.start_server()
        
        # List tools before browser start
        response = await client.list_tools()
        tools_before = [tool["name"] for tool in response["result"]["tools"]]
        basic_tools_count = len(tools_before)
        print(f"📊 Tools before browser start: {basic_tools_count}")
        
        # Start browser
        await client.call_tool("aux_start_browser", {"headless": True})
        
        # List tools after browser start
        response = await client.list_tools()
        tools_after = [tool["name"] for tool in response["result"]["tools"]]
        advanced_tools_count = len(tools_after)
        print(f"📊 Tools after browser start: {advanced_tools_count}")
        
        # Check for advanced tools
        expected_advanced_tools = [
            "aux_fill_form",
            "aux_wait_for_element", 
            "aux_extract_data",
            "aux_workflow"
        ]
        
        missing_tools = []
        for tool in expected_advanced_tools:
            if tool in tools_after:
                print(f"✅ {tool} available")
            else:
                print(f"❌ {tool} missing")
                missing_tools.append(tool)
        
        await client.call_tool("aux_stop_browser", {})
        
        return len(missing_tools) == 0
        
    except Exception as e:
        print(f"❌ Advanced tools test failed: {e}")
        return False
        
    finally:
        await client.stop_server()


async def test_form_filling():
    """Test intelligent form filling capabilities."""
    print("\n🤖 Testing Form Filling")
    print("-" * 40)
    
    client = AdvancedMCPTestClient()
    
    try:
        await client.start_server()
        await client.call_tool("aux_start_browser", {"headless": True})
        
        # Navigate to form page
        await client.call_tool("aux_navigate", {
            "url": "https://httpbin.org/forms/post"
        })
        
        # Test form filling
        response = await client.call_tool("aux_fill_form", {
            "form_data": {
                "custname": "AUX Test User",
                "custtel": "+1-555-TEST",
                "custemail": "test@aux-protocol.com",
                "size": "large",
                "comments": "Automated test via AUX Protocol"
            },
            "clear_first": True,
            "submit": False  # Don't submit for testing
        })
        
        if "result" in response:
            result_text = response["result"]["content"][0]["text"]
            if "✅" in result_text and "Filled" in result_text:
                print("✅ Form filling successful")
                print(f"📝 Result: {result_text[:200]}...")
                success = True
            else:
                print("❌ Form filling had issues")
                print(f"📝 Result: {result_text}")
                success = False
        else:
            print("❌ Form filling failed:", response)
            success = False
            
        await client.call_tool("aux_stop_browser", {})
        return success
        
    except Exception as e:
        print(f"❌ Form filling test failed: {e}")
        return False
        
    finally:
        await client.stop_server()


async def test_data_extraction():
    """Test structured data extraction."""
    print("\n📊 Testing Data Extraction")
    print("-" * 40)
    
    client = AdvancedMCPTestClient()
    
    try:
        await client.start_server()
        await client.call_tool("aux_start_browser", {"headless": True})
        
        # Navigate to a page with structured content
        await client.call_tool("aux_navigate", {
            "url": "https://httpbin.org/html"
        })
        
        # Test data extraction
        response = await client.call_tool("aux_extract_data", {
            "extraction_rules": {
                "page_title": {
                    "selector": "title",
                    "attribute": "text"
                },
                "headings": {
                    "selector": "h1, h2, h3",
                    "attribute": "text",
                    "multiple": True,
                    "transform": "trim"
                },
                "links": {
                    "selector": "a",
                    "attribute": "href",
                    "multiple": True
                },
                "paragraphs": {
                    "selector": "p",
                    "attribute": "text",
                    "multiple": True
                }
            },
            "output_format": "json"
        })
        
        if "result" in response:
            result_text = response["result"]["content"][0]["text"]
            if "Extracted data:" in result_text:
                print("✅ Data extraction successful")
                # Try to parse the JSON to verify it's valid
                try:
                    json_start = result_text.find("{")
                    if json_start != -1:
                        json_data = json.loads(result_text[json_start:])
                        print(f"📊 Extracted {len(json_data)} data fields")
                        success = True
                    else:
                        print("⚠️ No JSON data found in response")
                        success = False
                except json.JSONDecodeError:
                    print("⚠️ Invalid JSON in extraction result")
                    success = False
            else:
                print("❌ Data extraction had issues")
                success = False
        else:
            print("❌ Data extraction failed:", response)
            success = False
            
        await client.call_tool("aux_stop_browser", {})
        return success
        
    except Exception as e:
        print(f"❌ Data extraction test failed: {e}")
        return False
        
    finally:
        await client.stop_server()


async def test_waiting_functionality():
    """Test dynamic waiting capabilities."""
    print("\n⏳ Testing Dynamic Waiting")
    print("-" * 40)
    
    client = AdvancedMCPTestClient()
    
    try:
        await client.start_server()
        await client.call_tool("aux_start_browser", {"headless": True})
        
        # Navigate to a page
        await client.call_tool("aux_navigate", {
            "url": "https://httpbin.org/html"
        })
        
        # Test waiting for element to appear
        response = await client.call_tool("aux_wait_for_element", {
            "selector": "body",
            "condition": "appear",
            "timeout": 5.0,
            "poll_interval": 0.5
        })
        
        if "result" in response:
            result_text = response["result"]["content"][0]["text"]
            if "appeared" in result_text.lower() or "Element" in result_text:
                print("✅ Element waiting successful")
                success = True
            else:
                print("❌ Element waiting had issues")
                print(f"📝 Result: {result_text}")
                success = False
        else:
            print("❌ Element waiting failed:", response)
            success = False
            
        await client.call_tool("aux_stop_browser", {})
        return success
        
    except Exception as e:
        print(f"❌ Waiting functionality test failed: {e}")
        return False
        
    finally:
        await client.stop_server()


async def test_workflow_automation():
    """Test multi-step workflow automation."""
    print("\n🔄 Testing Workflow Automation")
    print("-" * 40)
    
    client = AdvancedMCPTestClient()
    
    try:
        await client.start_server()
        await client.call_tool("aux_start_browser", {"headless": True})
        
        # Test a simple workflow
        response = await client.call_tool("aux_workflow", {
            "steps": [
                {
                    "action": "navigate",
                    "params": {
                        "url": "https://httpbin.org/html",
                        "wait_for_load": True
                    }
                },
                {
                    "action": "wait",
                    "params": {"seconds": 1}
                },
                {
                    "action": "extract",
                    "params": {
                        "extraction_rules": {
                            "title": {
                                "selector": "title",
                                "attribute": "text"
                            }
                        },
                        "output_format": "json"
                    }
                }
            ],
            "continue_on_error": False
        })
        
        if "result" in response:
            result_text = response["result"]["content"][0]["text"]
            if "✅" in result_text and "steps executed" in result_text:
                print("✅ Workflow automation successful")
                print(f"📝 Result: {result_text[:200]}...")
                success = True
            else:
                print("❌ Workflow automation had issues")
                print(f"📝 Result: {result_text}")
                success = False
        else:
            print("❌ Workflow automation failed:", response)
            success = False
            
        await client.call_tool("aux_stop_browser", {})
        return success
        
    except Exception as e:
        print(f"❌ Workflow automation test failed: {e}")
        return False
        
    finally:
        await client.stop_server()


async def run_comprehensive_test():
    """Run all advanced automation tests."""
    print("🚀 AUX Protocol Advanced Automation Test Suite")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Advanced Tools Availability", test_advanced_tools_availability),
        ("Form Filling", test_form_filling),
        ("Data Extraction", test_data_extraction),
        ("Dynamic Waiting", test_waiting_functionality),
        ("Workflow Automation", test_workflow_automation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running {test_name} Test...")
            success = await test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
                
        except Exception as e:
            print(f"💥 {test_name} test CRASHED: {e}")
            results.append((test_name, False))
        
        print("-" * 60)
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! AUX Protocol is ready for production.")
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
    
    return passed == total


if __name__ == "__main__":
    print("Starting AUX Protocol Advanced Automation Test Suite...")
    success = asyncio.run(run_comprehensive_test())
    sys.exit(0 if success else 1)