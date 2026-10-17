"""Configuration management for AgentShield."""

import yaml
from pathlib import Path
from typing import Any


class Config:
    """AgentShield project configuration."""

    def __init__(self, data: dict[str, Any] | None = None):
        """Initialize configuration.

        Args:
            data: Configuration data dictionary
        """
        self.data = data or {}

    @property
    def agent_path(self) -> str | None:
        """Get the agent file path."""
        return self.data.get("agent_path")

    @property
    def policy_path(self) -> str | None:
        """Get the policy file path."""
        return self.data.get("policy_path")

    @property
    def default_output(self) -> str:
        """Get the default output path."""
        return self.data.get("default_output", "results.json")

    @staticmethod
    def load(path: str | Path) -> "Config":
        """Load configuration from a YAML file.

        Args:
            path: Path to the configuration file

        Returns:
            Config object
        """
        path = Path(path)
        if not path.exists():
            return Config()

        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}

        return Config(data)

    @staticmethod
    def find(start_dir: str | Path = ".") -> "Config":
        """Find and load configuration from current directory.

        Looks for .agentshield.yaml or agentshield.config.yaml

        Args:
            start_dir: Directory to start searching from

        Returns:
            Config object
        """
        start_dir = Path(start_dir).resolve()

        # Check for .agentshield.yaml
        config_path = start_dir / ".agentshield.yaml"
        if config_path.exists():
            return Config.load(config_path)

        # Check for agentshield.config.yaml
        config_path = start_dir / "agentshield.config.yaml"
        if config_path.exists():
            return Config.load(config_path)

        # Check parent directories
        parent = start_dir.parent
        if parent != start_dir:
            return Config.find(parent)

        return Config()
