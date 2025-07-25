# Advanced Automation Features

AUX Protocol provides powerful automation tools that go beyond basic click and type operations. These tools enable complex workflows, intelligent form filling, data extraction, and dynamic waiting.

## Overview of Advanced Tools

### 🤖 Form Automation (`aux_fill_form`)
Intelligently fills out web forms using multiple field matching strategies.

### ⏳ Dynamic Waiting (`aux_wait_for_element`)
Waits for elements to appear, disappear, or change state with customizable conditions.

### 📊 Data Extraction (`aux_extract_data`)
Extracts structured data from web pages with transformation and formatting options.

### 🔄 Workflow Automation (`aux_workflow`)
Executes multi-step automation workflows with conditional logic and error handling.

## Form Automation

### Features
- **Smart Field Matching**: Finds form fields by name, ID, label text, placeholder, or ARIA attributes
- **Multiple Input Types**: Supports text inputs, textareas, selects, checkboxes, and radio buttons
- **Auto-Submit**: Optionally submits forms after filling
- **Error Handling**: Reports which fields were filled successfully and which failed

### Usage Example

```python
# MCP tool call
await mcp_client.call_tool("aux_fill_form", {
    "form_data": {
        "email": "user@example.com",
        "password": "secure123",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1-555-0123",
        "message": "Hello from AUX Protocol!"
    },
    "form_selector": "form#contact-form",  # Optional: target specific form
    "submit": True,                        # Auto-submit after filling
    "clear_first": True                    # Clear existing values
})
```

### Field Matching Strategies

1. **Exact name match**: `input[name='email']`
2. **Exact ID match**: `input[id='email']`
3. **Label text match**: Labels containing "email"
4. **Placeholder match**: `input[placeholder*='email']`
5. **ARIA label match**: `input[aria-label*='email']`
6. **Fuzzy text matching**: Nearby text content

## Dynamic Waiting

### Supported Conditions
- `appear` - Element becomes present in DOM
- `disappear` - Element is removed from DOM
- `visible` - Element becomes visible
- `hidden` - Element becomes hidden
- `enabled` - Element becomes interactive
- `disabled` - Element becomes non-interactive
- `text_contains` - Element contains specific text

### Usage Example

```python
# Wait for loading spinner to disappear
await mcp_client.call_tool("aux_wait_for_element", {
    "selector": ".loading-spinner",
    "condition": "disappear",
    "timeout": 30.0,
    "poll_interval": 0.5
})

# Wait for submit button to become enabled
await mcp_client.call_tool("aux_wait_for_element", {
    "element_type": "button",
    "text": "submit",
    "condition": "enabled",
    "timeout": 10.0
})
```

## Data Extraction

### Features
- **Multiple Selectors**: CSS selectors, element types, text matching
- **Attribute Extraction**: Text, values, href, src, or any HTML attribute
- **Data Transformation**: Trim, case conversion, number extraction, URL extraction
- **Output Formats**: JSON, CSV, or formatted text
- **Batch Processing**: Extract multiple data points in one operation

### Extraction Rules Schema

```python
extraction_rules = {
    "field_name": {
        "selector": "CSS selector",           # Required
        "attribute": "text|value|href|src",   # Default: "text"
        "multiple": True|False,               # Default: False
        "transform": "trim|lower|upper|number|url"  # Optional
    }
}
```

### Usage Examples

#### Product Catalog Extraction
```python
await mcp_client.call_tool("aux_extract_data", {
    "extraction_rules": {
        "product_names": {
            "selector": ".product-title",
            "attribute": "text",
            "multiple": True,
            "transform": "trim"
        },
        "prices": {
            "selector": ".price",
            "attribute": "text",
            "multiple": True,
            "transform": "number"
        },
        "product_links": {
            "selector": ".product-link",
            "attribute": "href",
            "multiple": True
        },
        "availability": {
            "selector": ".stock-status",
            "attribute": "text",
            "multiple": True,
            "transform": "lower"
        }
    },
    "output_format": "json"
})
```

#### News Article Extraction
```python
await mcp_client.call_tool("aux_extract_data", {
    "extraction_rules": {
        "headline": {
            "selector": "h1.article-title",
            "attribute": "text"
        },
        "author": {
            "selector": ".author-name",
            "attribute": "text"
        },
        "publish_date": {
            "selector": ".publish-date",
            "attribute": "datetime"
        },
        "article_text": {
            "selector": ".article-content p",
            "attribute": "text",
            "multiple": True
        },
        "tags": {
            "selector": ".tag",
            "attribute": "text",
            "multiple": True
        }
    },
    "output_format": "json"
})
```

## Workflow Automation

### Supported Actions
- `navigate` - Navigate to URLs
- `click` - Click elements
- `type` - Type text into inputs
- `wait` - Wait for specified time
- `extract` - Extract data using extraction rules
- `fill_form` - Fill forms using form automation

### Conditional Execution
Workflows support conditional steps that only execute when conditions are met:

```python
{
    "action": "click",
    "params": {"element_id": "submit-btn"},
    "condition": {
        "type": "element_visible",
        "selector": "#submit-btn:not(:disabled)"
    }
}
```

### Error Handling
- `continue_on_error: true` - Continue workflow even if steps fail
- `continue_on_error: false` - Stop workflow on first error

### Complex Workflow Example

```python
await mcp_client.call_tool("aux_workflow", {
    "steps": [
        {
            "action": "navigate",
            "params": {
                "url": "https://example-shop.com",
                "wait_for_load": True
            }
        },
        {
            "action": "type",
            "params": {
                "element_id": "search-input",
                "text": "wireless headphones"
            }
        },
        {
            "action": "click",
            "params": {"element_id": "search-button"}
        },
        {
            "action": "wait",
            "params": {"seconds": 2}
        },
        {
            "action": "extract",
            "params": {
                "extraction_rules": {
                    "product_names": {
                        "selector": ".product-name",
                        "multiple": True
                    },
                    "prices": {
                        "selector": ".price",
                        "multiple": True,
                        "transform": "number"
                    }
                },
                "output_format": "json"
            }
        },
        {
            "action": "click",
            "params": {"element_id": "first-product"},
            "condition": {
                "type": "element_exists",
                "selector": ".product-item:first-child"
            }
        },
        {
            "action": "fill_form",
            "params": {
                "form_data": {
                    "quantity": "2",
                    "color": "black"
                },
                "submit": False
            }
        }
    ],
    "continue_on_error": False
})
```

## Real-World Use Cases

### E-commerce Automation
- Product catalog scraping
- Price monitoring
- Inventory checking
- Automated purchasing workflows
- Review and rating extraction

### Social Media Management
- Content posting automation
- Engagement tracking
- Profile information extraction
- Automated responses
- Analytics data collection

### Form Processing
- Lead generation form filling
- Survey completion
- Registration automation
- Data entry tasks
- Multi-step form workflows

### Content Management
- Blog post publishing
- Content migration
- SEO data extraction
- Link checking
- Content auditing

### Testing and QA
- Automated user journey testing
- Form validation testing
- Cross-browser compatibility
- Performance monitoring
- Regression testing

## Best Practices

### Performance Optimization
1. **Use specific selectors** - Avoid overly broad CSS selectors
2. **Limit extraction scope** - Use `limit` parameter in queries
3. **Batch operations** - Combine multiple extractions in one call
4. **Optimize wait times** - Use appropriate timeouts and poll intervals

### Reliability
1. **Handle dynamic content** - Use wait conditions for AJAX-loaded content
2. **Implement fallbacks** - Use multiple field matching strategies
3. **Error handling** - Always check for element existence before interaction
4. **Retry logic** - Implement retry mechanisms for flaky operations

### Security
1. **Validate inputs** - Sanitize form data and URLs
2. **Rate limiting** - Avoid overwhelming target websites
3. **Respect robots.txt** - Follow website automation policies
4. **Use headless mode** - For production automation

### Maintainability
1. **Modular workflows** - Break complex workflows into smaller steps
2. **Parameterize workflows** - Use variables for reusable workflows
3. **Document selectors** - Comment complex CSS selectors
4. **Version control** - Track changes to automation scripts