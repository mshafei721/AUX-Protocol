"""AUX Protocol schema definitions."""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field
from enum import Enum


class ElementType(str, Enum):
    """Semantic element types."""
    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    TEXT = "text"
    IMAGE = "image"
    FORM = "form"
    CONTAINER = "container"
    NAVIGATION = "navigation"
    MENU = "menu"
    DIALOG = "dialog"
    TABLE = "table"
    LIST = "list"


class ActionType(str, Enum):
    """Available actions on elements."""
    CLICK = "click"
    TYPE = "type"
    CLEAR = "clear"
    HOVER = "hover"
    SCROLL = "scroll"
    SELECT = "select"
    SUBMIT = "submit"
    FOCUS = "focus"
    BLUR = "blur"


class ElementInfo(BaseModel):
    """Semantic information about a UI element."""
    id: str = Field(description="Unique element identifier")
    type: ElementType = Field(description="Semantic element type")
    tag: str = Field(description="HTML tag name")
    text: Optional[str] = Field(default=None, description="Visible text content")
    value: Optional[str] = Field(default=None, description="Input value")
    placeholder: Optional[str] = Field(default=None, description="Placeholder text")
    aria_label: Optional[str] = Field(default=None, description="ARIA label")
    role: Optional[str] = Field(default=None, description="ARIA role")
    attributes: Dict[str, str] = Field(default_factory=dict, description="HTML attributes")
    position: Dict[str, float] = Field(default_factory=dict, description="Element position")
    size: Dict[str, float] = Field(default_factory=dict, description="Element dimensions")
    visible: bool = Field(default=True, description="Element visibility")
    enabled: bool = Field(default=True, description="Element interactability")
    children: List[str] = Field(default_factory=list, description="Child element IDs")
    parent: Optional[str] = Field(default=None, description="Parent element ID")


class BrowserState(BaseModel):
    """Current browser state observation."""
    url: str = Field(description="Current page URL")
    title: str = Field(description="Page title")
    elements: List[ElementInfo] = Field(description="All semantic elements")
    focused_element: Optional[str] = Field(default=None, description="Currently focused element ID")
    loading: bool = Field(default=False, description="Page loading state")
    alerts: List[str] = Field(default_factory=list, description="Active alerts/dialogs")


class AUXCommand(BaseModel):
    """AUX protocol command structure."""
    action: ActionType = Field(description="Action to perform")
    target: str = Field(description="Target element ID")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Action-specific data")
    wait_for: Optional[str] = Field(default=None, description="Wait condition")
    timeout: float = Field(default=5.0, description="Action timeout in seconds")


class AUXObservation(BaseModel):
    """AUX protocol observation structure."""
    browser_state: BrowserState = Field(description="Current browser state")
    timestamp: float = Field(description="Observation timestamp")
    changes: List[str] = Field(default_factory=list, description="Changed element IDs since last observation")
    events: List[Dict[str, Any]] = Field(default_factory=list, description="Recent events")


class NavigationCommand(BaseModel):
    """Navigation-specific command."""
    url: str = Field(description="URL to navigate to")
    wait_for_load: bool = Field(default=True, description="Wait for page load")
    timeout: float = Field(default=10.0, description="Navigation timeout")


class QueryCommand(BaseModel):
    """Element query command."""
    selector: Optional[str] = Field(default=None, description="CSS selector")
    text: Optional[str] = Field(default=None, description="Text content to match")
    type: Optional[ElementType] = Field(default=None, description="Element type filter")
    attributes: Optional[Dict[str, str]] = Field(default=None, description="Attribute filters")
    limit: int = Field(default=10, description="Maximum results")