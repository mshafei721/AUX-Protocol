# Contributing to AUX Protocol

We welcome contributions to the AUX Protocol! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/aux-protocol.git`
3. Install dependencies: `pip install -e .`
4. Run tests: `python test_direct_functionality.py`

## Development Setup

### Prerequisites
- Python 3.8+
- Chrome browser
- ChromeDriver (automatically managed by Selenium 4.15+)

### Installation
```bash
# Clone the repository
git clone https://github.com/aux-protocol/aux-protocol.git
cd aux-protocol

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e .[dev]
```

### Running Tests
```bash
# Run basic functionality tests
python test_direct_functionality.py

# Run comprehensive tests
python comprehensive_performance_test.py

# Run MCP server tests
python test_mcp_simple.py
```

## Contributing Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Add docstrings to all public functions and classes
- Keep functions focused and modular

### Testing
- Add tests for new features
- Ensure all existing tests pass
- Test both headless and non-headless browser modes
- Include performance benchmarks for significant changes

### Documentation
- Update README.md for new features
- Add examples for new tools
- Update API documentation
- Include usage examples in docstrings

### Pull Request Process

1. **Create a feature branch**: `git checkout -b feature/your-feature-name`
2. **Make your changes**: Implement your feature or fix
3. **Add tests**: Ensure your changes are tested
4. **Update documentation**: Update relevant docs
5. **Run tests**: Make sure all tests pass
6. **Commit changes**: Use clear, descriptive commit messages
7. **Push to your fork**: `git push origin feature/your-feature-name`
8. **Create pull request**: Submit a PR with a clear description

### Commit Message Format
```
type(scope): brief description

Longer description if needed

- List any breaking changes
- Reference issues: Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Areas for Contribution

### High Priority
- Enhanced form element support (checkboxes, radio buttons, dropdowns)
- Performance optimizations
- Cross-browser compatibility
- Error handling improvements

### Medium Priority
- Additional automation tools
- Better element matching strategies
- Mobile browser support
- Accessibility features

### Low Priority
- UI improvements
- Additional output formats
- Integration examples
- Performance monitoring

## Code Architecture

### Core Components
- `browser_adapter.py`: Selenium WebDriver integration
- `schema.py`: Pydantic models for protocol
- `server.py`: MCP server implementation
- `tools/`: Advanced automation tools

### Adding New Tools
1. Create tool class inheriting from `AUXTool`
2. Implement required methods: `name`, `description`, `input_schema`, `execute`
3. Add to `tools/__init__.py`
4. Register in `server.py`
5. Add tests and documentation

### Performance Guidelines
- Use performance mode optimizations
- Cache elements when possible
- Minimize DOM queries
- Use efficient selectors
- Implement timeouts appropriately

## Reporting Issues

### Bug Reports
Include:
- Python version
- Browser version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Feature Requests
Include:
- Use case description
- Proposed solution
- Alternative approaches
- Implementation complexity estimate

## Community

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Use GitHub Issues for bugs and features
- **Security**: Email security issues privately

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to AUX Protocol!