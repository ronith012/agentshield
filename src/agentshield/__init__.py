"""AgentShield: AI Agent Reliability and Security Testing Framework."""

__version__ = "0.1.0"

from agentshield.adapters import AgentAdapter
from agentshield.models import (
    AgentTestCase as TestCase,
)
from agentshield.models import (
    AgentTestResult as TestResult,
)
from agentshield.models import (
    AgentTestSuiteResult as TestSuiteResult,
)
from agentshield.models import (
    ExecutionTrace,
    PolicyConfig,
    Report,
    TestCategory,
    TestStatus,
    ToolCall,
)
from agentshield.policies import PolicyEngine, PolicyViolationError, validate_policy
from agentshield.reporting import ReportGenerator
from agentshield.runner import TestRunner

__all__ = [
    "__version__",
    "TestStatus",
    "TestCategory",
    "ToolCall",
    "ExecutionTrace",
    "PolicyConfig",
    "TestCase",
    "TestResult",
    "TestSuiteResult",
    "Report",
    "AgentAdapter",
    "PolicyEngine",
    "PolicyViolationError",
    "validate_policy",
    "TestRunner",
    "ReportGenerator",
]
