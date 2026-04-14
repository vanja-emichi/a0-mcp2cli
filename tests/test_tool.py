import asyncio
import importlib
import json
import shlex
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

TOOL_PATH = str(Path(__file__).resolve().parent.parent / "tools" / "mcp2cli.py")


def _import_tool():
    spec = importlib.util.spec_from_file_location("mcp2cli_tool", TOOL_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestGetMcp2CliBin:
    def test_returns_mcp2cli_when_installed(self, monkeypatch):
        mod = _import_tool()
        monkeypatch.setattr("shutil.which", lambda cmd: "/usr/local/bin/mcp2cli" if cmd == "mcp2cli" else None)
        assert mod._get_mcp2cli_bin() == ["mcp2cli"]

    def test_returns_uvx_mcp2cli_when_no_binary(self, monkeypatch):
        mod = _import_tool()
        monkeypatch.setattr("shutil.which", lambda cmd: "/usr/local/bin/uvx" if cmd == "uvx" else None)
        assert mod._get_mcp2cli_bin() == ["uvx", "mcp2cli"]

    def test_raises_runtime_error_when_nothing_found(self, monkeypatch):
        mod = _import_tool()
        monkeypatch.setattr("shutil.which", lambda cmd: None)
        with pytest.raises(RuntimeError, match="mcp2cli not found"):
            mod._get_mcp2cli_bin()

    def test_prefers_binary_over_uvx(self, monkeypatch):
        mod = _import_tool()
        monkeypatch.setattr("shutil.which", lambda cmd: "/usr/bin/" + cmd)
        assert mod._get_mcp2cli_bin() == ["mcp2cli"]


class TestLoadMcpServers:
    def test_loads_valid_settings(self, tmp_path, monkeypatch):
        mod = _import_tool()
        settings = {"mcp_servers": {"mcpServers": {"srv1": {"url": "http://x"}}}}
        usr_dir = tmp_path / "usr"
        usr_dir.mkdir()
        sf = usr_dir / "settings.json"
        sf.write_text(json.dumps(settings))
        monkeypatch.setattr(mod, "_A0_ROOT", str(tmp_path))
        result = mod._load_mcp_servers()
        assert "srv1" in result

    def test_returns_empty_when_no_file(self, tmp_path, monkeypatch):
        mod = _import_tool()
        monkeypatch.setattr(mod, "_A0_ROOT", str(tmp_path))
        assert mod._load_mcp_servers() == {}

    def test_returns_empty_when_no_mcp_key(self, tmp_path, monkeypatch):
        mod = _import_tool()
        usr_dir = tmp_path / "usr"
        usr_dir.mkdir()
        sf = usr_dir / "settings.json"
        sf.write_text(json.dumps({"other": 1}))
        monkeypatch.setattr(mod, "_A0_ROOT", str(tmp_path))
        assert mod._load_mcp_servers() == {}

    def test_handles_string_mcp_servers(self, tmp_path, monkeypatch):
        mod = _import_tool()
        inner = json.dumps({"mcpServers": {"srv": {"url": "http://x"}}})
        usr_dir = tmp_path / "usr"
        usr_dir.mkdir()
        sf = usr_dir / "settings.json"
        sf.write_text(json.dumps({"mcp_servers": inner}))
        monkeypatch.setattr(mod, "_A0_ROOT", str(tmp_path))
        assert "srv" in mod._load_mcp_servers()

    def test_handles_corrupt_json(self, tmp_path, monkeypatch):
        mod = _import_tool()
        usr_dir = tmp_path / "usr"
        usr_dir.mkdir()
        sf = usr_dir / "settings.json"
        sf.write_text("NOT JSON")
        monkeypatch.setattr(mod, "_A0_ROOT", str(tmp_path))
        assert mod._load_mcp_servers() == {}


class TestBuildCmd:
    def test_http_list(self, http_server_cfg):
        mod = _import_tool()
        cmd = mod._build_cmd(["mcp2cli"], http_server_cfg, "list", "", "", "", False)
        assert "--mcp" in cmd
        assert "https://mcp.example.com/mcp" in cmd
        assert "--transport" in cmd
        assert "streamable" in cmd
        assert "--pretty" in cmd
        assert "--list" in cmd

    def test_sse_transport(self, sse_server_cfg):
        mod = _import_tool()
        cmd = mod._build_cmd(["mcp2cli"], sse_server_cfg, "list", "", "", "", False)
        assert "--transport" in cmd
        assert "sse" in cmd

    def test_http_no_type_no_transport(self):
        mod = _import_tool()
        cmd = mod._build_cmd(["mcp2cli"], {"url": "http://x"}, "list", "", "", "", False)
        assert "--transport" not in cmd

    def test_stdio_with_env(self, stdio_server_cfg):
        mod = _import_tool()
        cmd = mod._build_cmd(["mcp2cli"], stdio_server_cfg, "list", "", "", "", False)
        assert "--mcp-stdio" in cmd
        assert "--env" in cmd
        idx = cmd.index("--env")
        assert cmd[idx + 1] == "API_KEY=sk-test-123"

    def test_stdio_no_env(self):
        mod = _import_tool()
        cfg = {"command": "npx", "args": ["my-server"]}
        cmd = mod._build_cmd(["mcp2cli"], cfg, "list", "", "", "", False)
        assert "--env" not in cmd

    def test_toon_overrides_pretty(self, http_server_cfg):
        mod = _import_tool()
        cmd = mod._build_cmd(["mcp2cli"], http_server_cfg, "list", "", "", "", True)
        assert "--toon" in cmd
        assert "--pretty" not in cmd

    def test_search_action(self, http_server_cfg):
        mod = _import_tool()
        cmd = mod._build_cmd(["mcp2cli"], http_server_cfg, "search", "", "", "tag", False)
        assert "--search" in cmd
        assert "tag" in cmd

    def test_search_requires_query(self, http_server_cfg):
        mod = _import_tool()
        with pytest.raises(ValueError, match="search_query is required"):
            mod._build_cmd(["mcp2cli"], http_server_cfg, "search", "", "", "", False)

    def test_help_action(self, http_server_cfg):
        mod = _import_tool()
        cmd = mod._build_cmd(["mcp2cli"], http_server_cfg, "help", "list-tags", "", "", False)
        assert "list-tags" in cmd
        assert "--help" in cmd

    def test_help_requires_tool_name(self, http_server_cfg):
        mod = _import_tool()
        with pytest.raises(ValueError, match="tool_name is required"):
            mod._build_cmd(["mcp2cli"], http_server_cfg, "help", "", "", "", False)

    def test_call_json_params(self, http_server_cfg):
        mod = _import_tool()
        cmd = mod._build_cmd(["mcp2cli"], http_server_cfg, "call", "x", '{"a_b": "1"}', "", False)
        assert "x" in cmd
        assert "--a-b" in cmd

    def test_call_cli_flags_params(self, http_server_cfg):
        mod = _import_tool()
        cmd = mod._build_cmd(["mcp2cli"], http_server_cfg, "call", "x", "--a-b 1", "", False)
        assert "--a-b" in cmd

    def test_call_requires_tool_name(self, http_server_cfg):
        mod = _import_tool()
        with pytest.raises(ValueError, match="tool_name is required"):
            mod._build_cmd(["mcp2cli"], http_server_cfg, "call", "", "", "", False)

    def test_unknown_action_raises(self, http_server_cfg):
        mod = _import_tool()
        with pytest.raises(ValueError, match="Unknown action"):
            mod._build_cmd(["mcp2cli"], http_server_cfg, "bad", "", "", "", False)

    def test_cfg_needs_url_or_command(self):
        mod = _import_tool()
        with pytest.raises(ValueError, match="url.*or.*command"):
            mod._build_cmd(["mcp2cli"], {"x": "y"}, "list", "", "", "", False)

    def test_call_empty_params(self, http_server_cfg):
        mod = _import_tool()
        cmd = mod._build_cmd(["mcp2cli"], http_server_cfg, "call", "list-all", "", "", False)
        assert "list-all" in cmd


class TestExecuteServersAction:
    @pytest.mark.asyncio
    async def test_lists_servers(self, tmp_path, sample_servers, monkeypatch):
        mod = _import_tool()
        usr_dir = tmp_path / "usr"
        usr_dir.mkdir()
        sf = usr_dir / "settings.json"
        sf.write_text(json.dumps({"mcp_servers": {"mcpServers": sample_servers}}))
        monkeypatch.setattr(mod, "_A0_ROOT", str(tmp_path))
        tool = mod.Mcp2cli()
        r = await tool.execute()
        assert "test-http" in r.message
        assert "test-stdio" in r.message
    @pytest.mark.asyncio
    async def test_disabled_status(self, tmp_path, sample_servers, monkeypatch):
        mod = _import_tool()
        usr_dir = tmp_path / "usr"
        usr_dir.mkdir()
        sf = usr_dir / "settings.json"
        sf.write_text(json.dumps({"mcp_servers": {"mcpServers": sample_servers}}))
        monkeypatch.setattr(mod, "_A0_ROOT", str(tmp_path))
        r = await mod.Mcp2cli().execute()
        assert "disabled" in r.message
        assert "enabled" in r.message
    @pytest.mark.asyncio
    async def test_http_and_stdio_labels(self, tmp_path, sample_servers, monkeypatch):
        mod = _import_tool()
        usr_dir = tmp_path / "usr"
        usr_dir.mkdir()
        sf = usr_dir / "settings.json"
        sf.write_text(json.dumps({"mcp_servers": {"mcpServers": sample_servers}}))
        monkeypatch.setattr(mod, "_A0_ROOT", str(tmp_path))
        r = await mod.Mcp2cli().execute()
        assert "HTTP" in r.message
        assert "stdio" in r.message
    @pytest.mark.asyncio
    async def test_no_servers(self, tmp_path, monkeypatch):
        mod = _import_tool()
        usr_dir = tmp_path / "usr"
        usr_dir.mkdir()
        sf = usr_dir / "settings.json"
        sf.write_text("{}")
        monkeypatch.setattr(mod, "_A0_ROOT", str(tmp_path))
        r = await mod.Mcp2cli().execute()
        assert "No MCP servers" in r.message


class TestExecuteServerResolution:
    @pytest.mark.asyncio
    async def test_adhoc_url(self, monkeypatch):
        mod = _import_tool()
        mp = MagicMock()
        mp.communicate = AsyncMock(return_value=(b'tools', b''))
        mp.returncode = 0
        monkeypatch.setattr("shutil.which", lambda c: "/usr/bin/" + c)
        monkeypatch.setattr(asyncio, "create_subprocess_exec", AsyncMock(return_value=mp))
        r = await mod.Mcp2cli().execute(mcp_url="https://x.com/mcp", action="list")
        assert "tools" in r.message

    @pytest.mark.asyncio
    async def test_adhoc_stdio(self, monkeypatch):
        mod = _import_tool()
        mp = MagicMock()
        mp.communicate = AsyncMock(return_value=(b'tx', b''))
        mp.returncode = 0
        monkeypatch.setattr("shutil.which", lambda c: "/usr/bin/" + c)
        monkeypatch.setattr(asyncio, "create_subprocess_exec", AsyncMock(return_value=mp))
        r = await mod.Mcp2cli().execute(mcp_stdio="npx s", mcp_env="K=V", action="list")
        assert "tx" in r.message

    @pytest.mark.asyncio
    async def test_unknown_server(self, tmp_path, monkeypatch):
        mod = _import_tool()
        usr_dir = tmp_path / "usr"
        usr_dir.mkdir()
        sf = usr_dir / "settings.json"
        sf.write_text(json.dumps({"mcp_servers": {"mcpServers": {"a": {"url": "http://x"}}}}))
        monkeypatch.setattr(mod, "_A0_ROOT", str(tmp_path))
        r = await mod.Mcp2cli().execute(server="missing", action="list")
        assert "not found" in r.message

    @pytest.mark.asyncio
    async def test_no_source_shows_no_servers(self, tmp_path, monkeypatch):
        mod = _import_tool()
        usr_dir = tmp_path / "usr"
        usr_dir.mkdir()
        sf = usr_dir / "settings.json"
        sf.write_text("{}")
        monkeypatch.setattr(mod, "_A0_ROOT", str(tmp_path))
        # action=list with no sources falls into servers listing block
        r = await mod.Mcp2cli().execute(action="list")
        assert "No MCP servers" in r.message


class TestExecuteSubprocess:
    @pytest.mark.asyncio
    async def test_success(self, monkeypatch):
        mod = _import_tool()
        mp = MagicMock()
        mp.communicate = AsyncMock(return_value=(b'ok', b''))
        mp.returncode = 0
        monkeypatch.setattr("shutil.which", lambda c: "/usr/bin/" + c)
        monkeypatch.setattr(asyncio, "create_subprocess_exec", AsyncMock(return_value=mp))
        r = await mod.Mcp2cli().execute(mcp_url="http://x", action="list")
        assert "ok" in r.message

    @pytest.mark.asyncio
    async def test_nonzero_exit(self, monkeypatch):
        mod = _import_tool()
        mp = MagicMock()
        mp.communicate = AsyncMock(return_value=(b'out', b'err'))
        mp.returncode = 1
        monkeypatch.setattr("shutil.which", lambda c: "/usr/bin/" + c)
        monkeypatch.setattr(asyncio, "create_subprocess_exec", AsyncMock(return_value=mp))
        r = await mod.Mcp2cli().execute(mcp_url="http://x", action="list")
        assert "exited 1" in r.message
        assert "err" in r.message

    @pytest.mark.asyncio
    async def test_timeout(self, monkeypatch):
        mod = _import_tool()
        mp = MagicMock()
        mp.communicate = AsyncMock(side_effect=asyncio.TimeoutError)
        mp.kill = MagicMock()
        monkeypatch.setattr("shutil.which", lambda c: "/usr/bin/" + c)
        monkeypatch.setattr(asyncio, "create_subprocess_exec", AsyncMock(return_value=mp))
        r = await mod.Mcp2cli().execute(mcp_url="http://x", action="list")
        assert "timed out" in r.message
        mp.kill.assert_called_once()

    @pytest.mark.asyncio
    async def test_binary_missing(self, monkeypatch):
        mod = _import_tool()
        monkeypatch.setattr("shutil.which", lambda c: None)
        r = await mod.Mcp2cli().execute(mcp_url="http://x", action="list")
        assert "not found" in r.message

    @pytest.mark.asyncio
    async def test_stderr_appended(self, monkeypatch):
        mod = _import_tool()
        mp = MagicMock()
        mp.communicate = AsyncMock(return_value=(b'out', b'info'))
        mp.returncode = 0
        monkeypatch.setattr("shutil.which", lambda c: "/usr/bin/" + c)
        monkeypatch.setattr(asyncio, "create_subprocess_exec", AsyncMock(return_value=mp))
        r = await mod.Mcp2cli().execute(mcp_url="http://x", action="list")
        assert "out" in r.message
        assert "info" in r.message

    @pytest.mark.asyncio
    async def test_empty_stdout(self, monkeypatch):
        mod = _import_tool()
        mp = MagicMock()
        mp.communicate = AsyncMock(return_value=(b'', b''))
        mp.returncode = 0
        monkeypatch.setattr("shutil.which", lambda c: "/usr/bin/" + c)
        monkeypatch.setattr(asyncio, "create_subprocess_exec", AsyncMock(return_value=mp))
        r = await mod.Mcp2cli().execute(mcp_url="http://x", action="list")
        assert "no output" in r.message

    @pytest.mark.asyncio
    async def test_toon_passed_through(self, monkeypatch):
        mod = _import_tool()
        mp = MagicMock()
        mp.communicate = AsyncMock(return_value=(b'd', b''))
        mp.returncode = 0
        monkeypatch.setattr("shutil.which", lambda c: "/usr/bin/" + c)
        ms = AsyncMock(return_value=mp)
        monkeypatch.setattr(asyncio, "create_subprocess_exec", ms)
        await mod.Mcp2cli().execute(mcp_url="http://x", action="list", toon="true")
        assert "--toon" in ms.call_args[0]

    @pytest.mark.asyncio
    async def test_build_error(self, monkeypatch):
        mod = _import_tool()
        monkeypatch.setattr("shutil.which", lambda c: "/usr/bin/" + c)
        r = await mod.Mcp2cli().execute(mcp_url="http://x", action="invalid")
        assert "Command build error" in r.message

    @pytest.mark.asyncio
    async def test_spawn_error(self, monkeypatch):
        mod = _import_tool()
        monkeypatch.setattr("shutil.which", lambda c: "/usr/bin/" + c)
        monkeypatch.setattr(asyncio, "create_subprocess_exec", AsyncMock(side_effect=OSError("fail")))
        r = await mod.Mcp2cli().execute(mcp_url="http://x", action="list")
        assert "Execution error" in r.message

    @pytest.mark.asyncio
    async def test_log_updated(self, monkeypatch):
        mod = _import_tool()
        mp = MagicMock()
        mp.communicate = AsyncMock(return_value=(b'd', b''))
        mp.returncode = 0
        monkeypatch.setattr("shutil.which", lambda c: "/usr/bin/" + c)
        monkeypatch.setattr(asyncio, "create_subprocess_exec", AsyncMock(return_value=mp))
        t = mod.Mcp2cli()
        await t.execute(mcp_url="http://x", action="list")
        t.log.update.assert_called()
        t.add_progress.assert_called_once()
