"""Core data models for AgentShield."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TestStatus(str, Enum):
    """Status of a test execution."""

    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class TestCategory(str, Enum):
    """Category of test."""

    RELIABILITY = "reliability"
    SECURITY = "security"


class ToolCall(BaseModel):
    """Record of a tool invocation."""

    name: str
    arguments: dict[str, Any]
    result: Any | None = None
    error: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ExecutionTrace(BaseModel):
    """Trace of agent execution."""

    tool_calls: list[ToolCall] = Field(default_factory=list)
    steps_taken: int = 0
    duration_seconds: float = 0.0
    final_output: str | None = None
    error: str | None = None


class PolicyConfig(BaseModel):
    """Configuration for agent constraints."""

    allowed_tools: list[str] | None = None
    prohibited_tools: list[str] = Field(default_factory=list)
    max_steps: int | None = None
    max_duration_seconds: float | None = None
    max_tool_calls: int | None = None
    permitted_output_formats: list[str] | None = None
    sensitive_values_to_redact: list[str] = Field(default_factory=list)


class AgentTestCase(BaseModel):
    """Definition of a single test case."""

    id: str
    name: str
    description: str
    category: TestCategory
    input: str
    expected_behavior: str
    assertions: list[str]
    tags: list[str] = Field(default_factory=list)
    timeout_seconds: float = 30.0


class AgentTestResult(BaseModel):
    """Result of a single test execution."""

    test_id: str
    status: TestStatus
    execution_trace: ExecutionTrace
    failure_reason: str | None = None
    error_message: str | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)
    duration_seconds: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentTestSuiteResult(BaseModel):
    """Aggregated results for a test suite."""

    total_tests: int
    passed: int
    failed: int
    errors: int
    skipped: int
    reliability_results: list[AgentTestResult] = Field(default_factory=list)
    security_results: list[AgentTestResult] = Field(default_factory=list)
    total_duration_seconds: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Report(BaseModel):
    """Structured test report."""

    suite_result: AgentTestSuiteResult
    policy_config: PolicyConfig
    remediation_recommendations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
