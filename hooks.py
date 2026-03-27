"""Plugin lifecycle hooks for mcp2cli.

The `install` hook is called by Agent Zero when the plugin is first enabled,
automatically installing the mcp2cli CLI tool into the active environment.
"""
from execute import main


def install():
    """Install mcp2cli binary when the plugin is enabled."""
    return main()
