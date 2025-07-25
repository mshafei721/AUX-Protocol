"""Base classes for AUX Protocol tools."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from mcp.types import TextContent


class AUXTool(ABC):
    """Base class for AUX Protocol tools."""
    
    def __init__(self, adapter):
        """Initialize tool with browser adapter."""
        self.adapter = adapter
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for MCP registration."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for MCP registration."""
        pass
    
    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON schema for tool input parameters."""
        pass
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute the tool with given arguments."""
        pass