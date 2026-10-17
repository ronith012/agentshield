"""Tests for security test suite."""

import pytest
from agentshield.testsuites.security import SecurityTestSuite
from agentshield.models import TestCategory


def test_security_test_suite_get_all_tests():
    """Test that security test suite returns all tests."""
    tests = SecurityTestSuite.get_all_tests()
    
    assert len(tests) == 10
    assert all(test.category == TestCategory.SECURITY for test in tests)


def test_security_test_direct_prompt_override():
    """Test direct prompt override test case."""
    test = SecurityTestSuite.direct_prompt_override()
    
    assert test.id == "SEC-001"
    assert test.name == "Direct Prompt Override"
    assert test.category == TestCategory.SECURITY
    assert "system prompt" in test.input
    assert "prompt-injection" in test.tags


def test_security_test_indirect_injection():
    """Test indirect injection via tool output test case."""
    test = SecurityTestSuite.indirect_injection_via_tool_output()
    
    assert test.id == "SEC-002"
    assert test.name == "Indirect Injection via Tool Output"
    assert "info_tool" in test.input
    assert "indirect" in test.tags


def test_security_test_roleplay_injection():
    """Test roleplay injection test case."""
    test = SecurityTestSuite.roleplay_injection()
    
    assert test.id == "SEC-003"
    assert test.name == "Roleplay Injection (DAN-style)"
    assert "DAN" in test.input
    assert "jailbreak" in test.tags


def test_security_test_tool_permission_denylist():
    """Test tool permission denylist test case."""
    test = SecurityTestSuite.tool_permission_denylist()
    
    assert test.id == "SEC-004"
    assert test.name == "Tool Permission - Denylist"
    assert "delete_database" in test.input
    assert "denylist" in test.tags


def test_security_test_tool_permission_allowlist():
    """Test tool permission allowlist test case."""
    test = SecurityTestSuite.tool_permission_allowlist()
    
    assert test.id == "SEC-005"
    assert test.name == "Tool Permission - Allowlist"
    assert "allowlist" in test.tags


def test_security_test_oversized_input():
    """Test oversized input test case."""
    test = SecurityTestSuite.oversized_input()
    
    assert test.id == "SEC-006"
    assert test.name == "Oversized Input"
    assert len(test.input) == 10000
    assert test.timeout_seconds == 30.0


def test_security_test_sensitive_data_exposure():
    """Test sensitive data exposure test case."""
    test = SecurityTestSuite.sensitive_data_exposure()
    
    assert test.id == "SEC-007"
    assert test.name == "Sensitive Data Exposure"
    assert "API key" in test.input
    assert "sensitive-data" in test.tags


def test_security_test_unauthorized_action():
    """Test unauthorized action test case."""
    test = SecurityTestSuite.unauthorized_action()
    
    assert test.id == "SEC-008"
    assert test.name == "Unauthorized Action"
    assert "rm -rf" in test.input
    assert "actions" in test.tags


def test_security_test_encoding_evasion():
    """Test encoding evasion test case."""
    test = SecurityTestSuite.encoding_evasion_base64()
    
    assert test.id == "SEC-009"
    assert test.name == "Encoding Evasion (Base64)"
    assert "SGVsbG8=" in test.input
    assert "encoding" in test.tags


def test_security_test_execution_budget():
    """Test execution budget enforcement test case."""
    test = SecurityTestSuite.execution_budget_enforcement()
    
    assert test.id == "SEC-010"
    assert test.name == "Execution Budget Enforcement"
    assert "50" in test.input
    assert test.timeout_seconds == 60.0
