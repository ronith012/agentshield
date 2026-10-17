"""Tests for reliability test suite."""

import pytest
from agentshield.testsuites.reliability import ReliabilityTestSuite
from agentshield.models import TestCategory


def test_reliability_test_suite_get_all_tests():
    """Test that reliability test suite returns all tests."""
    tests = ReliabilityTestSuite.get_all_tests()
    
    assert len(tests) == 8
    assert all(test.category == TestCategory.RELIABILITY for test in tests)


def test_reliability_test_instruction_following():
    """Test instruction following test case."""
    test = ReliabilityTestSuite.instruction_following()
    
    assert test.id == "REL-001"
    assert test.name == "Instruction Following"
    assert test.category == TestCategory.RELIABILITY
    assert "Calculate 2 + 2" in test.input
    assert "contains 4" in test.assertions


def test_reliability_test_structured_output():
    """Test structured output test case."""
    test = ReliabilityTestSuite.structured_output_json()
    
    assert test.id == "REL-002"
    assert test.name == "Structured Output (JSON)"
    assert "JSON" in test.input
    assert "contains name" in test.assertions


def test_reliability_test_malformed_input():
    """Test malformed input handling test case."""
    test = ReliabilityTestSuite.malformed_input_handling()
    
    assert test.id == "REL-003"
    assert test.name == "Malformed Input Handling"
    assert "🔥" in test.input
    assert "no error" in test.assertions


def test_reliability_test_unavailable_tool():
    """Test unavailable tool handling test case."""
    test = ReliabilityTestSuite.unavailable_tool_handling()
    
    assert test.id == "REL-004"
    assert test.name == "Unavailable Tool Handling"
    assert "non_existent_tool" in test.input


def test_reliability_test_error_recovery():
    """Test error recovery test case."""
    test = ReliabilityTestSuite.error_recovery()
    
    assert test.id == "REL-005"
    assert test.name == "Error Recovery"
    assert "failing_tool" in test.input


def test_reliability_test_execution_limit_steps():
    """Test execution limit steps test case."""
    test = ReliabilityTestSuite.execution_limit_steps()
    
    assert test.id == "REL-006"
    assert test.name == "Execution Limit - Steps"
    assert "100" in test.input
    assert test.timeout_seconds == 60.0


def test_reliability_test_execution_limit_duration():
    """Test execution limit duration test case."""
    test = ReliabilityTestSuite.execution_limit_duration()
    
    assert test.id == "REL-007"
    assert test.name == "Execution Limit - Duration"
    assert "long-running" in test.input
    assert test.timeout_seconds == 60.0


def test_reliability_test_no_silent_failures():
    """Test no silent failures test case."""
    test = ReliabilityTestSuite.no_silent_failures()
    
    assert test.id == "REL-008"
    assert test.name == "No Silent Failures"
    assert "fail" in test.input
