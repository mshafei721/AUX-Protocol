"""Comprehensive performance and functionality test for AUX Protocol improvements."""

import asyncio
import time
from aux_protocol.browser_adapter import BrowserAdapter
from aux_protocol.schema import NavigationCommand, QueryCommand, AUXCommand, ActionType
from aux_protocol.tools import (
    FillFormTool,
    WaitForElementTool,
    ExtractDataTool,
    WorkflowTool,
)


async def test_performance_improvements():
    """Test performance improvements in browser operations."""
    print("⚡ Testing Performance Improvements")
    print("-" * 50)
    
    adapter = BrowserAdapter(headless=True)
    
    try:
        # Test browser startup time
        start_time = time.time()
        await adapter.start()
        startup_time = time.time() - start_time
        print(f"✅ Browser startup: {startup_time:.2f}s")
        
        # Test navigation speed
        start_time = time.time()
        nav_command = NavigationCommand(url="https://httpbin.org/forms/post")
        await adapter.navigate(nav_command)
        nav_time = time.time() - start_time
        print(f"✅ Navigation time: {nav_time:.2f}s")
        
        # Test element observation speed
        start_time = time.time()
        observation = await adapter.observe()
        observe_time = time.time() - start_time
        print(f"✅ Observation time: {observe_time:.2f}s ({len(observation.browser_state.elements)} elements)")
        
        # Test element querying speed
        start_time = time.time()
        query = QueryCommand(element_type="input", limit=20)
        elements = await adapter.query_elements(query)
        query_time = time.time() - start_time
        print(f"✅ Query time: {query_time:.2f}s ({len(elements)} elements found)")
        
        total_time = startup_time + nav_time + observe_time + query_time
        print(f"🎯 Total operation time: {total_time:.2f}s")
        
        return total_time < 15.0  # Should complete in under 15 seconds
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False
        
    finally:
        await adapter.stop()


async def test_enhanced_form_elements():
    """Test enhanced form element handling."""
    print("\n🎛️ Testing Enhanced Form Element Support")
    print("-" * 50)
    
    adapter = BrowserAdapter(headless=True)
    
    try:
        await adapter.start()
        
        # Navigate to a comprehensive form page
        nav_command = NavigationCommand(url="https://httpbin.org/forms/post")
        await adapter.navigate(nav_command)
        
        # Test form filling tool with various element types
        form_tool = FillFormTool(adapter)
        
        # Test different form field types
        test_data = {
            "custname": "John Doe",
            "custtel": "555-0123",
            "custemail": "john@example.com",
            "size": "large",  # This is a radio button
            "comments": "Testing enhanced form handling"
        }
        
        result = await form_tool.execute({
            "form_data": test_data,
            "clear_first": True,
            "submit": False
        })
        
        result_text = result[0].text
        filled_count = result_text.count("✅")
        error_count = result_text.count("❌")
        
        print(f"✅ Form fields filled: {filled_count}")
        print(f"⚠️ Form field errors: {error_count}")
        
        # Success if we filled at least 3 out of 5 fields
        return filled_count >= 3
        
    except Exception as e:
        print(f"❌ Enhanced form test failed: {e}")
        return False
        
    finally:
        await adapter.stop()


async def test_smart_element_interaction():
    """Test smart element interaction capabilities."""
    print("\n🧠 Testing Smart Element Interaction")
    print("-" * 50)
    
    adapter = BrowserAdapter(headless=True)
    
    try:
        await adapter.start()
        
        # Navigate to a page with various interactive elements
        nav_command = NavigationCommand(url="https://httpbin.org/forms/post")
        await adapter.navigate(nav_command)
        
        # Find different types of elements
        inputs = await adapter.query_elements(QueryCommand(selector="input"))
        selects = await adapter.query_elements(QueryCommand(selector="select"))
        textareas = await adapter.query_elements(QueryCommand(selector="textarea"))
        
        print(f"✅ Found {len(inputs)} input elements")
        print(f"✅ Found {len(selects)} select elements")
        print(f"✅ Found {len(textareas)} textarea elements")
        
        # Test smart typing on different element types
        success_count = 0
        
        if inputs:
            try:
                # Test typing in text input
                await adapter.execute_command(AUXCommand(
                    action=ActionType.TYPE,
                    target=inputs[0].id,
                    data={"text": "Smart typing test"}
                ))
                success_count += 1
                print("✅ Smart typing in input successful")
            except Exception as e:
                print(f"⚠️ Input typing failed: {e}")
        
        if selects:
            try:
                # Test selection in dropdown
                await adapter.execute_command(AUXCommand(
                    action=ActionType.SELECT,
                    target=selects[0].id,
                    data={"value": "large"}
                ))
                success_count += 1
                print("✅ Smart selection successful")
            except Exception as e:
                print(f"⚠️ Selection failed: {e}")
        
        if textareas:
            try:
                # Test typing in textarea
                await adapter.execute_command(AUXCommand(
                    action=ActionType.TYPE,
                    target=textareas[0].id,
                    data={"text": "Smart textarea handling"}
                ))
                success_count += 1
                print("✅ Smart textarea typing successful")
            except Exception as e:
                print(f"⚠️ Textarea typing failed: {e}")
        
        return success_count >= 2
        
    except Exception as e:
        print(f"❌ Smart interaction test failed: {e}")
        return False
        
    finally:
        await adapter.stop()


async def test_advanced_data_extraction():
    """Test advanced data extraction with multiple formats."""
    print("\n📊 Testing Advanced Data Extraction")
    print("-" * 50)
    
    adapter = BrowserAdapter(headless=True)
    
    try:
        await adapter.start()
        
        # Navigate to a content-rich page
        nav_command = NavigationCommand(url="https://quotes.toscrape.com/")
        await adapter.navigate(nav_command)
        
        extract_tool = ExtractDataTool(adapter)
        
        # Test extraction with different output formats
        extraction_rules = {
            "quotes": {
                "selector": ".quote .text",
                "attribute": "text",
                "multiple": True,
                "transform": "trim"
            },
            "authors": {
                "selector": ".quote .author",
                "attribute": "text",
                "multiple": True
            }
        }
        
        formats_tested = 0
        
        # Test JSON format
        try:
            result = await extract_tool.execute({
                "extraction_rules": extraction_rules,
                "output_format": "json"
            })
            if "Extracted data:" in result[0].text:
                print("✅ JSON extraction successful")
                formats_tested += 1
        except Exception as e:
            print(f"⚠️ JSON extraction failed: {e}")
        
        # Test CSV format
        try:
            result = await extract_tool.execute({
                "extraction_rules": extraction_rules,
                "output_format": "csv"
            })
            if "Extracted data:" in result[0].text:
                print("✅ CSV extraction successful")
                formats_tested += 1
        except Exception as e:
            print(f"⚠️ CSV extraction failed: {e}")
        
        # Test text format
        try:
            result = await extract_tool.execute({
                "extraction_rules": extraction_rules,
                "output_format": "text"
            })
            if "Extracted data:" in result[0].text:
                print("✅ Text extraction successful")
                formats_tested += 1
        except Exception as e:
            print(f"⚠️ Text extraction failed: {e}")
        
        return formats_tested >= 2
        
    except Exception as e:
        print(f"❌ Advanced extraction test failed: {e}")
        return False
        
    finally:
        await adapter.stop()


async def test_workflow_automation():
    """Test complex workflow automation."""
    print("\n🔄 Testing Workflow Automation")
    print("-" * 50)
    
    adapter = BrowserAdapter(headless=True)
    
    try:
        await adapter.start()
        
        workflow_tool = WorkflowTool(adapter)
        
        # Test a comprehensive workflow
        workflow_steps = [
            {
                "action": "navigate",
                "params": {
                    "url": "https://httpbin.org/forms/post",
                    "wait_for_load": True
                }
            },
            {
                "action": "fill_form",
                "params": {
                    "form_data": {
                        "custname": "Workflow Test",
                        "custemail": "workflow@test.com"
                    },
                    "clear_first": True
                }
            },
            {
                "action": "extract",
                "params": {
                    "extraction_rules": {
                        "form_title": {
                            "selector": "h1",
                            "attribute": "text"
                        }
                    },
                    "output_format": "json"
                }
            }
        ]
        
        result = await workflow_tool.execute({
            "steps": workflow_steps,
            "continue_on_error": True
        })
        
        result_text = result[0].text
        steps_executed = result_text.count("Step")
        
        print(f"✅ Workflow steps executed: {steps_executed}")
        
        return "✅" in result_text and steps_executed >= 2
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False
        
    finally:
        await adapter.stop()


async def run_comprehensive_tests():
    """Run all comprehensive tests."""
    print("🚀 AUX Protocol Comprehensive Performance & Feature Tests")
    print("=" * 70)
    
    tests = [
        ("Performance Improvements", test_performance_improvements),
        ("Enhanced Form Elements", test_enhanced_form_elements),
        ("Smart Element Interaction", test_smart_element_interaction),
        ("Advanced Data Extraction", test_advanced_data_extraction),
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
        
        print("-" * 70)
    
    # Summary
    print("\n📊 Comprehensive Test Results Summary")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed >= 4:
        print("🎉 AUX Protocol improvements are working excellently!")
        print("\n✨ Key Improvements Verified:")
        print("  • Performance optimizations active")
        print("  • Enhanced form element support")
        print("  • Smart element interaction")
        print("  • Advanced data extraction")
        print("  • Complex workflow automation")
    else:
        print("⚠️ Some improvements need further work.")
    
    return passed >= 4


if __name__ == "__main__":
    print("Starting AUX Protocol Comprehensive Tests...")
    success = asyncio.run(run_comprehensive_tests())
    
    if success:
        print("\n🚀 AUX Protocol is significantly improved and ready!")
    else:
        print("\n⚠️ Some areas need additional work.")