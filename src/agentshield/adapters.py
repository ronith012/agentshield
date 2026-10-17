"""Agent adapter interface for AgentShield.

This module defines the abstract base class that all agent implementations
must follow. Third-party developers can extend the framework by implementing
this interface without modifying the core implementation.
"""

from abc import ABC, abstractmethod
from typing import Any

from agentshield.models import ExecutionTrace, PolicyConfig


class AgentAdapter(ABC):
    """Abstract base class for agent implementations.

    This interface defines the contract that all agent adapters must implement.
    Third-party developers can create custom agents by extending this class
    and implementing the required methods.

    Example:
        ```python
        from agentshield.adapters import AgentAdapter
        from agentshield.models import ExecutionTrace, PolicyConfig

        class MyAgent(AgentAdapter):
            def execute(self, input: str, tools: Dict[str, Any], policy: PolicyConfig) -> ExecutionTrace:
                # Implement agent logic here
                trace = ExecutionTrace()
                # ... agent execution ...
                return trace

            def get_name(self) -> str:
                return "my_agent"
        ```
    """

    @abstractmethod
    def execute(self, input: str, tools: dict[str, Any], policy: PolicyConfig) -> ExecutionTrace:
        """
        Execute the agent with the given input and tools.

        Args:
            input: The input prompt or instruction for the agent
            tools: Dictionary of available tools (name -> callable)
            policy: Policy constraints to enforce during execution

        Returns:
            ExecutionTrace containing tool calls, outputs, and metrics

        Note:
            The implementation should respect the policy constraints,
            including tool allowlists/denylists and execution limits.
            The policy engine will also enforce these constraints at
            the framework level for defense in depth.
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Return the name of this agent implementation.

        Returns:
            A string identifier for the agent
        """
        pass
