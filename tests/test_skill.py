"""Tests for the mcp2cli skill file and server-config resolver."""
import importlib.util
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = PLUGIN_ROOT / "skills" / "mcp2cli" / "SKILL.md"
HELPER_PATH = PLUGIN_ROOT / "helpers" / "mcp_servers.py"


def _load_helper():
    spec = importlib.util.spec_from_file_location("mcp_servers", str(HELPER_PATH))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestSkillFile:
    def test_file_exists(self):
        assert SKILL_PATH.is_file()

    def test_has_yaml_frontmatter(self):
        content = SKILL_PATH.read_text()
        assert content.startswith("---")
        assert content.count("---") >= 2

    def test_yaml_has_name(self):
        content = SKILL_PATH.read_text()
        fm = content.split("---")[1]
        assert "name:" in fm

    def test_yaml_has_description(self):
        content = SKILL_PATH.read_text()
        fm = content.split("---")[1]
        assert "description:" in fm

    def test_yaml_has_trigger_patterns(self):
        content = SKILL_PATH.read_text()
        fm = content.split("---")[1]
        assert "trigger_patterns:" in fm

    def test_skill_uses_code_execution_tool(self):
        content = SKILL_PATH.read_text()
        body = "---".join(content.split("---")[2:])
        assert "code_execution_tool" in body
        assert "runtime" in body
        assert "terminal" in body

    def test_skill_mentions_uvx(self):
        content = SKILL_PATH.read_text()
        body = "---".join(content.split("---")[2:])
        assert "uvx mcp2cli" in body

    def test_skill_mentions_helper_script(self):
        content = SKILL_PATH.read_text()
        body = "---".join(content.split("---")[2:])
        assert "mcp_servers.py" in body

    def test_skill_mentions_compact_flag(self):
        content = SKILL_PATH.read_text()
        body = "---".join(content.split("---")[2:])
        assert "--compact" in body

    def test_skill_no_hardcoded_server_names(self):
        """Skill should NOT hardcode instance-specific server names."""
        content = SKILL_PATH.read_text()
        fm = content.split("---")[1]
        desc_line = [l for l in fm.split("\n") if "description:" in l][0]
        assert "gtm" not in desc_line.lower()
        assert "deep-wiki" not in desc_line.lower()
        assert "google analytics" not in desc_line.lower()

    def test_skill_no_removed_tool_args(self):
        """Skill should NOT reference the old Tool class args."""
        content = SKILL_PATH.read_text()
        body = "---".join(content.split("---")[2:])
        assert '"action":' not in body
        assert '"tool_name": "mcp2cli"' not in body

    def test_skill_mentions_discovery_workflow(self):
        content = SKILL_PATH.read_text()
        body = "---".join(content.split("---")[2:])
        assert "list" in body.lower()
        assert "help" in body.lower()
        assert "call" in body.lower()


class TestHelperScript:
    def test_file_exists(self):
        assert HELPER_PATH.is_file()

    def test_load_servers_returns_dict(self):
        mod = _load_helper()
        servers = mod.load_servers()
        assert isinstance(servers, dict)

    def test_connection_line_format_url(self):
        mod = _load_helper()
        conn = mod._connection_line("test", {"url": "https://example.com/mcp", "type": "streamable-http"})
        assert "--mcp" in conn
        assert "streamable" in conn

    def test_connection_line_format_stdio(self):
        mod = _load_helper()
        conn = mod._connection_line("test", {"command": "npx", "args": ["foo"], "env": {"K": "v"}})
        assert "--mcp-stdio" in conn
        assert "--env" in conn
