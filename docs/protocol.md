# AUX Protocol Specification

## Overview

The AUX (Agent UX Layer) protocol provides a semantic interface for AI agents to interact with browser environments efficiently. Instead of relying on screenshots or visual parsing, AUX exposes structured, machine-readable representations of web pages and provides deterministic commands for interaction.

## Core Concepts

### Semantic Elements

AUX represents web page elements semantically rather than visually:

```json
{
  "id": "aux_123",
  "type": "button",
  "tag": "button", 
  "text": "Submit Form",
  "aria_label": "Submit the contact form",
  "visible": true,
  "enabled": true,
  "position": {"x": 100, "y": 200},
  "size": {"width": 120, "height": 40}
}
```

### Element Types

- `button` - Clickable buttons and button-like elements
- `input` - Text inputs, checkboxes, radio buttons
- `link` - Hyperlinks and navigation elements  
- `text` - Static text content
- `image` - Images and visual content
- `form` - Form containers
- `container` - Layout containers (div, section, etc.)
- `navigation` - Navigation menus and breadcrumbs
- `menu` - Dropdown menus and option lists
- `dialog` - Modal dialogs and popups
- `table` - Data tables
- `list` - Lists and list items

### Commands

AUX commands are structured actions that agents can perform:

```json
{
  "action": "click",
  "target": "aux_123", 
  "data": {},
  "wait_for": "page_load",
  "timeout": 5.0
}
```

### Observations

After each command, AUX returns a structured observation:

```json
{
  "browser_state": {
    "url": "https://example.com",
    "title": "Example Page",
    "elements": [...],
    "focused_element": "aux_456",
    "loading": false
  },
  "timestamp": 1642123456.789,
  "changes": ["aux_123", "aux_456"],
  "events": []
}
```

## Action Types

### Navigation
- Navigate to URLs
- Handle page loads and redirects
- Manage browser history

### Element Interaction  
- `click` - Click buttons, links, checkboxes
- `type` - Enter text into input fields
- `clear` - Clear input field contents
- `hover` - Hover over elements
- `scroll` - Scroll elements into view
- `select` - Select dropdown options
- `submit` - Submit forms
- `focus`/`blur` - Manage element focus

### Querying
- Find elements by CSS selector
- Search by text content
- Filter by element type
- Match by attributes

## Benefits Over Traditional Automation

### Token Efficiency
- No screenshot processing required
- Structured JSON instead of visual parsing
- Minimal data transfer

### Reliability  
- Deterministic element identification
- No visual recognition failures
- Consistent cross-platform behavior

### Speed
- Direct API calls vs. simulated user actions
- No waiting for visual rendering
- Parallel command execution

### Semantic Understanding
- Rich element metadata
- Accessibility information included
- Context-aware interactions

## Integration Patterns

### MCP Server
AUX runs as an MCP (Model Context Protocol) server, making it compatible with any MCP-enabled AI agent framework.

### Browser Adapters
- Selenium WebDriver for cross-browser support
- Chrome DevTools Protocol for advanced features
- Browser extensions for native integration

### Event System
- Real-time state change notifications
- Element lifecycle events
- User interaction tracking

## Security Considerations

- Sandboxed browser execution
- Permission-based access control
- Audit logging of all actions
- Rate limiting and timeout protection