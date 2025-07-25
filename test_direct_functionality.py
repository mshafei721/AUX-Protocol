"""Direct functionality test for AUX Protocol without MCP server."""

import asyncio
from aux_protocol.browser_adapter import BrowserAdapter
from aux_protocol.schema import NavigationCommand, QueryCommand
from aux_protocol.tools import (
    FillFormTool,
    WaitForElementTool,
    ExtractDataTool,
    WorkflowTool,
)


async def test_browser_basic_operations():
    """Test basic browser operations."""
    print("🌐 Testing Basic Browser Operations")
    print("-" * 40)
    
    adapter = BrowserAdapter(headless=True)
    
    try:
        # Start browser
        await adapter.start()
        print("✅ Browser started successfully")
        
        # Navigate to a test page
        nav_command = NavigationCommand(url="https://httpbin.org/html")
        observation = await adapter.navigate(nav_command)
        print(f"✅ Navigation successful - found {len(observation.browser_state.elements)} elements")
        
        # Test observation
        observation = await adapter.observe()
        print(f"✅ Page observation successful - URL: {observation.browser_state.url}")
        
        # Test element querying
        query = QueryCommand(selector="h1", limit=5)
        elements = await adapter.query_elements(query)
        print(f"✅ Element query successful - found {len(elements)} h1 elements")
        
        return True
        
    except Exception as e:
        print(f"❌ Browser operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await adapter.stop()
        print("✅ Browser stopped")


async def test_form_filling_direct():
    """Test form filling functionality directly."""
    print("\n🤖 Testing Form Filling")
    print("-" * 40)
    
    adapter = BrowserAdapter(headless=True)
    
    try:
        await adapter.start()
        
        # Navigate to form page
        nav_command = NavigationCommand(url="https://httpbin.org/forms/post")
        await adapter.navigate(nav_command)
        print("✅ Navigated to form page")
        
        # Create form filling tool
        form_tool = FillFormTool(adapter)
        
        # Test form filling
        result = await form_tool.execute({
            "form_data": {
                "custname": "Test User",
                "custemail": "test@example.com",
                "comments": "Direct test"
            },
            "clear_first": True,
            "submit": False
        })
        
        result_text = result[0].text
        if "✅" in result_text and "Filled" in result_text:
            print("✅ Form filling successful")
            return True
        else:
            print(f"⚠️ Form filling had issues: {result_text}")
            return False
        
    except Exception as e:
        print(f"❌ Form filling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await adapter.stop()


async def test_data_extraction_direct():
    """Test data extraction functionality directly."""
    print("\n📊 Testing Data Extraction")
    print("-" * 40)
    
    adapter = BrowserAdapter(headless=True)
    
    try:
        await adapter.start()
        
        # Navigate to a page with content
        nav_command = NavigationCommand(url="https://httpbin.org/html")
        await adapter.navigate(nav_command)
        print("✅ Navigated to test page")
        
        # Create extraction tool
        extract_tool = ExtractDataTool(adapter)
        
        # Test data extraction
        result = await extract_tool.execute({
            "extraction_rules": {
                "title": {
                    "selector": "title",
                    "attribute": "text"
                },
                "headings": {
                    "selector": "h1",
                    "attribute": "text",
                    "multiple": True
                }
            },
            "output_format": "json"
        })
        
        result_text = result[0].text
        if "Extracted data:" in result_text:
            print("✅ Data extraction successful")
            return True
        else:
            print(f"⚠️ Data extraction had issues: {result_text}")
            return False
        
    except Exception as e:
        print(f"❌ Data extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await adapter.stop()


async def test_waiting_functionality_direct():
    """Test waiting functionality directly."""
    print("\n⏳ Testing Waiting Functionality")
    print("-" * 40)
    
    adapter = BrowserAdapter(headless=True)
    
    try:
        await adapter.start()
        
        # Navigate to a page
        nav_command = NavigationCommand(url="https://httpbin.org/html")
        await adapter.navigate(nav_command)
        print("✅ Navigated to test page")
        
        # Create wait tool
        wait_tool = WaitForElementTool(adapter)
        
        # Test waiting for element that should exist
        result = await wait_tool.execute({
            "selector": "body",
            "condition": "appear",
            "timeout": 5.0
        })
        
        result_text = result[0].text
        if "appeared" in result_text.lower() or "Element" in result_text:
            print("✅ Element waiting successful")
            return True
        else:
            print(f"⚠️ Element waiting had issues: {result_text}")
            return False
        
    except Exception as e:
        print(f"❌ Waiting functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await adapter.stop()


async def test_workflow_direct():
    """Test workflow functionality directly."""
    print("\n🔄 Testing Workflow Functionality")
    print("-" * 40)
    
    adapter = BrowserAdapter(headless=True)
    
    try:
        await adapter.start()
        
        # Create workflow tool
        workflow_tool = WorkflowTool(adapter)
        
        # Test simple workflow
        result = await workflow_tool.execute({
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
        
        result_text = result[0].text
        if "✅" in result_text and "steps executed" in result_text:
            print("✅ Workflow execution successful")
            return True
        else:
            print(f"⚠️ Workflow had issues: {result_text}")
            return False
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await adapter.stop()


async def run_direct_tests():
    """Run all direct functionality tests."""
    print("🚀 AUX Protocol Direct Functionality Tests")
    print("=" * 60)
    
    tests = [
        ("Basic Browser Operations", test_browser_basic_operations),
        ("Form Filling", test_form_filling_direct),
        ("Data Extraction", test_data_extraction_direct),
        ("Waiting Functionality", test_waiting_functionality_direct),
        ("Workflow Functionality", test_workflow_direct),
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
        print("🎉 All direct tests passed! AUX Protocol core functionality is working.")
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
    
    return passed == total


if __name__ == "__main__":
    print("Starting AUX Protocol Direct Functionality Tests...")
    success = asyncio.run(run_direct_tests())
    
    if success:
        print("\n✨ AUX Protocol is ready for use!")
    else:
        print("\n⚠️ Some issues need to be resolved.")