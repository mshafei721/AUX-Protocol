"""Custom exceptions for AUX Protocol."""

from typing import Optional, Dict, Any


class AUXException(Exception):
    """Base exception for AUX Protocol."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class BrowserNotStartedException(AUXException):
    """Raised when browser operations are attempted without starting browser."""
    
    def __init__(self):
        super().__init__(
            "Browser not started. Use aux_start_browser first.",
            error_code="BROWSER_NOT_STARTED"
        )


class ElementNotFoundException(AUXException):
    """Raised when an element cannot be found."""
    
    def __init__(self, element_id: str, selector: Optional[str] = None):
        message = f"Element not found: {element_id}"
        if selector:
            message += f" (selector: {selector})"
        
        super().__init__(
            message,
            error_code="ELEMENT_NOT_FOUND",
            details={"element_id": element_id, "selector": selector}
        )


class ElementNotInteractableException(AUXException):
    """Raised when an element exists but cannot be interacted with."""
    
    def __init__(self, element_id: str, reason: str = "Element not visible or enabled"):
        super().__init__(
            f"Element not interactable: {element_id}. {reason}",
            error_code="ELEMENT_NOT_INTERACTABLE",
            details={"element_id": element_id, "reason": reason}
        )


class NavigationException(AUXException):
    """Raised when navigation fails."""
    
    def __init__(self, url: str, reason: str):
        super().__init__(
            f"Navigation failed to {url}: {reason}",
            error_code="NAVIGATION_FAILED",
            details={"url": url, "reason": reason}
        )


class TimeoutException(AUXException):
    """Raised when operations timeout."""
    
    def __init__(self, operation: str, timeout: float):
        super().__init__(
            f"Operation timed out: {operation} (timeout: {timeout}s)",
            error_code="OPERATION_TIMEOUT",
            details={"operation": operation, "timeout": timeout}
        )


class SecurityException(AUXException):
    """Raised when security policies are violated."""
    
    def __init__(self, message: str, domain: Optional[str] = None):
        super().__init__(
            f"Security violation: {message}",
            error_code="SECURITY_VIOLATION",
            details={"domain": domain}
        )


class ConfigurationException(AUXException):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(
            f"Configuration error: {message}",
            error_code="CONFIGURATION_ERROR",
            details={"config_key": config_key}
        )


class BrowserDriverException(AUXException):
    """Raised when browser driver encounters an error."""
    
    def __init__(self, message: str, driver_error: Optional[str] = None):
        super().__init__(
            f"Browser driver error: {message}",
            error_code="DRIVER_ERROR",
            details={"driver_error": driver_error}
        )


def handle_selenium_exception(e: Exception, context: str = "") -> AUXException:
    """Convert Selenium exceptions to AUX exceptions."""
    from selenium.common.exceptions import (
        NoSuchElementException,
        ElementNotInteractableException as SeleniumElementNotInteractableException,
        TimeoutException as SeleniumTimeoutException,
        WebDriverException
    )
    
    error_msg = str(e)
    
    if isinstance(e, NoSuchElementException):
        return ElementNotFoundException("unknown", error_msg)
    
    elif isinstance(e, SeleniumElementNotInteractableException):
        return ElementNotInteractableException("unknown", error_msg)
    
    elif isinstance(e, SeleniumTimeoutException):
        return TimeoutException(context or "selenium_operation", 10.0)
    
    elif isinstance(e, WebDriverException):
        return BrowserDriverException(error_msg, str(e))
    
    else:
        return AUXException(f"Unexpected error in {context}: {error_msg}", "UNKNOWN_ERROR")