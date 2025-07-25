"""Query tools for AUX Protocol."""

from typing import Any, Dict, List
from mcp.types import TextContent

from .base import AUXTool
from ..schema import QueryCommand, ElementType


class QueryTool(AUXTool):
    """Tool for querying elements on the page."""
    
    @property
    def name(self) -> str:
        return "aux_query"
    
    @property
    def description(self) -> str:
        return "Find elements on the page using various criteria"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector to match elements"
                },
                "text": {
                    "type": "string",
                    "description": "Text content to search for (partial match)"
                },
                "element_type": {
                    "type": "string",
                    "enum": [t.value for t in ElementType],
                    "description": "Element type filter"
                },
                "attributes": {
                    "type": "object",
                    "description": "HTML attributes to match",
                    "additionalProperties": {"type": "string"}
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 50
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any], adapter) -> List[TextContent]:
        """Execute element query."""
        query = QueryCommand(**arguments)
        
        try:
            elements = await adapter.query_elements(query)
            
            if not elements:
                return [TextContent(
                    type="text",
                    text="🔍 No elements found matching the criteria"
                )]
            
            result = f"🔍 Found {len(elements)} matching elements:\n\n"
            
            for i, elem in enumerate(elements, 1):
                # Create a descriptive label for the element
                label_parts = []
                if elem.text and elem.text.strip():
                    label_parts.append(f"'{elem.text.strip()[:50]}'")
                if elem.aria_label:
                    label_parts.append(f"[{elem.aria_label[:30]}]")
                if elem.placeholder:
                    label_parts.append(f"placeholder: {elem.placeholder[:30]}")
                
                label = " ".join(label_parts) if label_parts else elem.tag
                
                result += f"{i}. **{elem.id}** ({elem.type.value})\n"
                result += f"   📝 {label}\n"
                
                if elem.attributes.get("class"):
                    result += f"   🏷️ class: {elem.attributes['class'][:50]}\n"
                if elem.attributes.get("id"):
                    result += f"   🆔 id: {elem.attributes['id']}\n"
                
                result += f"   👁️ visible: {elem.visible}, enabled: {elem.enabled}\n\n"
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Query failed: {str(e)}"
            )]


class FindByTextTool(AUXTool):
    """Tool for finding elements by exact text match."""
    
    @property
    def name(self) -> str:
        return "aux_find_by_text"
    
    @property
    def description(self) -> str:
        return "Find elements containing specific text (exact match)"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Exact text to search for"
                },
                "element_type": {
                    "type": "string",
                    "enum": [t.value for t in ElementType],
                    "description": "Limit search to specific element type"
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "Case sensitive search",
                    "default": False
                }
            },
            "required": ["text"]
        }
    
    async def execute(self, arguments: Dict[str, Any], adapter) -> List[TextContent]:
        """Execute text-based search."""
        search_text = arguments["text"]
        element_type = arguments.get("element_type")
        case_sensitive = arguments.get("case_sensitive", False)
        
        # Build query
        query_args = {"text": search_text, "limit": 20}
        if element_type:
            query_args["element_type"] = element_type
            
        query = QueryCommand(**query_args)
        
        try:
            elements = await adapter.query_elements(query)
            
            # Filter for exact matches
            exact_matches = []
            for elem in elements:
                elem_text = elem.text or ""
                if case_sensitive:
                    if search_text in elem_text:
                        exact_matches.append(elem)
                else:
                    if search_text.lower() in elem_text.lower():
                        exact_matches.append(elem)
            
            if not exact_matches:
                return [TextContent(
                    type="text",
                    text=f"🔍 No elements found containing text: '{search_text}'"
                )]
            
            result = f"🔍 Found {len(exact_matches)} elements containing '{search_text}':\n\n"
            
            for i, elem in enumerate(exact_matches, 1):
                result += f"{i}. **{elem.id}** ({elem.type.value})\n"
                result += f"   📝 Text: '{elem.text}'\n"
                if elem.aria_label:
                    result += f"   🏷️ Label: {elem.aria_label}\n"
                result += f"   👁️ Visible: {elem.visible}\n\n"
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Text search failed: {str(e)}"
            )]


class FindButtonsTool(AUXTool):
    """Tool for finding all buttons on the page."""
    
    @property
    def name(self) -> str:
        return "aux_find_buttons"
    
    @property
    def description(self) -> str:
        return "Find all clickable buttons on the current page"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "enabled_only": {
                    "type": "boolean",
                    "description": "Only return enabled buttons",
                    "default": True
                },
                "visible_only": {
                    "type": "boolean",
                    "description": "Only return visible buttons",
                    "default": True
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any], adapter) -> List[TextContent]:
        """Execute button search."""
        query = QueryCommand(element_type=ElementType.BUTTON, limit=30)
        
        try:
            buttons = await adapter.query_elements(query)
            
            # Apply filters
            enabled_only = arguments.get("enabled_only", True)
            visible_only = arguments.get("visible_only", True)
            
            filtered_buttons = []
            for button in buttons:
                if enabled_only and not button.enabled:
                    continue
                if visible_only and not button.visible:
                    continue
                filtered_buttons.append(button)
            
            if not filtered_buttons:
                return [TextContent(
                    type="text",
                    text="🔍 No buttons found matching the criteria"
                )]
            
            result = f"🔘 Found {len(filtered_buttons)} buttons:\n\n"
            
            for i, button in enumerate(filtered_buttons, 1):
                text = button.text or button.aria_label or "No text"
                result += f"{i}. **{button.id}**\n"
                result += f"   📝 {text}\n"
                result += f"   ✅ Enabled: {button.enabled}, Visible: {button.visible}\n\n"
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Button search failed: {str(e)}"
            )]


class FindLinksTool(AUXTool):
    """Tool for finding all links on the page."""
    
    @property
    def name(self) -> str:
        return "aux_find_links"
    
    @property
    def description(self) -> str:
        return "Find all clickable links on the current page"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "internal_only": {
                    "type": "boolean",
                    "description": "Only return internal links (same domain)",
                    "default": False
                },
                "with_text_only": {
                    "type": "boolean",
                    "description": "Only return links with visible text",
                    "default": True
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any], adapter) -> List[TextContent]:
        """Execute link search."""
        query = QueryCommand(element_type=ElementType.LINK, limit=30)
        
        try:
            links = await adapter.query_elements(query)
            
            # Apply filters
            with_text_only = arguments.get("with_text_only", True)
            internal_only = arguments.get("internal_only", False)
            
            if internal_only and adapter.driver:
                current_domain = adapter.driver.current_url.split('/')[2] if '://' in adapter.driver.current_url else ""
            
            filtered_links = []
            for link in links:
                if with_text_only and not (link.text and link.text.strip()):
                    continue
                    
                if internal_only:
                    href = link.attributes.get("href", "")
                    if href.startswith("http") and current_domain not in href:
                        continue
                        
                filtered_links.append(link)
            
            if not filtered_links:
                return [TextContent(
                    type="text",
                    text="🔍 No links found matching the criteria"
                )]
            
            result = f"🔗 Found {len(filtered_links)} links:\n\n"
            
            for i, link in enumerate(filtered_links, 1):
                text = link.text or "No text"
                href = link.attributes.get("href", "No URL")
                result += f"{i}. **{link.id}**\n"
                result += f"   📝 {text}\n"
                result += f"   🌐 {href[:60]}{'...' if len(href) > 60 else ''}\n\n"
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Link search failed: {str(e)}"
            )]