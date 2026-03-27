"""mcp2cli Tool — token-efficient CLI bridge to any MCP server.

Reads MCP server configurations from Agent Zero settings and lets agents
discover and call tools on any configured MCP server without loading all
tool schemas into LLM context. Saves 96-99% tokens vs native MCP injection.
"""
import os
import json
import shlex
import asyncio
import shutil

_PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_A0_ROOT = os.path.abspath(os.path.join(_PLUGIN_ROOT, "..", "..", ".."))

from helpers.tool import Tool, Response


def _get_mcp2cli_bin() -> list:
    """Return argv prefix for mcp2cli, preferring installed binary over uvx."""
    if shutil.which("mcp2cli"):
        return ["mcp2cli"]
    if shutil.which("uvx"):
        return ["uvx", "mcp2cli"]
    raise RuntimeError(
        "mcp2cli not found. Run plugin Initialize or: pip install mcp2cli"
    )


def _load_mcp_servers() -> dict:
    """Load mcpServers dict from Agent Zero usr/settings.json."""
    try:
        settings_path = os.path.join(_A0_ROOT, "usr", "settings.json")
        with open(settings_path) as f:
            raw = json.load(f)
        mcp_raw = raw.get("mcp_servers", {})
        if isinstance(mcp_raw, str):
            mcp_raw = json.loads(mcp_raw)
        return mcp_raw.get("mcpServers", {})
    except Exception:
        return {}


def _build_cmd(bin_argv: list, server_cfg: dict, action: str,
               tool_name: str, params: str, search_query: str,
               toon: bool) -> list:
    """Build the full mcp2cli command list."""
    cmd = list(bin_argv)

    # --- Connection flags ---
    if "url" in server_cfg:
        cmd += ["--mcp", server_cfg["url"]]
        transport = server_cfg.get("type", "")
        if transport == "streamable-http":
            cmd += ["--transport", "streamable"]
        elif transport == "sse":
            cmd += ["--transport", "sse"]
    elif "command" in server_cfg:
        parts = [server_cfg["command"]] + server_cfg.get("args", [])
        stdio_cmd = " ".join(shlex.quote(p) for p in parts)
        cmd += ["--mcp-stdio", stdio_cmd]
        for k, v in server_cfg.get("env", {}).items():
            cmd += ["--env", f"{k}={v}"]
    else:
        raise ValueError("server_cfg must have 'url' or 'command'")

    # --- Output flags (global — must come before subcommand) ---
    if toon:
        cmd.append("--toon")
    elif action in ("list", "call", "search"):
        cmd.append("--pretty")

    # --- Action ---
    if action == "list":
        cmd.append("--list")
    elif action == "search":
        if not search_query:
            raise ValueError("search_query is required for action=search")
        cmd += ["--search", search_query]
    elif action == "help":
        if not tool_name:
            raise ValueError("tool_name is required for action=help")
        cmd += [tool_name, "--help"]
    elif action == "call":
        if not tool_name:
            raise ValueError("tool_name is required for action=call")
        cmd.append(tool_name)
        if params:
            # Accept JSON object or bare --flag value string
            try:
                args_dict = json.loads(params)
                for k, v in args_dict.items():
                    flag = "--" + k.replace("_", "-")
                    cmd += [flag, str(v)]
            except (json.JSONDecodeError, AttributeError):
                cmd += shlex.split(params)
    else:
        raise ValueError(f"Unknown action '{action}'. Use: list, search, help, call, servers")


    return cmd


class Mcp2cli(Tool):

    async def execute(
        self,
        server: str = "",
        action: str = "servers",
        tool_name: str = "",
        params: str = "",
        search_query: str = "",
        mcp_url: str = "",
        mcp_stdio: str = "",
        mcp_env: str = "",
        toon: str = "false",
        **kwargs,
    ):
        use_toon = str(toon).lower().strip() == "true"

        # ── Action: list configured servers ──────────────────────────────────
        if action == "servers" or (
            not server and not mcp_url and not mcp_stdio
        ):
            servers = _load_mcp_servers()
            if not servers:
                return Response(
                    message="No MCP servers configured in usr/settings.json.",
                    break_loop=False,
                )
            lines = ["**Configured MCP Servers:**\n"]
            for name, cfg in servers.items():
                disabled = cfg.get("disabled", False)
                status = "🔴 disabled" if disabled else "🟢 enabled"
                if "url" in cfg:
                    conn = f"HTTP — `{cfg['url']}`  (type: {cfg.get('type', 'auto')})"
                else:
                    cmd_str = cfg.get("command", "") + " " + " ".join(cfg.get("args", []))
                    conn = f"stdio — `{cmd_str.strip()}`"
                desc = cfg.get("description", "")
                lines.append(
                    f"- **{name}** ({status}) — {conn}"
                    + (f"\n  > {desc}" if desc else "")
                )
            lines.append(
                "\nUse `action=list` with a `server` name to discover its tools."
            )
            return Response(message="\n".join(lines), break_loop=False)

        # ── Resolve server config ─────────────────────────────────────────────
        if mcp_url:
            server_cfg: dict = {"url": mcp_url}
        elif mcp_stdio:
            parts = shlex.split(mcp_stdio)
            env_dict: dict = {}
            if mcp_env:
                for pair in mcp_env.split(","):
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        env_dict[k.strip()] = v.strip()
            server_cfg = {"command": parts[0], "args": parts[1:], "env": env_dict}
        elif server:
            servers = _load_mcp_servers()
            if server not in servers:
                avail = ", ".join(servers.keys()) if servers else "none"
                return Response(
                    message=f"Server '{server}' not found. Available: {avail}",
                    break_loop=False,
                )
            server_cfg = servers[server]
        else:
            return Response(
                message="Provide 'server' (configured name), 'mcp_url', or 'mcp_stdio'.",
                break_loop=False,
            )

        # ── Get binary ────────────────────────────────────────────────────────
        try:
            bin_argv = _get_mcp2cli_bin()
        except RuntimeError as e:
            return Response(message=str(e), break_loop=False)

        # ── Build command ─────────────────────────────────────────────────────
        try:
            cmd = _build_cmd(
                bin_argv=bin_argv,
                server_cfg=server_cfg,
                action=action,
                tool_name=tool_name,
                params=str(params) if not isinstance(params, str) else params,
                search_query=search_query,
                toon=use_toon,
            )
        except (ValueError, Exception) as e:
            return Response(message=f"Command build error: {e}", break_loop=False)

        display_cmd = " ".join(shlex.quote(c) for c in cmd)
        self.log.update(heading=f"mcp2cli {action}" + (f": {tool_name}" if tool_name else ""))
        self.add_progress(f"$ {display_cmd}")

        # ── Execute ───────────────────────────────────────────────────────────
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=90
                )
            except asyncio.TimeoutError:
                proc.kill()
                return Response(
                    message="mcp2cli timed out after 90 seconds.", break_loop=False
                )
        except Exception as e:
            return Response(message=f"Execution error: {e}", break_loop=False)

        out = stdout.decode("utf-8", errors="replace").strip()
        err = stderr.decode("utf-8", errors="replace").strip()

        if proc.returncode != 0:
            msg = f"mcp2cli exited {proc.returncode}"
            if err:
                msg += f"\n\nSTDERR:\n{err}"
            if out:
                msg += f"\n\nSTDOUT:\n{out}"
            return Response(message=msg, break_loop=False)

        result = out or "(no output)"
        if err:
            # mcp2cli sometimes writes informational text to stderr
            result += f"\n\n[stderr]:\n{err}"

        self.log.update(result=result[:800])
        return Response(message=result, break_loop=False)
