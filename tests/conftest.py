import json
import os
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

# ── Plugin root paths ──────────────────────────────────────────────
PLUGIN_ROOT = Path(__file__).resolve().parent.parent


# ── Mock Agent Zero framework modules before importing plugin code ──
def _install_mock_helpers():
    helpers = types.ModuleType("helpers")
    helpers_tool = types.ModuleType("helpers.tool")

    class MockResponse:
        def __init__(self, message="", break_loop=False):
            self.message = message
            self.break_loop = break_loop

    class MockTool:
        def __init__(self):
            self.log = MagicMock()
            self.log.update = MagicMock()
            self.add_progress = MagicMock()

    helpers_tool.Response = MockResponse
    helpers_tool.Tool = MockTool

    helpers_extension = types.ModuleType("helpers.extension")

    class MockExtension:
        def __init__(self):
            self.agent = None

    helpers_extension.Extension = MockExtension

    sys.modules["helpers"] = helpers
    sys.modules["helpers.tool"] = helpers_tool
    sys.modules["helpers.extension"] = helpers_extension


_install_mock_helpers()


# ── Fixtures ────────────────────────────────────────────────────────

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
def tmp_settings_dir(tmp_path):
    usr_dir = tmp_path / "usr"
    usr_dir.mkdir()
    return usr_dir


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
def write_settings(tmp_settings_dir, sample_servers):
    settings_path = tmp_settings_dir / "settings.json"
    settings = {"mcp_servers": {"mcpServers": sample_servers}}
    settings_path.write_text(json.dumps(settings))
    return settings_path


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
