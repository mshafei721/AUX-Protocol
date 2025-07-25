"""Configuration management for AUX Protocol."""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BrowserConfig:
    """Browser configuration settings."""
    headless: bool = False
    window_width: int = 1920
    window_height: int = 1080
    user_agent: Optional[str] = None
    disable_images: bool = False
    disable_javascript: bool = False
    page_load_strategy: str = "normal"  # normal, eager, none
    implicit_wait: float = 1.0
    explicit_wait: float = 10.0
    
    # Chrome-specific options
    chrome_options: list = field(default_factory=lambda: [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled"
    ])


@dataclass
class AUXConfig:
    """Main AUX Protocol configuration."""
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    log_level: str = "INFO"
    max_elements_per_query: int = 50
    element_cache_size: int = 1000
    observation_timeout: float = 30.0
    command_timeout: float = 10.0
    
    # MCP server settings
    server_name: str = "aux-protocol"
    server_version: str = "0.1.0"
    
    # Security settings
    allowed_domains: list = field(default_factory=list)  # Empty = all allowed
    blocked_domains: list = field(default_factory=lambda: [
        "malware.com",
        "phishing.example"
    ])
    
    # Performance settings
    enable_element_caching: bool = True
    enable_change_detection: bool = True
    screenshot_quality: int = 80  # JPEG quality 1-100


def load_config() -> AUXConfig:
    """Load configuration from environment variables and files."""
    config = AUXConfig()
    
    # Browser settings from environment
    config.browser.headless = os.getenv("AUX_BROWSER_HEADLESS", "false").lower() == "true"
    config.browser.window_width = int(os.getenv("AUX_BROWSER_WIDTH", "1920"))
    config.browser.window_height = int(os.getenv("AUX_BROWSER_HEIGHT", "1080"))
    config.browser.user_agent = os.getenv("AUX_BROWSER_USER_AGENT")
    config.browser.disable_images = os.getenv("AUX_DISABLE_IMAGES", "false").lower() == "true"
    config.browser.disable_javascript = os.getenv("AUX_DISABLE_JS", "false").lower() == "true"
    config.browser.page_load_strategy = os.getenv("AUX_PAGE_LOAD_STRATEGY", "normal")
    
    # Timeout settings
    config.browser.implicit_wait = float(os.getenv("AUX_IMPLICIT_WAIT", "1.0"))
    config.browser.explicit_wait = float(os.getenv("AUX_EXPLICIT_WAIT", "10.0"))
    config.observation_timeout = float(os.getenv("AUX_OBSERVATION_TIMEOUT", "30.0"))
    config.command_timeout = float(os.getenv("AUX_COMMAND_TIMEOUT", "10.0"))
    
    # General settings
    config.log_level = os.getenv("AUX_LOG_LEVEL", "INFO").upper()
    config.max_elements_per_query = int(os.getenv("AUX_MAX_ELEMENTS", "50"))
    
    # Security settings
    allowed_domains = os.getenv("AUX_ALLOWED_DOMAINS")
    if allowed_domains:
        config.allowed_domains = [d.strip() for d in allowed_domains.split(",")]
    
    blocked_domains = os.getenv("AUX_BLOCKED_DOMAINS")
    if blocked_domains:
        config.blocked_domains.extend([d.strip() for d in blocked_domains.split(",")])
    
    # Performance settings
    config.enable_element_caching = os.getenv("AUX_ENABLE_CACHING", "true").lower() == "true"
    config.enable_change_detection = os.getenv("AUX_ENABLE_CHANGE_DETECTION", "true").lower() == "true"
    
    return config


def get_chrome_options(config: BrowserConfig) -> list:
    """Get Chrome options based on configuration."""
    options = config.chrome_options.copy()
    
    if config.headless:
        options.append("--headless")
    
    if config.disable_images:
        options.extend([
            "--blink-settings=imagesEnabled=false",
            "--disable-images"
        ])
    
    if config.disable_javascript:
        options.append("--disable-javascript")
    
    if config.user_agent:
        options.append(f"--user-agent={config.user_agent}")
    
    options.append(f"--window-size={config.window_width},{config.window_height}")
    
    return options


# Global configuration instance
_config: Optional[AUXConfig] = None


def get_config() -> AUXConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config() -> AUXConfig:
    """Reload configuration from environment."""
    global _config
    _config = load_config()
    return _config