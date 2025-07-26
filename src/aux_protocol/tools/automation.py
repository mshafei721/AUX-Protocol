"""Advanced automation tools for AUX Protocol."""

import asyncio
import json
import re
from typing import Any, Dict, List, Optional, Union
from mcp.types import TextContent

from .base import AUXTool
from ..schema import QueryCommand, AUXCommand, ActionType, ElementType


class FillFormTool(AUXTool):
    """Tool for automatically filling out forms."""
    
    @property
    def name(self) -> str:
        return "aux_fill_form"
    
    @property
    def description(self) -> str:
        return "Automatically fill out a form with provided data"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "form_data": {
                    "type": "object",
                    "description": "Key-value pairs of form field names/labels and their values",
                    "additionalProperties": {"type": "string"}
                },
                "form_selector": {
                    "type": "string",
                    "description": "CSS selector for the form container (optional)",
                    "default": "form"
                },
                "submit": {
                    "type": "boolean",
                    "description": "Whether to submit the form after filling",
                    "default": False
                },
                "clear_first": {
                    "type": "boolean",
                    "description": "Clear existing values before filling",
                    "default": True
                }
            },
            "required": ["form_data"],
            "additionalProperties": false
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute form filling automation."""
        form_data = arguments["form_data"]
        form_selector = arguments.get("form_selector", "form")
        should_submit = arguments.get("submit", False)
        clear_first = arguments.get("clear_first", True)
        
        filled_fields = []
        errors = []
        
        try:
            # Find form container if specified
            if form_selector != "form":
                form_containers = await self.adapter.query_elements(
                    QueryCommand(selector=form_selector, limit=1)
                )
                if not form_containers:
                    return [TextContent(type="text", text=f"Form container '{form_selector}' not found")]
            
            # Process each field in form_data
            for field_key, field_value in form_data.items():
                try:
                    element = await self._find_form_field(field_key, form_selector)
                    if element:
                        # Determine the best action based on element type
                        success = await self._fill_field_intelligently(element, field_value, clear_first)
                        if success:
                            filled_fields.append(f"{field_key}: '{field_value}'")
                    else:
                        errors.append(f"Field '{field_key}' not found")
                        
                except Exception as e:
                    errors.append(f"Error filling '{field_key}': {str(e)}")
            
            # Submit form if requested
            if should_submit and not errors:
                submit_result = await self._submit_form(form_selector)
                if submit_result:
                    filled_fields.append("Form submitted successfully")
                else:
                    errors.append("Failed to submit form")
            
            # Prepare result message
            result = f"Form filling completed:\n"
            result += f"✅ Filled {len(filled_fields)} fields:\n"
            for field in filled_fields:
                result += f"  - {field}\n"
                
            if errors:
                result += f"\n❌ {len(errors)} errors:\n"
                for error in errors:
                    result += f"  - {error}\n"
                    
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Form filling failed: {str(e)}")]
    
    async def _find_form_field(self, field_key: str, form_selector: str) -> Optional[Any]:
        """Find form field by various matching strategies with enhanced element support."""
        
        # Strategy 1: Exact name match (all form elements)
        elements = await self.adapter.query_elements(
            QueryCommand(selector=f"input[name='{field_key}'], select[name='{field_key}'], textarea[name='{field_key}'], button[name='{field_key}']")
        )
        if elements:
            return elements[0]
        
        # Strategy 2: Exact ID match (all form elements)
        elements = await self.adapter.query_elements(
            QueryCommand(selector=f"input[id='{field_key}'], select[id='{field_key}'], textarea[id='{field_key}'], button[id='{field_key}']")
        )
        if elements:
            return elements[0]
        
        # Strategy 3: Data attribute match (common in modern forms)
        elements = await self.adapter.query_elements(
            QueryCommand(selector=f"[data-name='{field_key}'], [data-field='{field_key}'], [data-testid='{field_key}']")
        )
        if elements:
            return elements[0]
        
        # Strategy 4: Label association (for attribute pointing to input id)
        elements = await self.adapter.query_elements(
            QueryCommand(selector=f"label[for]")
        )
        for element in elements:
            if element.text and field_key.lower() in element.text.lower():
                # Found matching label, now find the associated input
                for_attr = element.attributes.get("for")
                if for_attr:
                    associated_elements = await self.adapter.query_elements(
                        QueryCommand(selector=f"#{for_attr}")
                    )
                    if associated_elements:
                        return associated_elements[0]
        
        # Strategy 5: Placeholder match (enhanced)
        elements = await self.adapter.query_elements(
            QueryCommand(selector=f"input[placeholder*='{field_key}'], textarea[placeholder*='{field_key}']")
        )
        if elements:
            return elements[0]
        
        # Strategy 6: ARIA label match
        elements = await self.adapter.query_elements(
            QueryCommand(selector=f"[aria-label*='{field_key}'], [aria-labelledby*='{field_key}']")
        )
        if elements:
            return elements[0]
        
        # Strategy 7: Class name match (common patterns)
        common_patterns = [
            f".{field_key}", f".{field_key}-input", f".{field_key}_field",
            f".field-{field_key}", f".input-{field_key}"
        ]
        for pattern in common_patterns:
            elements = await self.adapter.query_elements(QueryCommand(selector=pattern))
            if elements:
                return elements[0]
        
        # Strategy 8: Fuzzy text matching in nearby labels
        all_form_elements = await self.adapter.query_elements(
            QueryCommand(selector="input, select, textarea, button[type='submit']", limit=100)
        )
        
        for element in all_form_elements:
            # Check aria-label
            if element.aria_label and field_key.lower() in element.aria_label.lower():
                return element
            
            # Check if there's a nearby label
            try:
                # Look for preceding label elements
                preceding_labels = await self.adapter.query_elements(
                    QueryCommand(selector="label")
                )
                for label in preceding_labels:
                    if label.text and field_key.lower() in label.text.lower():
                        # Check if this label is near our element (simplified proximity check)
                        if abs(label.position.get("y", 0) - element.position.get("y", 0)) < 50:
                            return element
            except:
                pass
        
        # Strategy 9: Partial name/id matching (case insensitive)
        partial_selectors = [
            f"input[name*='{field_key.lower()}'], select[name*='{field_key.lower()}'], textarea[name*='{field_key.lower()}']",
            f"input[id*='{field_key.lower()}'], select[id*='{field_key.lower()}'], textarea[id*='{field_key.lower()}']"
        ]
        
        for selector in partial_selectors:
            elements = await self.adapter.query_elements(QueryCommand(selector=selector))
            if elements:
                return elements[0]
        
        # Strategy 10: Common field name variations
        field_variations = [
            field_key.lower(),
            field_key.replace('_', ''),
            field_key.replace('-', ''),
            field_key.replace(' ', ''),
            f"user_{field_key.lower()}",
            f"customer_{field_key.lower()}",
            f"cust_{field_key.lower()}",
        ]
        
        for variation in field_variations:
            elements = await self.adapter.query_elements(
                QueryCommand(selector=f"input[name='{variation}'], input[id='{variation}']")
            )
            if elements:
                return elements[0]
        
        return None
    
    async def _fill_field_intelligently(self, element: Any, field_value: str, clear_first: bool = True) -> bool:
        """Fill form field based on its type with intelligent handling."""
        try:
            # Get element information
            tag = element.tag.lower()
            element_type = element.attributes.get("type", "").lower()
            
            # Handle different element types
            if tag == "input":
                if element_type == "checkbox":
                    # Handle checkbox - interpret value as boolean
                    desired_state = field_value.lower() in ["true", "1", "yes", "on", "checked"]
                    current_state = element.attributes.get("checked") == "true"
                    if current_state != desired_state:
                        await self.adapter.execute_command(AUXCommand(
                            action=ActionType.CLICK,
                            target=element.id,
                            data={"checked": desired_state}
                        ))
                    return True
                    
                elif element_type == "radio":
                    # Handle radio button - click to select
                    await self.adapter.execute_command(AUXCommand(
                        action=ActionType.CLICK,
                        target=element.id
                    ))
                    return True
                    
                elif element_type in ["date", "time", "datetime-local", "month", "week"]:
                    # Handle date/time inputs
                    await self.adapter.execute_command(AUXCommand(
                        action=ActionType.TYPE,
                        target=element.id,
                        data={"text": field_value}
                    ))
                    return True
                    
                elif element_type == "file":
                    # Handle file inputs (would need file path)
                    await self.adapter.execute_command(AUXCommand(
                        action=ActionType.TYPE,
                        target=element.id,
                        data={"text": field_value}
                    ))
                    return True
                    
                elif element_type == "range":
                    # Handle range sliders
                    await self.adapter.execute_command(AUXCommand(
                        action=ActionType.TYPE,
                        target=element.id,
                        data={"text": field_value}
                    ))
                    return True
                    
                elif element_type == "color":
                    # Handle color pickers
                    await self.adapter.execute_command(AUXCommand(
                        action=ActionType.TYPE,
                        target=element.id,
                        data={"text": field_value}
                    ))
                    return True
                    
                else:
                    # Handle regular text inputs
                    if clear_first:
                        await self.adapter.execute_command(AUXCommand(
                            action=ActionType.CLEAR,
                            target=element.id
                        ))
                    
                    await self.adapter.execute_command(AUXCommand(
                        action=ActionType.TYPE,
                        target=element.id,
                        data={"text": field_value}
                    ))
                    return True
                    
            elif tag == "select":
                # Handle dropdown/select elements
                await self.adapter.execute_command(AUXCommand(
                    action=ActionType.SELECT,
                    target=element.id,
                    data={"value": field_value}
                ))
                return True
                
            elif tag == "textarea":
                # Handle text areas
                if clear_first:
                    await self.adapter.execute_command(AUXCommand(
                        action=ActionType.CLEAR,
                        target=element.id
                    ))
                
                await self.adapter.execute_command(AUXCommand(
                    action=ActionType.TYPE,
                    target=element.id,
                    data={"text": field_value}
                ))
                return True
                
            elif tag == "button":
                # Handle buttons (usually for submission)
                await self.adapter.execute_command(AUXCommand(
                    action=ActionType.CLICK,
                    target=element.id
                ))
                return True
                
            else:
                # Fallback for unknown elements - try typing
                await self.adapter.execute_command(AUXCommand(
                    action=ActionType.TYPE,
                    target=element.id,
                    data={"text": field_value}
                ))
                return True
                
        except Exception as e:
            print(f"Error filling field: {e}")
            return False
    
    async def _submit_form(self, form_selector: str) -> bool:
        """Find and click form submit button."""
        # Look for submit buttons
        submit_queries = [
            QueryCommand(selector="input[type='submit']"),
            QueryCommand(selector="button[type='submit']"),
            QueryCommand(text="submit", element_type=ElementType.BUTTON),
            QueryCommand(text="send", element_type=ElementType.BUTTON),
            QueryCommand(text="save", element_type=ElementType.BUTTON),
        ]
        
        for query in submit_queries:
            elements = await self.adapter.query_elements(query)
            if elements:
                await self.adapter.execute_command(AUXCommand(
                    action=ActionType.CLICK,
                    target=elements[0].id
                ))
                return True
        
        return False


class WaitForElementTool(AUXTool):
    """Tool for waiting for elements to appear or change state."""
    
    @property
    def name(self) -> str:
        return "aux_wait_for_element"
    
    @property
    def description(self) -> str:
        return "Wait for an element to appear, disappear, or change state"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector for the element to wait for"
                },
                "text": {
                    "type": "string",
                    "description": "Text content to wait for"
                },
                "element_type": {
                    "type": "string",
                    "enum": [t.value for t in ElementType],
                    "description": "Element type to wait for"
                },
                "condition": {
                    "type": "string",
                    "enum": ["appear", "disappear", "visible", "hidden", "enabled", "disabled", "text_contains"],
                    "description": "Condition to wait for",
                    "default": "appear"
                },
                "timeout": {
                    "type": "number",
                    "description": "Maximum time to wait in seconds",
                    "default": 10.0
                },
                "poll_interval": {
                    "type": "number",
                    "description": "How often to check condition in seconds",
                    "default": 0.5
                }
            },
            "additionalProperties": false
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute element waiting."""
        condition = arguments.get("condition", "appear")
        timeout = arguments.get("timeout", 10.0)
        poll_interval = arguments.get("poll_interval", 0.5)
        
        # Build query
        query_args = {}
        if "selector" in arguments:
            query_args["selector"] = arguments["selector"]
        if "text" in arguments:
            query_args["text"] = arguments["text"]
        if "element_type" in arguments:
            query_args["element_type"] = ElementType(arguments["element_type"])
        
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            try:
                elements = await self.adapter.query_elements(QueryCommand(**query_args))
                
                if condition == "appear" and elements:
                    return [TextContent(type="text", text=f"Element appeared: {elements[0].id}")]
                elif condition == "disappear" and not elements:
                    return [TextContent(type="text", text="Element disappeared")]
                elif condition == "visible" and elements and elements[0].visible:
                    return [TextContent(type="text", text=f"Element became visible: {elements[0].id}")]
                elif condition == "hidden" and elements and not elements[0].visible:
                    return [TextContent(type="text", text=f"Element became hidden: {elements[0].id}")]
                elif condition == "enabled" and elements and elements[0].enabled:
                    return [TextContent(type="text", text=f"Element became enabled: {elements[0].id}")]
                elif condition == "disabled" and elements and not elements[0].enabled:
                    return [TextContent(type="text", text=f"Element became disabled: {elements[0].id}")]
                elif condition == "text_contains" and elements:
                    expected_text = arguments.get("text", "")
                    if expected_text.lower() in (elements[0].text or "").lower():
                        return [TextContent(type="text", text=f"Element contains expected text: {elements[0].id}")]
                
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                await asyncio.sleep(poll_interval)
                continue
        
        return [TextContent(type="text", text=f"Timeout: Condition '{condition}' not met within {timeout} seconds")]


class ExtractDataTool(AUXTool):
    """Tool for extracting structured data from web pages."""
    
    @property
    def name(self) -> str:
        return "aux_extract_data"
    
    @property
    def description(self) -> str:
        return "Extract structured data from page elements"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "extraction_rules": {
                    "type": "object",
                    "description": "Rules for data extraction",
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "selector": {"type": "string"},
                            "attribute": {"type": "string", "default": "text"},
                            "multiple": {"type": "boolean", "default": False},
                            "transform": {"type": "string", "enum": ["trim", "lower", "upper", "number", "url"]}
                        }
                    }
                },
                "output_format": {
                    "type": "string",
                    "enum": ["json", "csv", "text"],
                    "default": "json"
                }
            },
            "required": ["extraction_rules"],
            "additionalProperties": false
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute data extraction."""
        extraction_rules = arguments["extraction_rules"]
        output_format = arguments.get("output_format", "json")
        
        extracted_data = {}
        
        try:
            for field_name, rule in extraction_rules.items():
                selector = rule["selector"]
                attribute = rule.get("attribute", "text")
                multiple = rule.get("multiple", False)
                transform = rule.get("transform")
                
                # Query elements
                elements = await self.adapter.query_elements(
                    QueryCommand(selector=selector, limit=100 if multiple else 1)
                )
                
                if not elements:
                    extracted_data[field_name] = [] if multiple else None
                    continue
                
                # Extract values
                values = []
                for element in elements:
                    if attribute == "text":
                        value = element.text
                    elif attribute == "value":
                        value = element.value
                    elif attribute == "href" and element.tag == "a":
                        value = element.attributes.get("href")
                    elif attribute == "src" and element.tag == "img":
                        value = element.attributes.get("src")
                    else:
                        value = element.attributes.get(attribute)
                    
                    # Apply transformations
                    if value and transform:
                        value = self._transform_value(value, transform)
                    
                    values.append(value)
                    
                    if not multiple:
                        break
                
                extracted_data[field_name] = values if multiple else (values[0] if values else None)
            
            # Format output
            if output_format == "json":
                result = json.dumps(extracted_data, indent=2)
            elif output_format == "csv":
                result = self._format_as_csv(extracted_data)
            else:
                result = self._format_as_text(extracted_data)
            
            return [TextContent(type="text", text=f"Extracted data:\n{result}")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Data extraction failed: {str(e)}")]
    
    def _transform_value(self, value: str, transform: str) -> str:
        """Apply transformation to extracted value."""
        if transform == "trim":
            return value.strip()
        elif transform == "lower":
            return value.lower()
        elif transform == "upper":
            return value.upper()
        elif transform == "number":
            # Extract numbers from string
            numbers = re.findall(r'-?\d+\.?\d*', value)
            return numbers[0] if numbers else "0"
        elif transform == "url":
            # Extract URLs from string
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', value)
            return urls[0] if urls else value
        return value
    
    def _format_as_csv(self, data: Dict[str, Any]) -> str:
        """Format extracted data as CSV."""
        if not data:
            return ""
        
        # Simple CSV formatting
        headers = list(data.keys())
        csv_lines = [",".join(headers)]
        
        # Handle mixed single/multiple values
        max_rows = 1
        for value in data.values():
            if isinstance(value, list):
                max_rows = max(max_rows, len(value))
        
        for i in range(max_rows):
            row = []
            for key in headers:
                value = data[key]
                if isinstance(value, list):
                    cell = value[i] if i < len(value) else ""
                else:
                    cell = value if i == 0 else ""
                row.append(f'"{cell}"' if cell else '""')
            csv_lines.append(",".join(row))
        
        return "\n".join(csv_lines)
    
    def _format_as_text(self, data: Dict[str, Any]) -> str:
        """Format extracted data as readable text."""
        lines = []
        for key, value in data.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)


class WorkflowTool(AUXTool):
    """Tool for executing multi-step automation workflows."""
    
    @property
    def name(self) -> str:
        return "aux_workflow"
    
    @property
    def description(self) -> str:
        return "Execute a multi-step automation workflow"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "description": "Array of workflow steps to execute",
                    "items": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["navigate", "click", "type", "wait", "extract", "fill_form"],
                                "description": "Action to perform"
                            },
                            "params": {
                                "type": "object",
                                "description": "Parameters for the action"
                            },
                            "condition": {
                                "type": "object",
                                "description": "Optional condition to check before executing step"
                            }
                        },
                        "required": ["action", "params"],
                        "additionalProperties": false
                    }
                },
                "continue_on_error": {
                    "type": "boolean",
                    "description": "Whether to continue workflow if a step fails",
                    "default": False
                }
            },
            "required": ["steps"],
            "additionalProperties": false
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute workflow steps."""
        steps = arguments["steps"]
        continue_on_error = arguments.get("continue_on_error", False)
        
        results = []
        errors = []
        
        for i, step in enumerate(steps):
            try:
                action = step["action"]
                params = step["params"]
                condition = step.get("condition")
                
                # Check condition if specified
                if condition and not await self._check_condition(condition):
                    results.append(f"Step {i+1}: Skipped (condition not met)")
                    continue
                
                # Execute step
                if action == "navigate":
                    from ..schema import NavigationCommand
                    nav_command = NavigationCommand(**params)
                    await self.adapter.navigate(nav_command)
                    results.append(f"Step {i+1}: Navigated to {params['url']}")
                    
                elif action == "click":
                    command = AUXCommand(
                        action=ActionType.CLICK,
                        target=params["element_id"],
                        timeout=params.get("timeout", 5.0)
                    )
                    await self.adapter.execute_command(command)
                    results.append(f"Step {i+1}: Clicked {params['element_id']}")
                    
                elif action == "type":
                    command = AUXCommand(
                        action=ActionType.TYPE,
                        target=params["element_id"],
                        data={"text": params["text"]},
                        timeout=params.get("timeout", 5.0)
                    )
                    await self.adapter.execute_command(command)
                    results.append(f"Step {i+1}: Typed into {params['element_id']}")
                    
                elif action == "wait":
                    wait_time = params.get("seconds", 1.0)
                    await asyncio.sleep(wait_time)
                    results.append(f"Step {i+1}: Waited {wait_time} seconds")
                    
                elif action == "extract":
                    # Use ExtractDataTool
                    extract_tool = ExtractDataTool(self.adapter)
                    extract_result = await extract_tool.execute(params)
                    results.append(f"Step {i+1}: Data extracted")
                    
                elif action == "fill_form":
                    # Use FillFormTool
                    form_tool = FillFormTool(self.adapter)
                    form_result = await form_tool.execute(params)
                    results.append(f"Step {i+1}: Form filled")
                    
                else:
                    errors.append(f"Step {i+1}: Unknown action '{action}'")
                    if not continue_on_error:
                        break
                        
            except Exception as e:
                error_msg = f"Step {i+1}: Error - {str(e)}"
                errors.append(error_msg)
                if not continue_on_error:
                    break
        
        # Prepare result
        result = f"Workflow execution completed:\n"
        result += f"✅ {len(results)} steps executed:\n"
        for result_msg in results:
            result += f"  - {result_msg}\n"
            
        if errors:
            result += f"\n❌ {len(errors)} errors:\n"
            for error in errors:
                result += f"  - {error}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _check_condition(self, condition: Dict[str, Any]) -> bool:
        """Check if a condition is met."""
        condition_type = condition.get("type")
        
        if condition_type == "element_exists":
            elements = await self.adapter.query_elements(
                QueryCommand(selector=condition["selector"], limit=1)
            )
            return len(elements) > 0
            
        elif condition_type == "element_visible":
            elements = await self.adapter.query_elements(
                QueryCommand(selector=condition["selector"], limit=1)
            )
            return len(elements) > 0 and elements[0].visible
            
        elif condition_type == "url_contains":
            observation = await self.adapter.observe()
            return condition["text"] in observation.browser_state.url
            
        elif condition_type == "title_contains":
            observation = await self.adapter.observe()
            return condition["text"] in observation.browser_state.title
        
        return True  # Default to true if condition type unknown
       