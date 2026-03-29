"""Plugin lifecycle hooks for mcp2cli.

The `install` hook is called by Agent Zero when the plugin is first enabled,
automatically installing the mcp2cli CLI tool into the active environment.
"""
import importlib.util
from pathlib import Path


def _load_execute():
    """Load execute.py from plugin root using importlib (avoids sys.path pollution)."""
    execute_path = Path(__file__).parent / "execute.py"
    spec = importlib.util.spec_from_file_location("execute", str(execute_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load execute.py from {execute_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install():
    """Install mcp2cli binary when the plugin is enabled."""
    execute = _load_execute()
    return execute.main()
