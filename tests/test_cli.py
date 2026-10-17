"""Tests for CLI commands."""

import pytest
import tempfile
import os
import subprocess
from pathlib import Path


def test_cli_list_tests():
    """Test list-tests command."""
    result = subprocess.run(
        ["python3", "-m", "agentshield.cli", "list-tests"],
        capture_output=True,
        text=True,
        cwd="/Users/ronithbodepudi/Documents/Projects/AgentSheild - AI Agent Reliability & Security"
    )
    
    assert result.returncode == 0
    assert "Available Tests" in result.stdout
    assert "REL-001" in result.stdout
    assert "SEC-001" in result.stdout


def test_cli_list_tests_category_filter():
    """Test list-tests with category filter."""
    result = subprocess.run(
        ["python3", "-m", "agentshield.cli", "list-tests", "--category", "reliability"],
        capture_output=True,
        text=True,
        cwd="/Users/ronithbodepudi/Documents/Projects/AgentSheild - AI Agent Reliability & Security"
    )
    
    assert result.returncode == 0
    assert "REL-001" in result.stdout
    # Should not show security tests
    assert "SEC-001" not in result.stdout


def test_cli_init():
    """Test init command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["python3", "-m", "agentshield.cli", "init", tmpdir],
            capture_output=True,
            text=True,
            cwd="/Users/ronithbodepudi/Documents/Projects/AgentSheild - AI Agent Reliability & Security"
        )
        
        assert result.returncode == 0
        assert "Initializing AgentShield project" in result.stdout
        
        # Check that files were created
        assert os.path.exists(os.path.join(tmpdir, "agent.py"))
        assert os.path.exists(os.path.join(tmpdir, "policy.yaml"))
        assert os.path.exists(os.path.join(tmpdir, "agentshield.config.yaml"))
        assert os.path.exists(os.path.join(tmpdir, "tests"))


def test_cli_help():
    """Test help command."""
    result = subprocess.run(
        ["python3", "-m", "agentshield.cli", "--help"],
        capture_output=True,
        text=True,
        cwd="/Users/ronithbodepudi/Documents/Projects/AgentSheild - AI Agent Reliability & Security"
    )
    
    assert result.returncode == 0
    assert "AgentShield" in result.stdout
    assert "test" in result.stdout
    assert "report" in result.stdout
    assert "list-tests" in result.stdout
    assert "init" in result.stdout
