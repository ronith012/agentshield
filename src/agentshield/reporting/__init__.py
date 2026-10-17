"""Reporting module for AgentShield."""

from .reporting import ReportGenerator, get_failure_explanation
from .html import HTMLReportGenerator

__all__ = ["ReportGenerator", "HTMLReportGenerator", "get_failure_explanation"]
