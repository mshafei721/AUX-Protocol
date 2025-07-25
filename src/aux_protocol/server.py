"""AUX Protocol MCP Server implementation."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from .browser_adapter import BrowserAdapter
from .schema import (
    AUXCommand,
    NavigationCommand, 
    QueryCommand,
    ActionType,
    ElementType
)
from .tools import (
    FillFormTool,
    WaitForElementTool,
    ExtractDataTool,
    WorkflowTool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global browser adapter instance
browser_adapter: Optional[BrowserAdapter] = None

# MCP Server instance
server = Server("aux-protocol")

# Initialize advanced automation tools (will be created when browser starts)
advanced_tools: Dict[str, Any] = {}

def _create_advanced_tools() -> Dict[str, Any]:
    """Create advanced automation tools when browser is available."""
    if not browser_adapter:
        return {}
    
    return {
        "aux_fill_form": FillFormTool(browser_adapter),
        "aux_wait_for_element": WaitForElementTool(browser_adapter),
        "aux_extract_data": ExtractDataTool(browser_adapter),
        "aux_workflow": WorkflowTool(browser_adapter),
    }


@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available AUX resources."""
    return [
        Resource(
            uri="aux://browser/state",
            name="Browser State",
            description="Current browser state and elements",
            mimeType="application/json",
        ),
        Resource(
            uri="aux://browser/elements",
            name="Page Elements", 
            description="All semantic elements on current page",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read AUX resource content."""
    global browser_adapter
    
    if not browser_adapter:
        return json.dumps({"error": "Browser not initialized"})
        
    if uri == "aux://browser/state":
        observation = await browser_adapter.observe()
        return observation.model_dump_json(indent=2)
    elif uri == "aux://browser/elements":
        observation = await browser_adapter.observe()
        elements_data = [elem.model_dump() for elem in observation.browser_state.elements]
        return json.dumps(elements_data, indent=2)
    else:
        return json.dumps({"error": f"Unknown resource: {uri}"})


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available AUX tools."""
    tools = [
        # Basic browser management
        Tool(
            name="aux_start_browser",
            description="Start browser session",
            inputSchema={
                "type": "object",
                "properties": {
                    "headless": {
                        "type": "boolean",
                        "description": "Run browser in headless mode",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="aux_stop_browser", 
            description="Stop browser session",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        # Basic navigation and interaction
        Tool(
            name="aux_navigate",
            description="Navigate to a URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to navigate to"
                    },
                    "wait_for_load": {
                        "type": "boolean", 
                        "description": "Wait for page to fully load",
                        "default": True
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Navigation timeout in seconds",
                        "default": 10.0
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="aux_click",
            description="Click on an element",
            inputSchema={
                "type": "object",
                "properties": {
                    "element_id": {
                        "type": "string",
                        "description": "ID of element to click"
                    },
                    "wait_for": {
                        "type": "string",
                        "description": "Condition to wait for after click"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Action timeout in seconds",
                        "default": 5.0
                    }
                },
                "required": ["element_id"]
            }
        ),
        Tool(
            name="aux_type",
            description="Type text into an input element",
            inputSchema={
                "type": "object",
                "properties": {
                    "element_id": {
                        "type": "string",
                        "description": "ID of input element"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text to type"
                    },
                    "clear_first": {
                        "type": "boolean",
                        "description": "Clear field before typing",
                        "default": True
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Action timeout in seconds", 
                        "default": 5.0
                    }
                },
                "required": ["element_id", "text"]
            }
        ),
        Tool(
            name="aux_query",
            description="Query elements on the page",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector to match elements"
                    },
                    "text": {
                        "type": "string", 
                        "description": "Text content to search for"
                    },
                    "element_type": {
                        "type": "string",
                        "enum": [t.value for t in ElementType],
                        "description": "Element type filter"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="aux_observe",
            description="Get current browser state and all elements",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]
    
    # Add advanced automation tools if browser is started
    if browser_adapter:
        global advanced_tools
        advanced_tools = _create_advanced_tools()
        
        for tool_name, tool_instance in advanced_tools.items():
            tools.append(Tool(
                name=tool_name,
                description=tool_instance.description,
                inputSchema=tool_instance.input_schema
            ))
    
    return tools


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle AUX tool calls."""
    global browser_adapter, advanced_tools
    
    try:
        # Handle browser management tools
        if name == "aux_start_browser":
            headless = arguments.get("headless", False)
            browser_adapter = BrowserAdapter(headless=headless)
            await browser_adapter.start()
            # Initialize advanced tools now that browser is available
            advanced_tools = _create_advanced_tools()
            return [TextContent(type="text", text="🚀 Browser started successfully")]
            
        elif name == "aux_stop_browser":
            if browser_adapter:
                await browser_adapter.stop()
                browser_adapter = None
                advanced_tools = {}
            return [TextContent(type="text", text="🛑 Browser stopped")]
        
        # All other tools require browser to be started
        if not browser_adapter:
            return [TextContent(type="text", text="❌ Error: Browser not started. Use aux_start_browser first.")]
        
        # Handle advanced automation tools
        if name in advanced_tools:
            tool = advanced_tools[name]
            return await tool.execute(arguments)
        
        # Handle basic tools
        elif name == "aux_navigate":
            command = NavigationCommand(**arguments)
            observation = await browser_adapter.navigate(command)
            return [TextContent(
                type="text", 
                text=f"🌐 Navigated to {command.url}. Found {len(observation.browser_state.elements)} interactive elements."
            )]
            
        elif name == "aux_click":
            command = AUXCommand(
                action=ActionType.CLICK,
                target=arguments["element_id"],
                wait_for=arguments.get("wait_for"),
                timeout=arguments.get("timeout", 5.0)
            )
            observation = await browser_adapter.execute_command(command)
            return [TextContent(
                type="text",
                text=f"👆 Clicked element {arguments['element_id']}. Page state updated."
            )]
            
        elif name == "aux_type":
            command = AUXCommand(
                action=ActionType.TYPE,
                target=arguments["element_id"],
                data={"text": arguments["text"]},
                timeout=arguments.get("timeout", 5.0)
            )
            observation = await browser_adapter.execute_command(command)
            return [TextContent(
                type="text",
                text=f"⌨️ Typed '{arguments['text']}' into element {arguments['element_id']}"
            )]
            
        elif name == "aux_query":
            query = QueryCommand(**arguments)
            elements = await browser_adapter.query_elements(query)
            
            result = f"🔍 Found {len(elements)} matching elements:\n"
            for elem in elements:
                result += f"  • {elem.id}: {elem.type.value} '{elem.text or elem.aria_label or elem.tag}'\n"
                
            return [TextContent(type="text", text=result)]
            
        elif name == "aux_observe":
            observation = await browser_adapter.observe()
            
            result = f"👁️ Browser State:\n"
            result += f"  URL: {observation.browser_state.url}\n"
            result += f"  Title: {observation.browser_state.title}\n"
            result += f"  Elements: {len(observation.browser_state.elements)}\n"
            result += f"  Loading: {observation.browser_state.loading}\n\n"
            
            result += "🎯 Interactive Elements:\n"
            for elem in observation.browser_state.elements[:10]:  # Show first 10
                result += f"  • {elem.id}: {elem.type.value} '{elem.text or elem.aria_label or elem.tag}'\n"
                
            if len(observation.browser_state.elements) > 10:
                result += f"  ... and {len(observation.browser_state.elements) - 10} more elements\n"
                
            return [TextContent(type="text", text=result)]
            
        else:
            return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


async def main():
    """Run the AUX Protocol MCP server."""
    logger.info("Starting AUX Protocol MCP Server...")
    
    async with stdio_server() as (read_stream, write_stream):
        from mcp.server.lowlevel.server import NotificationOptions
        
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="aux-protocol",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())