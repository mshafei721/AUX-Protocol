"""Advanced AUX Protocol automation examples showcasing powerful features."""

import asyncio
import json
from aux_protocol.browser_adapter import BrowserAdapter
from aux_protocol.tools import (
    FillFormTool,
    WaitForElementTool,
    ExtractDataTool,
    WorkflowTool,
)


async def form_automation_example():
    """Demonstrate intelligent form filling."""
    print("🤖 Advanced Form Automation Example")
    print("=" * 50)
    
    adapter = BrowserAdapter(headless=False)
    await adapter.start()
    
    try:
        # Navigate to a contact form
        from aux_protocol.schema import NavigationCommand
        await adapter.navigate(NavigationCommand(url="https://httpbin.org/forms/post"))
        
        # Initialize form filling tool
        form_tool = FillFormTool(adapter)
        
        # Fill form with intelligent field matching
        form_data = {
            "custname": "John Doe",
            "custtel": "+1-555-0123", 
            "custemail": "john.doe@example.com",
            "size": "large",
            "comments": "This is an automated test using AUX Protocol!"
        }
        
        result = await form_tool.execute({
            "form_data": form_data,
            "submit": True,
            "clear_first": True
        })
        
        print("Form filling result:")
        print(result[0].text)
        
    finally:
        await adapter.stop()


async def data_extraction_example():
    """Demonstrate structured data extraction."""
    print("\n📊 Data Extraction Example")
    print("=" * 50)
    
    adapter = BrowserAdapter(headless=False)
    await adapter.start()
    
    try:
        # Navigate to a page with structured data
        from aux_protocol.schema import NavigationCommand
        await adapter.navigate(NavigationCommand(url="https://quotes.toscrape.com/"))
        
        # Initialize extraction tool
        extract_tool = ExtractDataTool(adapter)
        
        # Define extraction rules for quotes
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
            },
            "tags": {
                "selector": ".quote .tags a",
                "attribute": "text",
                "multiple": True
            },
            "page_title": {
                "selector": "title",
                "attribute": "text"
            }
        }
        
        # Extract data in different formats
        for output_format in ["json", "csv", "text"]:
            print(f"\n--- {output_format.upper()} Format ---")
            result = await extract_tool.execute({
                "extraction_rules": extraction_rules,
                "output_format": output_format
            })
            print(result[0].text[:500] + "..." if len(result[0].text) > 500 else result[0].text)
        
    finally:
        await adapter.stop()


async def wait_and_interact_example():
    """Demonstrate dynamic waiting and interaction."""
    print("\n⏳ Dynamic Waiting Example")
    print("=" * 50)
    
    adapter = BrowserAdapter(headless=False)
    await adapter.start()
    
    try:
        # Navigate to a dynamic page
        from aux_protocol.schema import NavigationCommand
        await adapter.navigate(NavigationCommand(url="https://httpbin.org/delay/2"))
        
        # Initialize wait tool
        wait_tool = WaitForElementTool(adapter)
        
        # Wait for page to load completely
        result = await wait_tool.execute({
            "selector": "body",
            "condition": "appear",
            "timeout": 10.0
        })
        print("Wait result:", result[0].text)
        
        # Navigate to a form and wait for specific elements
        await adapter.navigate(NavigationCommand(url="https://httpbin.org/forms/post"))
        
        # Wait for form inputs to be ready
        result = await wait_tool.execute({
            "element_type": "input",
            "condition": "enabled",
            "timeout": 5.0
        })
        print("Form ready:", result[0].text)
        
    finally:
        await adapter.stop()


async def workflow_automation_example():
    """Demonstrate complex multi-step workflows."""
    print("\n🔄 Workflow Automation Example")
    print("=" * 50)
    
    adapter = BrowserAdapter(headless=False)
    await adapter.start()
    
    try:
        # Initialize workflow tool
        workflow_tool = WorkflowTool(adapter)
        
        # Define a complex workflow
        workflow_steps = [
            {
                "action": "navigate",
                "params": {
                    "url": "https://httpbin.org/forms/post",
                    "wait_for_load": True
                }
            },
            {
                "action": "wait",
                "params": {"seconds": 1}
            },
            {
                "action": "fill_form",
                "params": {
                    "form_data": {
                        "custname": "Workflow Test User",
                        "custemail": "workflow@example.com",
                        "comments": "Automated via AUX Protocol workflow!"
                    },
                    "clear_first": True
                }
            },
            {
                "action": "extract",
                "params": {
                    "extraction_rules": {
                        "form_fields": {
                            "selector": "input, textarea, select",
                            "attribute": "name",
                            "multiple": True
                        }
                    },
                    "output_format": "json"
                }
            }
        ]
        
        # Execute workflow
        result = await workflow_tool.execute({
            "steps": workflow_steps,
            "continue_on_error": False
        })
        
        print("Workflow execution result:")
        print(result[0].text)
        
    finally:
        await adapter.stop()


async def e_commerce_automation_example():
    """Demonstrate e-commerce automation workflow."""
    print("\n🛒 E-commerce Automation Example")
    print("=" * 50)
    
    adapter = BrowserAdapter(headless=False)
    await adapter.start()
    
    try:
        workflow_tool = WorkflowTool(adapter)
        
        # E-commerce workflow: search, select, add to cart
        ecommerce_workflow = [
            {
                "action": "navigate",
                "params": {
                    "url": "https://books.toscrape.com/",
                    "wait_for_load": True
                }
            },
            {
                "action": "extract",
                "params": {
                    "extraction_rules": {
                        "book_titles": {
                            "selector": "article.product_pod h3 a",
                            "attribute": "title",
                            "multiple": True
                        },
                        "book_prices": {
                            "selector": "article.product_pod .price_color",
                            "attribute": "text",
                            "multiple": True
                        },
                        "book_availability": {
                            "selector": "article.product_pod .instock.availability",
                            "attribute": "text",
                            "multiple": True,
                            "transform": "trim"
                        }
                    },
                    "output_format": "json"
                }
            }
        ]
        
        result = await workflow_tool.execute({
            "steps": ecommerce_workflow,
            "continue_on_error": True
        })
        
        print("E-commerce data extraction result:")
        print(result[0].text)
        
    finally:
        await adapter.stop()


async def social_media_automation_example():
    """Demonstrate social media automation patterns."""
    print("\n📱 Social Media Automation Example")
    print("=" * 50)
    
    adapter = BrowserAdapter(headless=False)
    await adapter.start()
    
    try:
        # Navigate to a social media-like interface
        from aux_protocol.schema import NavigationCommand
        await adapter.navigate(NavigationCommand(url="https://httpbin.org/html"))
        
        extract_tool = ExtractDataTool(adapter)
        
        # Extract page structure (simulating social media content)
        extraction_rules = {
            "headings": {
                "selector": "h1, h2, h3, h4, h5, h6",
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
                "multiple": True,
                "transform": "trim"
            }
        }
        
        result = await extract_tool.execute({
            "extraction_rules": extraction_rules,
            "output_format": "text"
        })
        
        print("Social media content extraction:")
        print(result[0].text)
        
    finally:
        await adapter.stop()


async def main():
    """Run all advanced automation examples."""
    print("🚀 AUX Protocol Advanced Automation Examples")
    print("=" * 60)
    
    examples = [
        ("Form Automation", form_automation_example),
        ("Data Extraction", data_extraction_example),
        ("Dynamic Waiting", wait_and_interact_example),
        ("Workflow Automation", workflow_automation_example),
        ("E-commerce Automation", e_commerce_automation_example),
        ("Social Media Automation", social_media_automation_example),
    ]
    
    for name, example_func in examples:
        try:
            print(f"\n🎯 Running {name} Example...")
            await example_func()
            print(f"✅ {name} completed successfully!")
        except Exception as e:
            print(f"❌ {name} failed: {e}")
        
        print("\n" + "-" * 60)
    
    print("\n🎉 All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())