"""Navigation tools for AUX Protocol."""

from typing import Any, Dict, List
from mcp.types import TextContent

from .base import AUXTool
from ..schema import NavigationCommand


class NavigationTool(AUXTool):
    """Tool for navigating to URLs."""
    
    @property
    def name(self) -> str:
        return "aux_navigate"
    
    @property
    def description(self) -> str:
        return "Navigate to a URL and wait for page load"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
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
    
    async def execute(self, arguments: Dict[str, Any], adapter) -> List[TextContent]:
        """Execute navigation."""
        command = NavigationCommand(**arguments)
        observation = await adapter.navigate(command)
        
        return [TextContent(
            type="text",
            text=f"✅ Navigated to {command.url}\n"
                 f"📄 Title: {observation.browser_state.title}\n"
                 f"🔗 Elements found: {len(observation.browser_state.elements)}\n"
                 f"⏱️ Loading: {observation.browser_state.loading}"
        )]


class BackTool(AUXTool):
    """Tool for navigating back in browser history."""
    
    @property
    def name(self) -> str:
        return "aux_back"
    
    @property
    def description(self) -> str:
        return "Navigate back in browser history"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
        }
    
    async def execute(self, arguments: Dict[str, Any], adapter) -> List[TextContent]:
        """Execute back navigation."""
        if not adapter.driver:
            return [TextContent(type="text", text="❌ Browser not started")]
        
        adapter.driver.back()
        observation = await adapter.observe()
        
        return [TextContent(
            type="text",
            text=f"⬅️ Navigated back to: {observation.browser_state.url}"
        )]


class ForwardTool(AUXTool):
    """Tool for navigating forward in browser history."""
    
    @property
    def name(self) -> str:
        return "aux_forward"
    
    @property
    def description(self) -> str:
        return "Navigate forward in browser history"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
        }
    
    async def execute(self, arguments: Dict[str, Any], adapter) -> List[TextContent]:
        """Execute forward navigation."""
        if not adapter.driver:
            return [TextContent(type="text", text="❌ Browser not started")]
        
        adapter.driver.forward()
        observation = await adapter.observe()
        
        return [TextContent(
            type="text",
            text=f"➡️ Navigated forward to: {observation.browser_state.url}"
        )]


class RefreshTool(AUXTool):
    """Tool for refreshing the current page."""
    
    @property
    def name(self) -> str:
        return "aux_refresh"
    
    @property
    def description(self) -> str:
        return "Refresh the current page"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "wait_for_load": {
                    "type": "boolean",
                    "description": "Wait for page to fully reload",
                    "default": True
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any], adapter) -> List[TextContent]:
        """Execute page refresh."""
        if not adapter.driver:
            return [TextContent(type="text", text="❌ Browser not started")]
        
        adapter.driver.refresh()
        
        if arguments.get("wait_for_load", True):
            from selenium.webdriver.support.ui import WebDriverWait
            WebDriverWait(adapter.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        
        observation = await adapter.observe()
        
        return [TextContent(
            type="text",
            text=f"🔄 Page refreshed: {observation.browser_state.url}\n"
                 f"🔗 Elements: {len(observation.browser_state.elements)}"
        )]