"""AUX Protocol - Agent UX Layer for semantic browser automation."""

__version__ = "0.1.0"
__author__ = "AUX Protocol Contributors"
__description__ = "Semantic interface protocol for AI agents"

from .schema import (
    AUXCommand,
    AUXObservation,
    ElementInfo,
    BrowserState,
)

__all__ = [
    "AUXCommand",
    "AUXObservation", 
    "ElementInfo",
    "BrowserState",
]