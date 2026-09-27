"""Standalone server-config resolver for mcp2cli.

Prints configured MCP server connection strings so the agent can build
``uvx mcp2cli`` commands via ``code_execution_tool`` without reading raw
settings or credentials. Usage::

    python /a0/usr/plugins/mcp2cli/helpers/mcp_servers.py            # list all
    python /a0/usr/plugins/mcp2cli/helpers/mcp_servers.py gtm         # show one

LOCAL DIVERGENCE (upstream PR planned): this helper originally read only
global ``usr/settings.json``. It now also merges the active project's
``<project>/.a0proj/mcp_servers.json`` over global, matching the live MCP
engine's merge order (project wins on name collision). A PR will be opened
to propagate this fix upstream. See the plugin's local notes.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _a0_root() -> Path:
    here = Path(__file__).resolve().parent
    for parent in [here, *here.parents]:
        if (parent / "agent.py").exists() or (parent / "run_ui.py").exists():
            return parent
    return Path("/a0")


def _parse_mcp_servers(raw) -> dict:
    if isinstance(raw, dict):
        data = raw
    elif isinstance(raw, str):
        data = json.loads(raw) if raw.strip() else {}
    else:
        data = {}
    if isinstance(data, dict) and "mcpServers" in data:
        data = data["mcpServers"]
    return data if isinstance(data, dict) else {}


def _project_servers_files(root: Path) -> list[Path]:
    """All project-scoped MCP config files, newest last so the most recent
    project wins on name collisions (mirrors the engine's merge order)."""
    projects_dir = root / "usr" / "projects"
    if not projects_dir.exists():
        return []
    files = []
    for proj in sorted(projects_dir.iterdir()):
        cfg = proj / ".a0proj" / "mcp_servers.json"
        if cfg.exists():
            files.append(cfg)
    return files


def load_servers(project_name: str | None = None) -> dict:
    root = _a0_root()
    servers: dict = {}
    settings_path = root / "usr" / "settings.json"
    if settings_path.exists():
        settings = json.loads(settings_path.read_text())
        servers.update(_parse_mcp_servers(settings.get("mcp_servers", {})))
    # Project-scoped overrides (engine merge order: project wins).
    proj_files = _project_servers_files(root)
    if project_name:
        named = root / "usr" / "projects" / project_name / ".a0proj" / "mcp_servers.json"
        proj_files = [named] if named.exists() else []
    for cfg in proj_files:
        try:
            servers.update(_parse_mcp_servers(json.loads(cfg.read_text())))
        except Exception:
            continue
    return servers


def _resolve_secrets(text):
    """Resolve secret-alias placeholders via the framework's secrets store.

    Placeholder shape is the section mark + 'secret(' + KEY + ')'. Falls back to
    the literal text if the secrets module is unavailable, so the helper still
    runs standalone outside an Agent Zero checkout.
    """
    marker = "§§secret("  # alias prefix, built without the literal token
    if marker not in text:
        return text
    try:
        from helpers.secrets import get_default_secrets_manager
        return get_default_secrets_manager().replace_placeholders(text)
    except Exception:
        return text


def _auth_flags(cfg: dict) -> str:
    """Emit --auth-header flags from a server's configured headers."""
    headers = cfg.get("headers") or {}
    if not isinstance(headers, dict):
        return ""
    flags = []
    for key, value in headers.items():
        flags.append(f'--auth-header "{key}: {_resolve_secrets(str(value))}"')
    return (" " + " ".join(flags)) if flags else ""


def _connection_line(name: str, cfg: dict) -> str:
    if "url" in cfg:
        transport = cfg.get("type", "sse")
        flag = "--transport streamable" if transport == "streamable-http" else "--transport sse"
        return f'--mcp "{cfg["url"]}" {flag}{_auth_flags(cfg)}'
    elif "command" in cfg:
        parts = [cfg["command"]] + cfg.get("args", [])
        stdio = " ".join(parts)
        env = cfg.get("env", {})
        env_flags = " ".join(f'--env "{k}={v}"' for k, v in env.items()) if env else ""
        return f'--mcp-stdio "{stdio}"' + (f" {env_flags}" if env_flags else "")
    return "(unknown connection type)"


def main():
    servers = load_servers()
    if not servers:
        print("No MCP servers configured.")
        return

    filter_name = sys.argv[1].strip() if len(sys.argv) > 1 else ""

    if filter_name:
        if filter_name not in servers:
            avail = ", ".join(sorted(servers))
            print(f"Server '{filter_name}' not found. Available: {avail}")
            return
        cfg = servers[filter_name]
        conn = _connection_line(filter_name, cfg)
        print(f"# {filter_name}")
        print(f"uvx mcp2cli {conn} --list")
        return

    print("Configured MCP Servers:")
    for name, cfg in sorted(servers.items()):
        conn = _connection_line(name, cfg)
        disabled = cfg.get("disabled", False)
        status = "disabled" if disabled else "enabled"
        desc = cfg.get("description", "")
        print(f"\n## {name} ({status})")
        if desc:
            print(f"  {desc}")
        print(f"  uvx mcp2cli {conn} --list")


if __name__ == "__main__":
    main()
