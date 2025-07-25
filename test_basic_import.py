"""Basic import test for AUX Protocol."""

def test_imports():
    """Test that all modules can be imported."""
    try:
        print("Testing basic imports...")
        
        # Test schema imports
        from aux_protocol.schema import (
            ElementInfo, 
            BrowserState, 
            AUXCommand, 
            NavigationCommand,
            QueryCommand,
            ActionType,
            ElementType
        )
        print("✅ Schema imports successful")
        
        # Test browser adapter import
        from aux_protocol.browser_adapter import BrowserAdapter
        print("✅ Browser adapter import successful")
        
        # Test tools imports
        from aux_protocol.tools import (
            FillFormTool,
            WaitForElementTool,
            ExtractDataTool,
            WorkflowTool,
        )
        print("✅ Tools imports successful")
        
        # Test server import
        from aux_protocol.server import server
        print("✅ Server import successful")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_browser_adapter():
    """Test browser adapter creation."""
    try:
        print("\nTesting browser adapter creation...")
        from aux_protocol.browser_adapter import BrowserAdapter
        
        adapter = BrowserAdapter(headless=True)
        print("✅ Browser adapter created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Browser adapter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tools_creation():
    """Test tools creation."""
    try:
        print("\nTesting tools creation...")
        from aux_protocol.browser_adapter import BrowserAdapter
        from aux_protocol.tools import (
            FillFormTool,
            WaitForElementTool,
            ExtractDataTool,
            WorkflowTool,
        )
        
        # Create a mock adapter
        adapter = BrowserAdapter(headless=True)
        
        # Create tools
        fill_tool = FillFormTool(adapter)
        wait_tool = WaitForElementTool(adapter)
        extract_tool = ExtractDataTool(adapter)
        workflow_tool = WorkflowTool(adapter)
        
        print("✅ All tools created successfully")
        print(f"  - {fill_tool.name}: {fill_tool.description}")
        print(f"  - {wait_tool.name}: {wait_tool.description}")
        print(f"  - {extract_tool.name}: {extract_tool.description}")
        print(f"  - {workflow_tool.name}: {workflow_tool.description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tools creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 AUX Protocol Basic Tests")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Browser Adapter Test", test_browser_adapter),
        ("Tools Creation Test", test_tools_creation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        success = test_func()
        results.append((test_name, success))
        
        if success:
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    # Summary
    print(f"\n📊 Test Results:")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed!")
    else:
        print("⚠️ Some tests failed.")