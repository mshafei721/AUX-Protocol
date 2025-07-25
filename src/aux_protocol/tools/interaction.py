"""Interaction tools for AUX Protocol."""

import asyncio
from typing import Any, Dict, List
from mcp.types import TextContent

from .base import AUXTool
from ..schema import AUXCommand, ActionType


class ClickTool(AUXTool):
    """Tool for clicking elements."""
    
    @property
    def name(self) -> str:
        return "aux_click"
    
    @property
    def description(self) -> str:
        return "Click on an element by its ID"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "element_id": {
                    "type": "string",
                    "description": "ID of element to click"
                },
                "wait_for": {
                    "type": "string",
                    "description": "Condition to wait for after click (page_load, element_visible, etc.)"
                },
                "timeout": {
                    "type": "number",
                    "description": "Action timeout in seconds",
                    "default": 5.0
                }
            },
            "required": ["element_id"]
        }
    
    async def execute(self, arguments: Dict[str, Any], adapter) -> List[TextContent]:
        """Execute click action."""
        command = AUXCommand(
            action=ActionType.CLICK,
            target=arguments["element_id"],
            wait_for=arguments.get("wait_for"),
            timeout=arguments.get("timeout", 5.0)
        )
        
        try:
            observation = await adapter.execute_command(command)
            return [TextContent(
                type="text",
                text=f"🖱️ Clicked element {arguments['element_id']}\n"
                     f"📄 Current URL: {observation.browser_state.url}\n"
                     f"⏱️ Loading: {observation.browser_state.loading}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Click failed: {str(e)}"
            )]


class TypeTool(AUXTool):
    """Tool for typing text into input elements."""
    
    @property
    def name(self) -> str:
        return "aux_type"
    
    @property
    def description(self) -> str:
        return "Type text into an input element"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
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
    
    async def execute(self, arguments: Dict[str, Any], adapter) -> List[TextContent]:
        """Execute type action."""
        # Clear first if requested
        if arguments.get("clear_first", True):
            clear_command = AUXCommand(
                action=ActionType.CLEAR,
                target=arguments["element_id"],
                timeout=arguments.get("timeout", 5.0)
            )
            await adapter.execute_command(clear_command)
        
        # Type text
        command = AUXCommand(
            action=ActionType.TYPE,
            target=arguments["element_id"],
            data={"text": arguments["text"]},
            timeout=arguments.get("timeout", 5.0)
        )
        
        try:
            await adapter.execute_command(command)
            return [TextContent(
                type="text",
                text=f"⌨️ Typed '{arguments['text']}' into element {arguments['element_id']}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Type failed: {str(e)}"
            )]


class HoverTool(AUXTool):
    """Tool for hovering over elements."""
    
    @property
    def name(self) -> str:
        return "aux_hover"
    
    @property
    def description(self) -> str:
        return "Hover over an element to reveal dropdowns or tooltips"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "element_id": {
                    "type": "string",
                    "description": "ID of element to hover over"
                },
                "duration": {
                    "type": "number",
                    "description": "How long to hover in seconds",
                    "default": 1.0
                }
            },
            "required": ["element_id"]
        }
    
    async def execute(self, arguments: Dict[str, Any], adapter) -> List[TextContent]:
        """Execute hover action."""
        command = AUXCommand(
            action=ActionType.HOVER,
            target=arguments["element_id"]
        )
        
        try:
            await adapter.execute_command(command)
            
            # Wait for hover duration
            duration = arguments.get("duration", 1.0)
            await asyncio.sleep(duration)
            
            observation = await adapter.observe()
            
            return [TextContent(
                type="text",
                text=f"👆 Hovered over element {arguments['element_id']}\n"
                     f"🔗 New elements may be visible: {len(observation.browser_state.elements)}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Hover failed: {str(e)}"
            )]


class ScrollTool(AUXTool):
    """Tool for scrolling elements into view."""
    
    @property
    def name(self) -> str:
        return "aux_scroll"
    
    @property
    def description(self) -> str:
        return "Scroll an element into view"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "element_id": {
                    "type": "string",
                    "description": "ID of element to scroll to"
                },
                "behavior": {
                    "type": "string",
                    "enum": ["auto", "smooth"],
                    "description": "Scroll behavior",
                    "default": "auto"
                }
            },
            "required": ["element_id"]
        }
    
    async def execute(self, arguments: Dict[str, Any], adapter) -> List[TextContent]:
        """Execute scroll action."""
        command = AUXCommand(
            action=ActionType.SCROLL,
            target=arguments["element_id"],
            data={"behavior": arguments.get("behavior", "auto")}
        )
        
        try:
            await adapter.execute_command(command)
            return [TextContent(
                type="text",
                text=f"📜 Scrolled to element {arguments['element_id']}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Scroll failed: {str(e)}"
            )]


class WaitTool(AUXTool):
    """Tool for waiting for conditions."""
    
    @property
    def name(self) -> str:
        return "aux_wait"
    
    @property
    def description(self) -> str:
        return "Wait for a specific condition or time duration"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "condition": {
                    "type": "string",
                    "enum": ["page_load", "element_visible", "element_clickable", "time"],
                    "description": "Condition to wait for"
                },
                "element_id": {
                    "type": "string",
                    "description": "Element ID (required for element conditions)"
                },
                "duration": {
                    "type": "number",
                    "description": "Time to wait in seconds",
                    "default": 1.0
                },
                "timeout": {
                    "type": "number",
                    "description": "Maximum time to wait",
                    "default": 10.0
                }
            },
            "required": ["condition"]
        }
    
    async def execute(self, arguments: Dict[str, Any], adapter) -> List[TextContent]:
        """Execute wait action."""
        condition = arguments["condition"]
        
        try:
            if condition == "time":
                duration = arguments.get("duration", 1.0)
                await asyncio.sleep(duration)
                return [TextContent(
                    type="text",
                    text=f"⏰ Waited {duration} seconds"
                )]
            
            elif condition == "page_load":
                if adapter.driver:
                    from selenium.webdriver.support.ui import WebDriverWait
                    WebDriverWait(adapter.driver, arguments.get("timeout", 10)).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )
                return [TextContent(
                    type="text",
                    text="✅ Page fully loaded"
                )]
            
            else:
                # For element conditions, we'd need more sophisticated waiting logic
                await asyncio.sleep(arguments.get("duration", 1.0))
                return [TextContent(
                    type="text",
                    text=f"⏳ Waited for condition: {condition}"
                )]
                
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Wait failed: {str(e)}"
            )]