"""Observation tools for AUX Protocol."""

import json
from typing import Any, Dict, List
from mcp.types import TextContent

from .base import AUXTool


class ObservationTool(AUXTool):
    """Tool for observing current browser state."""
    
    @property
    def name(self) -> str:
        return "aux_observe"
    
    @property
    def description(self) -> str:
        return "Get current browser state and all interactive elements"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "include_details": {
                    "type": "boolean",
                    "description": "Include detailed element information",
                    "default": False
                },
                "element_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by specific element types"
                },
                "max_elements": {
                    "type": "integer",
                    "description": "Maximum elements to show in summary",
                    "default": 15,
                    "minimum": 1,
                    "maximum": 100
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any], adapter) -> List[TextContent]:
        """Execute observation."""
        try:
            observation = await adapter.observe()
            browser_state = observation.browser_state
            
            include_details = arguments.get("include_details", False)
            element_types = arguments.get("element_types", [])
            max_elements = arguments.get("max_elements", 15)
            
            # Filter elements by type if specified
            elements = browser_state.elements
            if element_types:
                elements = [e for e in elements if e.type.value in element_types]
            
            # Build response
            result = f"🌐 **Browser State**\n"
            result += f"📄 **URL:** {browser_state.url}\n"
            result += f"📋 **Title:** {browser_state.title}\n"
            result += f"⏱️ **Loading:** {browser_state.loading}\n"
            result += f"🔗 **Total Elements:** {len(browser_state.elements)}\n"
            
            if element_types:
                result += f"🎯 **Filtered Elements:** {len(elements)} (types: {', '.join(element_types)})\n"
            
            if browser_state.focused_element:
                result += f"🎯 **Focused Element:** {browser_state.focused_element}\n"
            
            if browser_state.alerts:
                result += f"⚠️ **Alerts:** {', '.join(browser_state.alerts)}\n"
            
            result += f"\n📋 **Interactive Elements** (showing first {min(max_elements, len(elements))}):\n\n"
            
            # Group elements by type for better organization
            elements_by_type = {}
            for elem in elements[:max_elements]:
                elem_type = elem.type.value
                if elem_type not in elements_by_type:
                    elements_by_type[elem_type] = []
                elements_by_type[elem_type].append(elem)
            
            for elem_type, type_elements in elements_by_type.items():
                result += f"**{elem_type.upper()}S ({len(type_elements)}):**\n"
                
                for elem in type_elements:
                    # Create element description
                    desc_parts = []
                    if elem.text and elem.text.strip():
                        desc_parts.append(f"'{elem.text.strip()[:40]}'")
                    if elem.aria_label:
                        desc_parts.append(f"[{elem.aria_label[:30]}]")
                    if elem.placeholder:
                        desc_parts.append(f"placeholder: {elem.placeholder[:25]}")
                    
                    description = " ".join(desc_parts) if desc_parts else elem.tag
                    
                    result += f"  • **{elem.id}**: {description}\n"
                    
                    if include_details:
                        result += f"    - Position: ({elem.position.get('x', 0):.0f}, {elem.position.get('y', 0):.0f})\n"
                        result += f"    - Size: {elem.size.get('width', 0):.0f}x{elem.size.get('height', 0):.0f}\n"
                        result += f"    - Visible: {elem.visible}, Enabled: {elem.enabled}\n"
                        if elem.attributes.get("class"):
                            result += f"    - Class: {elem.attributes['class'][:40]}\n"
                
                result += "\n"
            
            if len(elements) > max_elements:
                result += f"... and {len(elements) - max_elements} more elements\n"
            
            # Add summary statistics
            result += f"\n📊 **Element Summary:**\n"
            type_counts = {}
            for elem in browser_state.elements:
                elem_type = elem.type.value
                type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
            
            for elem_type, count in sorted(type_counts.items()):
                result += f"  • {elem_type}: {count}\n"
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Observation failed: {str(e)}"
            )]


class PageInfoTool(AUXTool):
    """Tool for getting basic page information."""
    
    @property
    def name(self) -> str:
        return "aux_page_info"
    
    @property
    def description(self) -> str:
        return "Get basic information about the current page"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
        }
    
    async def execute(self, arguments: Dict[str, Any], adapter) -> List[TextContent]:
        """Execute page info retrieval."""
        if not adapter.driver:
            return [TextContent(type="text", text="❌ Browser not started")]
        
        try:
            # Get basic page info
            url = adapter.driver.current_url
            title = adapter.driver.title
            
            # Get page dimensions
            window_size = adapter.driver.get_window_size()
            page_height = adapter.driver.execute_script("return document.body.scrollHeight")
            
            # Get loading state
            ready_state = adapter.driver.execute_script("return document.readyState")
            
            # Get meta information
            try:
                description = adapter.driver.execute_script(
                    "return document.querySelector('meta[name=\"description\"]')?.content || 'No description'"
                )
                keywords = adapter.driver.execute_script(
                    "return document.querySelector('meta[name=\"keywords\"]')?.content || 'No keywords'"
                )
            except:
                description = "No description"
                keywords = "No keywords"
            
            result = f"📄 **Page Information**\n\n"
            result += f"🌐 **URL:** {url}\n"
            result += f"📋 **Title:** {title}\n"
            result += f"📝 **Description:** {description[:100]}{'...' if len(description) > 100 else ''}\n"
            result += f"🏷️ **Keywords:** {keywords[:100]}{'...' if len(keywords) > 100 else ''}\n"
            result += f"⏱️ **Ready State:** {ready_state}\n"
            result += f"📐 **Window Size:** {window_size['width']}x{window_size['height']}\n"
            result += f"📏 **Page Height:** {page_height}px\n"
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Page info retrieval failed: {str(e)}"
            )]


class ScreenshotTool(AUXTool):
    """Tool for taking page screenshots (fallback for visual debugging)."""
    
    @property
    def name(self) -> str:
        return "aux_screenshot"
    
    @property
    def description(self) -> str:
        return "Take a screenshot of the current page (for debugging only)"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "element_id": {
                    "type": "string",
                    "description": "Take screenshot of specific element only"
                },
                "full_page": {
                    "type": "boolean",
                    "description": "Capture full page height",
                    "default": False
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any], adapter) -> List[TextContent]:
        """Execute screenshot capture."""
        if not adapter.driver:
            return [TextContent(type="text", text="❌ Browser not started")]
        
        try:
            element_id = arguments.get("element_id")
            full_page = arguments.get("full_page", False)
            
            if element_id:
                # Screenshot specific element
                element = adapter._get_element_by_id(element_id)
                screenshot_data = element.screenshot_as_base64
                return [TextContent(
                    type="text",
                    text=f"📸 Screenshot captured for element {element_id}\n"
                         f"📊 Data size: {len(screenshot_data)} characters (base64)"
                )]
            else:
                # Full page or viewport screenshot
                if full_page:
                    # Set window size to capture full page
                    original_size = adapter.driver.get_window_size()
                    page_height = adapter.driver.execute_script("return document.body.scrollHeight")
                    adapter.driver.set_window_size(original_size['width'], page_height)
                
                screenshot_data = adapter.driver.get_screenshot_as_base64()
                
                if full_page:
                    # Restore original window size
                    adapter.driver.set_window_size(original_size['width'], original_size['height'])
                
                return [TextContent(
                    type="text",
                    text=f"📸 {'Full page' if full_page else 'Viewport'} screenshot captured\n"
                         f"📊 Data size: {len(screenshot_data)} characters (base64)\n"
                         f"💡 Note: AUX Protocol is designed to avoid screenshots - use semantic tools instead!"
                )]
                
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Screenshot failed: {str(e)}"
            )]