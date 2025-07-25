# AUX Protocol - Agent UX Layer

A semantic interface protocol for AI agents to interact with desktop and browser environments efficiently.

## Overview

AUX (Agent UX Layer) provides a structured, machine-native protocol that eliminates the need for screenshot parsing and visual interaction simulation. Instead of mimicking human behavior, agents can directly perceive and manipulate computing environments through semantic commands and observations.

## Key Benefits

- **Efficient**: No token-heavy screenshot processing
- **Reliable**: Deterministic semantic interactions vs. fragile visual recognition  
- **Fast**: Direct API calls instead of simulated user actions
- **Cross-platform**: Standardized interface across different environments
- **MCP Compatible**: Integrates seamlessly with existing AI agent frameworks

## Quick Start

```bash
# Install dependencies
pip install aux-protocol

# Run as MCP server
python -m aux_protocol.server
```

## Protocol Features

### Core Capabilities
- **Semantic Element Inspection** - Rich metadata about UI elements
- **Structured Observations** - JSON-based page state representation
- **Declarative Commands** - Simple, consistent action schema
- **Cross-browser Compatibility** - Works with Chrome, Firefox, Edge

### Advanced Automation Tools
- **🤖 Smart Form Filling** - Intelligent field matching and auto-completion
- **⏳ Dynamic Waiting** - Wait for elements to appear, change, or meet conditions
- **📊 Data Extraction** - Structured data scraping with transformations
- **🔄 Workflow Automation** - Multi-step automation with conditional logic
- **🎯 Element Querying** - Powerful element finding with multiple strategies

### MCP Integration
- **7 Basic Tools** - Navigation, clicking, typing, querying, observation
- **4 Advanced Tools** - Form filling, waiting, extraction, workflows
- **Real-time Resources** - Live browser state and element information
- **Error Handling** - Comprehensive error reporting and recovery

## Documentation

- [Protocol Specification](docs/protocol.md)
- [MCP Integration Guide](docs/mcp-integration.md)
- [Browser Setup](docs/browser-setup.md)
- [Examples](examples/)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.