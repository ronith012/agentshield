"""Unit tests for report generation."""

import json
import pytest
from agentshield.reporting import ReportGenerator, get_failure_explanation
from agentshield.models import (
    PolicyConfig,
    AgentTestSuiteResult as TestSuiteResult,
    AgentTestResult as TestResult,
    ExecutionTrace,
    TestStatus,
    TestCategory,
)


def test_report_generator_initialization():
    """Test report generator initialization."""
    policy = PolicyConfig()
    generator = ReportGenerator(policy)
    
    assert generator.policy == policy


def test_generate_report():
    """Test report generation."""
    policy = PolicyConfig()
    generator = ReportGenerator(policy)
    
    # Create a test suite result
    result = TestResult(
        test_id="TEST-001",
        status=TestStatus.PASSED,
        execution_trace=ExecutionTrace(steps_taken=1),
        duration_seconds=0.5,
    )
    
    suite_result = TestSuiteResult(
        total_tests=1,
        passed=1,
        failed=0,
        errors=0,
        skipped=0,
        reliability_results=[result],
        total_duration_seconds=0.5,
    )
    
    report = generator.generate_report(suite_result)
    
    assert report.suite_result == suite_result
    assert report.policy_config == policy
    assert len(report.limitations) > 0
    assert "generated_at" in report.metadata


def test_remediation_recommendations():
    """Test remediation recommendation generation."""
    policy = PolicyConfig()
    generator = ReportGenerator(policy)
    
    # Create a failed test result
    result = TestResult(
        test_id="REL-001",
        status=TestStatus.FAILED,
        execution_trace=ExecutionTrace(steps_taken=1),
        failure_reason="Assertions failed",
        duration_seconds=0.5,
    )
    
    suite_result = TestSuiteResult(
        total_tests=1,
        passed=0,
        failed=1,
        errors=0,
        skipped=0,
        reliability_results=[result],
        total_duration_seconds=0.5,
    )
    
    report = generator.generate_report(suite_result)
    
    assert len(report.remediation_recommendations) > 0
    assert any("instruction" in rec.lower() for rec in report.remediation_recommendations)


def test_limitations_generation():
    """Test limitations generation."""
    policy = PolicyConfig()
    generator = ReportGenerator(policy)
    
    suite_result = TestSuiteResult(
        total_tests=0,
        passed=0,
        failed=0,
        errors=0,
        skipped=0,
        total_duration_seconds=0.0,
    )
    
    report = generator.generate_report(suite_result)
    
    assert len(report.limitations) > 0
    assert any("mock" in lim.lower() for lim in report.limitations)
    assert any("synthetic" in lim.lower() for lim in report.limitations)


def test_export_json():
    """Test JSON export."""
    import tempfile
    import os
    
    policy = PolicyConfig()
    generator = ReportGenerator(policy)
    
    suite_result = TestSuiteResult(
        total_tests=1,
        passed=1,
        failed=0,
        errors=0,
        skipped=0,
        total_duration_seconds=0.5,
    )
    
    report = generator.generate_report(suite_result)
    
    # Export to temp file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        temp_path = f.name
    
    try:
        generator.export_json(report, temp_path)
        
        # Verify file exists and is valid JSON
        assert os.path.exists(temp_path)
        
        with open(temp_path, "r") as f:
            loaded = json.load(f)
        
        assert "suite_result" in loaded
        assert "policy_config" in loaded
        assert "limitations" in loaded
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_export_json_string():
    """Test JSON string export."""
    policy = PolicyConfig()
    generator = ReportGenerator(policy)
    
    suite_result = TestSuiteResult(
        total_tests=1,
        passed=1,
        failed=0,
        errors=0,
        skipped=0,
        total_duration_seconds=0.5,
    )
    
    report = generator.generate_report(suite_result)
    
    json_str = generator.export_json_string(report)
    
    # Verify it's valid JSON
    loaded = json.loads(json_str)
    assert "suite_result" in loaded


def test_generate_summary():
    """Test human-readable summary generation."""
    policy = PolicyConfig()
    generator = ReportGenerator(policy)
    
    suite_result = TestSuiteResult(
        total_tests=2,
        passed=1,
        failed=1,
        errors=0,
        skipped=0,
        total_duration_seconds=1.0,
    )
    
    report = generator.generate_report(suite_result)
    
    summary = generator.generate_summary(report)
    
    assert "AgentShield Test Report Summary" in summary
    assert "Total Tests: 2" in summary
    assert "Passed: 1" in summary
    assert "Failed: 1" in summary
    assert "Limitations:" in summary


def test_get_failure_explanation_passed():
    """Test failure explanation for passed test."""
    result = TestResult(
        test_id="TEST-001",
        status=TestStatus.PASSED,
        execution_trace=ExecutionTrace(steps_taken=1),
        duration_seconds=0.5,
    )
    
    explanation = get_failure_explanation(result)
    assert "passed successfully" in explanation.lower()


def test_get_failure_explanation_failed():
    """Test failure explanation for failed test."""
    result = TestResult(
        test_id="TEST-001",
        status=TestStatus.FAILED,
        execution_trace=ExecutionTrace(steps_taken=1),
        failure_reason="Test assertion failed",
        duration_seconds=0.5,
        evidence={"tool_calls": 5},
    )
    
    explanation = get_failure_explanation(result)
    assert "failed" in explanation.lower()
    assert "Test assertion failed" in explanation
    assert "Evidence:" in explanation


def test_get_failure_explanation_error():
    """Test failure explanation for error test."""
    result = TestResult(
        test_id="TEST-001",
        status=TestStatus.ERROR,
        execution_trace=ExecutionTrace(error="Test error"),
        error_message="Execution error occurred",
        duration_seconds=0.5,
    )
    
    explanation = get_failure_explanation(result)
    assert "execution error" in explanation.lower()
    assert "Execution error occurred" in explanation


def test_get_failure_explanation_skipped():
    """Test failure explanation for skipped test."""
    result = TestResult(
        test_id="TEST-001",
        status=TestStatus.SKIPPED,
        execution_trace=ExecutionTrace(steps_taken=0),
        duration_seconds=0.0,
    )
    
    explanation = get_failure_explanation(result)
    assert "skipped" in explanation.lower()


def test_high_failure_rate_recommendation():
    """Test recommendation for high failure rate."""
    policy = PolicyConfig()
    generator = ReportGenerator(policy)
    
    # Create many failed tests
    results = [
        TestResult(
            test_id=f"TEST-{i:03d}",
            status=TestStatus.FAILED,
            execution_trace=ExecutionTrace(steps_taken=1),
            failure_reason="Failed",
            duration_seconds=0.5,
        )
        for i in range(6)
    ]
    
    suite_result = TestSuiteResult(
        total_tests=10,
        passed=4,
        failed=6,
        errors=0,
        skipped=0,
        reliability_results=results,
        total_duration_seconds=3.0,
    )
    
    report = generator.generate_report(suite_result)
    
    # Should include high failure rate recommendation
    assert any("high failure rate" in rec.lower() for rec in report.remediation_recommendations)
