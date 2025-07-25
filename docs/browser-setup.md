# Browser Setup Guide

## Prerequisites

AUX Protocol requires a compatible browser and WebDriver setup for automation.

## Chrome/Chromium Setup

### Install Chrome
- **Windows**: Download from https://www.google.com/chrome/
- **macOS**: `brew install --cask google-chrome`
- **Linux**: `sudo apt-get install google-chrome-stable`

### Install ChromeDriver

ChromeDriver is automatically managed by Selenium 4.15+, but you can install manually:

```bash
# Using webdriver-manager (recommended)
pip install webdriver-manager

# Or download manually from:
# https://chromedriver.chromium.org/
```

## Firefox Setup (Optional)

```bash
# Install Firefox
# Windows: Download from https://www.mozilla.org/firefox/
# macOS: brew install --cask firefox
# Linux: sudo apt-get install firefox

# Install GeckoDriver
pip install webdriver-manager
```

## Environment Configuration

### Chrome Options
Set environment variables to customize browser behavior:

```bash
export AUX_BROWSER_HEADLESS=true
export AUX_BROWSER_WINDOW_SIZE=1920x1080
export AUX_BROWSER_USER_AGENT="AUX-Agent/1.0"
```

### WebDriver Configuration
```python
# Custom browser options in your code
from aux_protocol.browser_adapter import BrowserAdapter

adapter = BrowserAdapter(
    headless=True,
    window_size=(1920, 1080),
    user_agent="AUX-Agent/1.0"
)
```

## Docker Setup

For containerized environments:

```dockerfile
FROM python:3.11-slim

# Install Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy AUX Protocol
COPY . /app
WORKDIR /app

# Run in headless mode
ENV AUX_BROWSER_HEADLESS=true

CMD ["python", "-m", "aux_protocol.server"]
```

## Troubleshooting

### Common Issues

**ChromeDriver not found**
```bash
# Install webdriver-manager
pip install webdriver-manager

# Or set path manually
export PATH=$PATH:/path/to/chromedriver
```

**Permission denied**
```bash
# Make ChromeDriver executable
chmod +x /path/to/chromedriver
```

**Display issues in headless mode**
```bash
# Install virtual display for Linux
sudo apt-get install xvfb

# Run with virtual display
xvfb-run -a python -m aux_protocol.server
```

### Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Fully supported |
| Chromium | 90+ | ✅ Fully supported |
| Firefox | 88+ | 🟡 Basic support |
| Safari | 14+ | 🔴 Not supported |
| Edge | 90+ | 🟡 Basic support |

### Performance Tuning

```python
# Optimize for speed
options = {
    "headless": True,
    "disable_images": True,
    "disable_javascript": False,  # Keep for dynamic content
    "page_load_strategy": "eager",  # Don't wait for all resources
    "implicit_wait": 1,  # Reduce wait times
}
```

### Security Considerations

- Run browser in sandboxed mode
- Disable unnecessary features
- Use separate browser profile
- Limit network access if possible

```python
# Security-focused options
security_options = [
    "--no-sandbox",
    "--disable-dev-shm-usage", 
    "--disable-extensions",
    "--disable-plugins",
    "--disable-images",
    "--disable-javascript",  # If not needed
    "--incognito"
]
```