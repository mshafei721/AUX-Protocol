# MCP Integration Guide

## Overview

AUX Protocol integrates seamlessly with the Model Context Protocol (MCP) ecosystem, allowing any MCP-compatible AI agent to perform browser automation tasks.

## Installation

```bash
pip install aux-protocol
```

## MCP Server Configuration

Add AUX to your MCP configuration:

```json
{
  "mcpServers": {
    "aux-protocol": {
      "command": "python",
      "args": ["-m", "aux_protocol.server"],
      "env": {
        "AUX_LOG_LEVEL": "INFO"
      },
      "disabled": false,
      "autoApprove": [
        "aux_observe",
        "aux_query"
      ]
    }
  }
}
```

## Available Tools

### Browser Management
- `aux_start_browser` - Initialize browser session
- `aux_stop_browser` - Close browser session

### Navigation
- `aux_navigate` - Navigate to URLs

### Element Interaction
- `aux_click` - Click elements
- `aux_type` - Type text into inputs
- `aux_observe` - Get current page state
- `aux_query` - Find elements

## Usage Examples

### Basic Navigation and Interaction

```python
# Start browser
await mcp_client.call_tool("aux_start_browser", {"headless": False})

# Navigate to a page
await mcp_client.call_tool("aux_navigate", {
    "url": "https://example.com/login"
})

# Find login form elements
result = await mcp_client.call_tool("aux_query", {
    "element_type": "input"
})

# Type credentials
await mcp_client.call_tool("aux_type", {
    "element_id": "aux_0",  # username field
    "text": "user@example.com"
})

await mcp_client.call_tool("aux_type", {
    "element_id": "aux_1",  # password field  
    "text": "password123"
})

# Click login button
await mcp_client.call_tool("aux_click", {
    "element_id": "aux_2"  # login button
})
```

### Form Automation

```python
# Navigate to contact form
await mcp_client.call_tool("aux_navigate", {
    "url": "https://example.com/contact"
})

# Get current page state
state = await mcp_client.call_tool("aux_observe", {})

# Fill out form fields
form_data = {
    "name": "John Doe",
    "email": "john@example.com", 
    "message": "Hello from AUX Protocol!"
}

# Find form inputs
inputs = await mcp_client.call_tool("aux_query", {
    "element_type": "input"
})

# Type into each field (simplified)
for field_name, value in form_data.items():
    # Find field by name attribute
    field_elements = await mcp_client.call_tool("aux_query", {
        "selector": f"input[name='{field_name}']"
    })
    
    if field_elements:
        await mcp_client.call_tool("aux_type", {
            "element_id": field_elements[0]["id"],
            "text": value
        })

# Submit form
submit_btn = await mcp_client.call_tool("aux_query", {
    "element_type": "button",
    "text": "submit"
})

await mcp_client.call_tool("aux_click", {
    "element_id": submit_btn[0]["id"]
})
```

### E-commerce Automation

```python
# Search for products
await mcp_client.call_tool("aux_navigate", {
    "url": "https://shop.example.com"
})

# Find search box
search_box = await mcp_client.call_tool("aux_query", {
    "selector": "input[type='search']"
})

# Search for product
await mcp_client.call_tool("aux_type", {
    "element_id": search_box[0]["id"],
    "text": "wireless headphones"
})

# Click search button
search_btn = await mcp_client.call_tool("aux_query", {
    "element_type": "button",
    "text": "search"
})

await mcp_client.call_tool("aux_click", {
    "element_id": search_btn[0]["id"]
})

# Wait for results and select first product
products = await mcp_client.call_tool("aux_query", {
    "selector": ".product-item a"
})

await mcp_client.call_tool("aux_click", {
    "element_id": products[0]["id"]
})

# Add to cart
add_to_cart = await mcp_client.call_tool("aux_query", {
    "text": "add to cart"
})

await mcp_client.call_tool("aux_click", {
    "element_id": add_to_cart[0]["id"]
})
```

## Resources

AUX provides MCP resources for real-time browser state:

- `aux://browser/state` - Complete browser state
- `aux://browser/elements` - All page elements

```python
# Get browser state as resource
state = await mcp_client.read_resource("aux://browser/state")
browser_data = json.loads(state)

# Get all elements
elements = await mcp_client.read_resource("aux://browser/elements") 
elements_data = json.loads(elements)
```

## Error Handling

```python
try:
    result = await mcp_client.call_tool("aux_click", {
        "element_id": "nonexistent_element"
    })
except Exception as e:
    print(f"Action failed: {e}")
    
    # Get current state to debug
    state = await mcp_client.call_tool("aux_observe", {})
    print("Available elements:", state["elements"])
```

## Best Practices

1. **Always start browser first** - Call `aux_start_browser` before other operations
2. **Use semantic queries** - Prefer element type and text matching over CSS selectors
3. **Handle timeouts** - Set appropriate timeout values for slow-loading pages
4. **Observe after actions** - Check page state after interactions
5. **Clean up** - Call `aux_stop_browser` when done

## Configuration Options

### Environment Variables
- `AUX_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `AUX_BROWSER_TIMEOUT` - Default browser timeout in seconds
- `AUX_HEADLESS` - Run browser in headless mode by default

### MCP Server Options
- `autoApprove` - Tools that don't require user confirmation
- `disabled` - Disable the AUX server
- `env` - Environment variables for the server process