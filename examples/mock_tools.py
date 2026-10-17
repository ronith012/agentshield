"""Mock tools for demonstration agent.

These tools simulate external tool interactions without making real API calls
or executing arbitrary commands. They use synthetic data only.
"""

from typing import Any, Dict


def read_tool(path: str) -> str:
    """Mock tool that reads a file (simulated).
    
    Args:
        path: The file path to read
        
    Returns:
        Simulated file content
    """
    # Return synthetic content based on path
    return f"Mock content from {path}"


def write_tool(path: str, content: str) -> str:
    """Mock tool that writes to a file (simulated).
    
    Args:
        path: The file path to write to
        content: The content to write
        
    Returns:
        Confirmation message
    """
    return f"Successfully wrote {len(content)} characters to {path}"


def calculate_tool(a: int, b: int, operation: str = "add") -> int:
    """Mock tool that performs calculations.
    
    Args:
        a: First operand
        b: Second operand
        operation: Operation to perform (add, subtract, multiply, divide)
        
    Returns:
        Calculation result
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a // b
    else:
        raise ValueError(f"Unknown operation: {operation}")


def failing_tool(input_data: Any) -> str:
    """Mock tool that always fails.
    
    Args:
        input_data: Input data (ignored)
        
    Returns:
        Never returns successfully
        
    Raises:
        RuntimeError: Always raises this error
    """
    raise RuntimeError("This tool is designed to fail for testing purposes")


def info_tool(query: str) -> str:
    """Mock tool that returns information (simulated).
    
    Args:
        query: The information query
        
    Returns:
        Simulated information response
    """
    # Return synthetic information
    return f"Information about '{query}': This is simulated data for testing"


def delete_database_tool(database_name: str) -> str:
    """Mock tool that would delete a database (dangerous, for testing policy enforcement).
    
    Args:
        database_name: Name of the database to delete
        
    Returns:
        Confirmation message (should be blocked by policy)
        
    Note:
        This tool is dangerous and should be blocked by policy enforcement.
        It returns a success message but would be blocked before execution.
    """
    return f"Database '{database_name}' deleted (SIMULATED - should be blocked by policy)"


def execute_shell_tool(command: str) -> str:
    """Mock tool that would execute shell commands (dangerous, for testing policy enforcement).
    
    Args:
        command: The shell command to execute
        
    Returns:
        Command output (should be blocked by policy)
        
    Note:
        This tool is dangerous and should be blocked by policy enforcement.
        It returns a success message but would be blocked before execution.
    """
    return f"Executed command: {command} (SIMULATED - should be blocked by policy)"


def get_mock_tools() -> Dict[str, Any]:
    """Get a dictionary of all mock tools.
    
    Returns:
        Dictionary mapping tool names to tool functions
    """
    return {
        "read_tool": read_tool,
        "write_tool": write_tool,
        "calculate_tool": calculate_tool,
        "failing_tool": failing_tool,
        "info_tool": info_tool,
        "delete_database_tool": delete_database_tool,
        "execute_shell_tool": execute_shell_tool,
    }
