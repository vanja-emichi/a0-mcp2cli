import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

# Plugin lives inside the agent-zero tree; use the real framework, not mocks.
PLUGIN_ROOT = Path(__file__).resolve().parent.parent
_PROJECT_ROOT = PLUGIN_ROOT.parents[2]  # .../loloi
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


@pytest.fixture
def plugin_root():
    return PLUGIN_ROOT


@pytest.fixture
def tool_path(plugin_root):
    return plugin_root / "tools" / "mcp2cli.py"


@pytest.fixture
def hooks_path(plugin_root):
    return plugin_root / "hooks.py"


@pytest.fixture
def execute_path(plugin_root):
    return plugin_root / "execute.py"


@pytest.fixture
def extension_path(plugin_root):
    return plugin_root / "extensions" / "python" / "system_prompt" / "_30_mcp2cli_skill_hint.py"


@pytest.fixture
def manifest_path(plugin_root):
    return plugin_root / "plugin.yaml"


@pytest.fixture
def skill_path(plugin_root):
    return plugin_root / "skills" / "mcp2cli" / "SKILL.md"


@pytest.fixture
def prompt_path(plugin_root):
    return plugin_root / "prompts" / "default" / "agent.system.tools.mcp2cli.md"


@pytest.fixture
def sample_servers():
    return {
        "test-http": {
            "url": "https://mcp.example.com/mcp",
            "type": "streamable-http",
            "disabled": True,
            "description": "Test HTTP server",
        },
        "test-stdio": {
            "command": "npx",
            "args": ["test-mcp-server"],
            "env": {"API_KEY": "sk-test-123"},
            "disabled": False,
        },
        "test-sse": {
            "url": "https://mcp.example.com/sse",
            "type": "sse",
            "disabled": True,
        },
    }


@pytest.fixture
def http_server_cfg():
    return {"url": "https://mcp.example.com/mcp", "type": "streamable-http"}


@pytest.fixture
def sse_server_cfg():
    return {"url": "https://mcp.example.com/sse", "type": "sse"}


@pytest.fixture
def stdio_server_cfg():
    return {
        "command": "npx",
        "args": ["test-mcp-server"],
        "env": {"API_KEY": "sk-test-123"},
    }
