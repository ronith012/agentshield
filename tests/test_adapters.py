"""Unit tests for agent adapter interface."""

import pytest
from agentshield.adapters import AgentAdapter
from agentshield.models import ExecutionTrace, PolicyConfig


def test_agent_adapter_is_abstract():
    """Test that AgentAdapter cannot be instantiated directly."""
    with pytest.raises(TypeError):
        AgentAdapter()


def test_custom_agent_adapter():
    """Test that a custom agent can implement the adapter interface."""
    
    class CustomAgent(AgentAdapter):
        def execute(self, input: str, tools: dict, policy: PolicyConfig) -> ExecutionTrace:
            trace = ExecutionTrace(
                steps_taken=1,
                duration_seconds=0.1,
                final_output=f"Processed: {input}",
            )
            return trace
        
        def get_name(self) -> str:
            return "custom_agent"
    
    agent = CustomAgent()
    policy = PolicyConfig()
    tools = {}
    
    trace = agent.execute("test input", tools, policy)
    
    assert agent.get_name() == "custom_agent"
    assert trace.final_output == "Processed: test input"
    assert trace.steps_taken == 1


def test_agent_adapter_with_tools():
    """Test agent adapter with tool usage."""
    
    class ToolUsingAgent(AgentAdapter):
        def execute(self, input: str, tools: dict, policy: PolicyConfig) -> ExecutionTrace:
            from agentshield.models import ToolCall
            from datetime import datetime
            
            # Simulate using a tool
            tool_call = ToolCall(
                name="test_tool",
                arguments={"input": input},
                result="tool result",
                timestamp=datetime.utcnow(),
            )
            
            trace = ExecutionTrace(
                tool_calls=[tool_call],
                steps_taken=1,
                duration_seconds=0.1,
                final_output="Used tool successfully",
            )
            return trace
        
        def get_name(self) -> str:
            return "tool_using_agent"
    
    agent = ToolUsingAgent()
    policy = PolicyConfig()
    tools = {"test_tool": lambda x: f"result: {x}"}
    
    trace = agent.execute("test", tools, policy)
    
    assert len(trace.tool_calls) == 1
    assert trace.tool_calls[0].name == "test_tool"
