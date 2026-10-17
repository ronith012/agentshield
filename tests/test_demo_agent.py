"""Tests for the demonstration agent."""

import sys
from pathlib import Path

# Add examples directory to path
examples_dir = Path(__file__).parent.parent / "examples"
sys.path.insert(0, str(examples_dir))

import pytest
from demo_agent import MockAgent, create_demo_agent
from mock_tools import get_mock_tools
from demo_policy import get_demo_policy


def test_mock_agent_compliant_scenario():
    """Test the compliant scenario of the mock agent."""
    agent = MockAgent(scenario="compliant")
    tools = get_mock_tools()
    policy = get_demo_policy()
    
    trace = agent.execute("calculate 2 + 2", tools, policy)
    
    assert trace.final_output == "4"
    assert trace.steps_taken == 1
    assert len(trace.tool_calls) == 1
    assert trace.tool_calls[0].name == "calculate_tool"


def test_mock_agent_policy_violating_scenario():
    """Test the policy-violating scenario of the mock agent."""
    agent = MockAgent(scenario="policy_violating")
    tools = get_mock_tools()
    policy = get_demo_policy()
    
    trace = agent.execute("delete_database production", tools, policy)
    
    assert "deleted" in trace.final_output.lower()
    assert len(trace.tool_calls) == 1
    assert trace.tool_calls[0].name == "delete_database_tool"


def test_mock_agent_untrusted_handler_scenario():
    """Test the untrusted handler scenario of the mock agent."""
    agent = MockAgent(scenario="untrusted_handler")
    tools = get_mock_tools()
    policy = get_demo_policy()
    
    trace = agent.execute("untrusted input", tools, policy)
    
    assert trace.final_output == "HACKED"
    assert len(trace.tool_calls) == 1
    assert trace.tool_calls[0].name == "info_tool"


def test_mock_agent_malformed_output_scenario():
    """Test the malformed output scenario of the mock agent."""
    agent = MockAgent(scenario="malformed_output")
    tools = get_mock_tools()
    policy = get_demo_policy()
    
    trace = agent.execute("malformed input", tools, policy)
    
    assert trace.final_output == "{invalid json: no closing brace"
    assert trace.steps_taken == 1


def test_mock_agent_limit_violator_scenario():
    """Test the limit violator scenario of the mock agent."""
    agent = MockAgent(scenario="limit_violator")
    tools = get_mock_tools()
    policy = get_demo_policy()
    
    trace = agent.execute("limit input", tools, policy)
    
    assert len(trace.tool_calls) == 20
    assert trace.steps_taken == 20
    assert "20" in trace.final_output


def test_create_demo_agent():
    """Test the factory function for creating demo agents."""
    agent = create_demo_agent(scenario="compliant")
    
    assert agent.get_name() == "MockAgent(compliant)"
    assert agent.scenario == "compliant"


def test_mock_agent_adapter_interface():
    """Test that the mock agent implements the adapter interface correctly."""
    from agentshield.adapters import AgentAdapter
    
    agent = MockAgent()
    assert isinstance(agent, AgentAdapter)
    assert callable(agent.execute)
    assert callable(agent.get_name)
