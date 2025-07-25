"""Browser adapter for AUX protocol integration."""

import asyncio
import json
from typing import Dict, List, Optional, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .schema import (
    ElementInfo, 
    BrowserState, 
    AUXCommand, 
    AUXObservation,
    NavigationCommand,
    QueryCommand,
    ElementType,
    ActionType
)


class BrowserAdapter:
    """Adapter for browser automation via Selenium WebDriver."""
    
    def __init__(self, headless: bool = False):
        self.driver: Optional[webdriver.Chrome] = None
        self.headless = headless
        self._element_cache: Dict[str, Any] = {}
        self._last_observation_time = 0.0
        self._performance_mode = True  # Enable performance optimizations
        
    async def start(self) -> None:
        """Initialize browser driver with performance optimizations."""
        options = webdriver.ChromeOptions()
        
        # Basic options
        if self.headless:
            options.add_argument("--headless=new")  # Use new headless mode
        
        # Performance optimizations
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Don't load images for speed
        options.add_argument("--disable-javascript-harmony-shipping")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-translate")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--mute-audio")
        options.add_argument("--no-first-run")
        options.add_argument("--safebrowsing-disable-auto-update")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--ignore-certificate-errors-spki-list")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Set page load strategy for faster loading
        options.page_load_strategy = 'eager'  # Don't wait for all resources
        
        # Disable logging to reduce overhead
        options.add_argument("--log-level=3")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Set window size for consistent performance
        options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=options)
        
        # Reduce implicit wait for faster element finding
        self.driver.implicitly_wait(0.5)
        
        # Set page load timeout
        self.driver.set_page_load_timeout(10)
        
        # Execute script to disable images and CSS for even faster loading
        if self._performance_mode:
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 AUX-Protocol-Bot"
            })
        
    async def stop(self) -> None:
        """Close browser driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            
    async def navigate(self, command: NavigationCommand) -> AUXObservation:
        """Navigate to a URL."""
        if not self.driver:
            raise RuntimeError("Browser not started")
            
        self.driver.get(command.url)
        
        if command.wait_for_load:
            WebDriverWait(self.driver, command.timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
        return await self.observe()
        
    async def execute_command(self, command: AUXCommand) -> AUXObservation:
        """Execute an AUX command."""
        if not self.driver:
            raise RuntimeError("Browser not started")
            
        element = self._get_element_by_id(command.target)
        
        if command.action == ActionType.CLICK:
            # Enhanced click handling for different element types
            await self._smart_click(element, command.data)
        elif command.action == ActionType.TYPE:
            text = command.data.get("text", "") if command.data else ""
            await self._smart_type(element, text)
        elif command.action == ActionType.CLEAR:
            await self._smart_clear(element)
        elif command.action == ActionType.SELECT:
            value = command.data.get("value", "") if command.data else ""
            await self._smart_select(element, value)
        elif command.action == ActionType.HOVER:
            ActionChains(self.driver).move_to_element(element).perform()
        elif command.action == ActionType.SCROLL:
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", element)
        elif command.action == ActionType.FOCUS:
            element.click()
        elif command.action == ActionType.SUBMIT:
            element.submit()
            
        # Wait for any specified condition
        if command.wait_for:
            await self._wait_for_condition(command.wait_for, command.timeout)
            
        return await self.observe()
        
    async def query_elements(self, query: QueryCommand) -> List[ElementInfo]:
        """Query elements based on criteria."""
        if not self.driver:
            raise RuntimeError("Browser not started")
            
        elements = []
        
        if query.selector:
            web_elements = self.driver.find_elements(By.CSS_SELECTOR, query.selector)
        else:
            web_elements = self.driver.find_elements(By.XPATH, "//*")
            
        for i, elem in enumerate(web_elements[:query.limit]):
            element_info = self._extract_element_info(elem, f"elem_{i}")
            
            # Apply filters
            if query.text and query.text.lower() not in (element_info.text or "").lower():
                continue
            if query.type and element_info.type != query.type:
                continue
            if query.attributes:
                if not all(element_info.attributes.get(k) == v for k, v in query.attributes.items()):
                    continue
                    
            elements.append(element_info)
            
        return elements
        
    async def observe(self) -> AUXObservation:
        """Get current browser state observation."""
        if not self.driver:
            raise RuntimeError("Browser not started")
            
        # Get all interactive elements with performance optimization
        elements = []
        
        if self._performance_mode:
            # Use single query for better performance
            combined_selector = "button, input, a, select, textarea, [role='button'], [role='link'], [role='textbox'], [onclick], [onsubmit], form"
            try:
                web_elements = self.driver.find_elements(By.CSS_SELECTOR, combined_selector)
                element_id = 0
                for elem in web_elements:
                    try:
                        # Quick visibility check without full is_displayed() call
                        if elem.size['height'] > 0 and elem.size['width'] > 0:
                            element_info = self._extract_element_info(elem, f"aux_{element_id}")
                            elements.append(element_info)
                            element_id += 1
                    except Exception:
                        continue
            except Exception:
                pass
        else:
            # Fallback to original method
            selectors = [
                "button", "input", "a", "select", "textarea", 
                "[role='button']", "[role='link']", "[role='textbox']",
                "[onclick]", "[onsubmit]", "form"
            ]
            
            element_id = 0
            for selector in selectors:
                try:
                    web_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in web_elements:
                        if elem.is_displayed():
                            element_info = self._extract_element_info(elem, f"aux_{element_id}")
                            elements.append(element_info)
                            element_id += 1
                except Exception:
                    continue
                
        # Get focused element
        focused_element = None
        try:
            active = self.driver.switch_to.active_element
            if active:
                focused_element = f"aux_{hash(active) % 10000}"
        except Exception:
            pass
            
        browser_state = BrowserState(
            url=self.driver.current_url,
            title=self.driver.title,
            elements=elements,
            focused_element=focused_element,
            loading=self.driver.execute_script("return document.readyState") != "complete"
        )
        
        import time
        observation = AUXObservation(
            browser_state=browser_state,
            timestamp=time.time(),
            changes=[],  # TODO: Implement change detection
            events=[]    # TODO: Implement event tracking
        )
        
        return observation
        
    def _get_element_by_id(self, element_id: str) -> Any:
        """Get WebDriver element by AUX ID."""
        # This is a simplified implementation
        # In practice, you'd maintain a mapping of AUX IDs to WebDriver elements
        if element_id in self._element_cache:
            return self._element_cache[element_id]
        raise NoSuchElementException(f"Element {element_id} not found")
        
    def _extract_element_info(self, element: Any, element_id: str) -> ElementInfo:
        """Extract semantic information from WebDriver element."""
        # Cache the element for later use
        self._element_cache[element_id] = element
        
        tag = element.tag_name.lower()
        element_type = self._determine_element_type(element, tag)
        
        # Get position and size
        location = element.location
        size = element.size
        
        return ElementInfo(
            id=element_id,
            type=element_type,
            tag=tag,
            text=element.text.strip() if element.text else None,
            value=element.get_attribute("value"),
            placeholder=element.get_attribute("placeholder"),
            aria_label=element.get_attribute("aria-label"),
            role=element.get_attribute("role"),
            attributes={
                "class": element.get_attribute("class") or "",
                "id": element.get_attribute("id") or "",
                "name": element.get_attribute("name") or "",
            },
            position={"x": location["x"], "y": location["y"]},
            size={"width": size["width"], "height": size["height"]},
            visible=element.is_displayed(),
            enabled=element.is_enabled()
        )
        
    def _determine_element_type(self, element: Any, tag: str) -> ElementType:
        """Determine semantic element type."""
        role = element.get_attribute("role")
        element_type = element.get_attribute("type")
        
        if tag == "button" or role == "button":
            return ElementType.BUTTON
        elif tag == "input":
            return ElementType.INPUT
        elif tag == "a":
            return ElementType.LINK
        elif tag == "img":
            return ElementType.IMAGE
        elif tag == "form":
            return ElementType.FORM
        elif tag in ["nav", "navigation"] or role == "navigation":
            return ElementType.NAVIGATION
        elif tag in ["ul", "ol", "li"] or role in ["list", "listitem"]:
            return ElementType.LIST
        elif tag == "table" or role == "table":
            return ElementType.TABLE
        elif role == "dialog":
            return ElementType.DIALOG
        elif role == "menu":
            return ElementType.MENU
        elif tag in ["div", "section", "article", "aside"]:
            return ElementType.CONTAINER
        else:
            return ElementType.TEXT
            
    async def _smart_click(self, element: Any, data: Optional[Dict[str, Any]] = None) -> None:
        """Enhanced click handling for different element types."""
        tag = element.tag_name.lower()
        element_type = element.get_attribute("type")
        
        try:
            # Scroll element into view first
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", element)
            
            # Handle different element types
            if tag == "input":
                if element_type == "checkbox":
                    # For checkboxes, check if we want to set a specific state
                    desired_state = data.get("checked", True) if data else True
                    current_state = element.is_selected()
                    if current_state != desired_state:
                        element.click()
                elif element_type == "radio":
                    # Radio buttons - just click to select
                    element.click()
                elif element_type in ["submit", "button"]:
                    element.click()
                else:
                    # Regular input - focus for typing
                    element.click()
            elif tag == "select":
                # Don't click select elements directly, use _smart_select instead
                pass
            else:
                # Regular click for buttons, links, etc.
                element.click()
                
        except Exception as e:
            # Fallback to JavaScript click if regular click fails
            self.driver.execute_script("arguments[0].click();", element)
    
    async def _smart_type(self, element: Any, text: str) -> None:
        """Enhanced typing for different input types."""
        tag = element.tag_name.lower()
        element_type = element.get_attribute("type")
        
        try:
            # Clear field first if it's a text input
            if tag in ["input", "textarea"] and element_type not in ["checkbox", "radio", "file"]:
                # Use JavaScript to clear for better reliability
                self.driver.execute_script("arguments[0].value = '';", element)
                element.send_keys(text)
            elif element_type == "date":
                # Handle date inputs
                self.driver.execute_script("arguments[0].value = arguments[1];", element, text)
            elif element_type == "time":
                # Handle time inputs
                self.driver.execute_script("arguments[0].value = arguments[1];", element, text)
            elif element_type == "datetime-local":
                # Handle datetime inputs
                self.driver.execute_script("arguments[0].value = arguments[1];", element, text)
            elif element_type == "number":
                # Handle number inputs
                self.driver.execute_script("arguments[0].value = arguments[1];", element, text)
            else:
                element.send_keys(text)
                
        except Exception as e:
            # Fallback to JavaScript
            self.driver.execute_script("arguments[0].value = arguments[1];", element, text)
    
    async def _smart_clear(self, element: Any) -> None:
        """Enhanced clearing for different element types."""
        tag = element.tag_name.lower()
        element_type = element.get_attribute("type")
        
        try:
            if tag in ["input", "textarea"] and element_type not in ["checkbox", "radio"]:
                # Use JavaScript for reliable clearing
                self.driver.execute_script("arguments[0].value = '';", element)
            elif element_type == "checkbox" and element.is_selected():
                element.click()  # Uncheck checkbox
        except Exception:
            pass
    
    async def _smart_select(self, element: Any, value: str) -> None:
        """Enhanced selection for dropdowns and multi-select elements."""
        from selenium.webdriver.support.ui import Select
        
        tag = element.tag_name.lower()
        
        try:
            if tag == "select":
                select = Select(element)
                
                # Try different selection methods
                try:
                    # Try by visible text first
                    select.select_by_visible_text(value)
                except:
                    try:
                        # Try by value
                        select.select_by_value(value)
                    except:
                        try:
                            # Try by index if value is numeric
                            select.select_by_index(int(value))
                        except:
                            # Last resort - find option by partial text match
                            options = select.options
                            for option in options:
                                if value.lower() in option.text.lower():
                                    option.click()
                                    break
            else:
                # For non-select elements, try clicking
                element.click()
                
        except Exception as e:
            # Fallback to JavaScript
            self.driver.execute_script("""
                var element = arguments[0];
                var value = arguments[1];
                if (element.tagName.toLowerCase() === 'select') {
                    for (var i = 0; i < element.options.length; i++) {
                        if (element.options[i].text.toLowerCase().includes(value.toLowerCase()) ||
                            element.options[i].value === value) {
                            element.selectedIndex = i;
                            element.dispatchEvent(new Event('change'));
                            break;
                        }
                    }
                }
            """, element, value)
    
    async def _wait_for_condition(self, condition: str, timeout: float) -> None:
        """Wait for a specified condition."""
        if condition == "page_load":
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )