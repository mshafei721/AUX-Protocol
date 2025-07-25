"""Basic AUX Protocol automation example."""

import asyncio
import json
from aux_protocol.browser_adapter import BrowserAdapter
from aux_protocol.schema import NavigationCommand, QueryCommand, AUXCommand, ActionType


async def basic_example():
    """Demonstrate basic AUX Protocol usage."""
    
    # Initialize browser
    adapter = BrowserAdapter(headless=False)
    await adapter.start()
    
    try:
        # Navigate to a test page
        print("Navigating to example.com...")
        nav_command = NavigationCommand(url="https://example.com")
        observation = await adapter.navigate(nav_command)
        
        print(f"Page loaded: {observation.browser_state.title}")
        print(f"Found {len(observation.browser_state.elements)} interactive elements")
        
        # Query for links
        print("\nSearching for links...")
        query = QueryCommand(element_type="link", limit=5)
        links = await adapter.query_elements(query)
        
        for link in links:
            print(f"- {link.id}: {link.text or link.aria_label}")
            
        # Get full page observation
        print("\nFull page observation:")
        observation = await adapter.observe()
        
        print(f"URL: {observation.browser_state.url}")
        print(f"Title: {observation.browser_state.title}")
        print(f"Loading: {observation.browser_state.loading}")
        
        # Show first few elements
        print("\nFirst 5 elements:")
        for elem in observation.browser_state.elements[:5]:
            print(f"- {elem.id}: {elem.type.value} '{elem.text or elem.tag}'")
            
    finally:
        await adapter.stop()


async def form_example():
    """Demonstrate form interaction."""
    
    adapter = BrowserAdapter(headless=False)
    await adapter.start()
    
    try:
        # Navigate to a form page (using httpbin for testing)
        print("Navigating to form test page...")
        nav_command = NavigationCommand(url="https://httpbin.org/forms/post")
        await adapter.navigate(nav_command)
        
        # Find form inputs
        print("Finding form inputs...")
        inputs = await adapter.query_elements(QueryCommand(element_type="input"))
        
        for inp in inputs:
            print(f"Input: {inp.id} - {inp.attributes.get('name', 'unnamed')}")
            
        # Fill out form (if inputs found)
        if len(inputs) >= 2:
            # Fill first input
            print("Filling first input...")
            command = AUXCommand(
                action=ActionType.TYPE,
                target=inputs[0].id,
                data={"text": "AUX Protocol Test"}
            )
            await adapter.execute_command(command)
            
            # Fill second input  
            print("Filling second input...")
            command = AUXCommand(
                action=ActionType.TYPE,
                target=inputs[1].id,
                data={"text": "test@example.com"}
            )
            await adapter.execute_command(command)
            
        # Find and click submit button
        buttons = await adapter.query_elements(QueryCommand(element_type="button"))
        submit_buttons = [b for b in buttons if "submit" in (b.text or "").lower()]
        
        if submit_buttons:
            print("Clicking submit button...")
            command = AUXCommand(
                action=ActionType.CLICK,
                target=submit_buttons[0].id
            )
            await adapter.execute_command(command)
            
            # Wait a moment and observe result
            await asyncio.sleep(2)
            final_observation = await adapter.observe()
            print(f"Final URL: {final_observation.browser_state.url}")
            
    finally:
        await adapter.stop()


if __name__ == "__main__":
    print("AUX Protocol Basic Example")
    print("=" * 40)
    
    # Run basic example
    asyncio.run(basic_example())
    
    print("\n" + "=" * 40)
    print("Form Interaction Example")
    print("=" * 40)
    
    # Run form example
    asyncio.run(form_example())