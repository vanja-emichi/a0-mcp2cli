"""Suppress native MCP schema injection when mcp2cli is in cli mode.

Hooks the @extensible build_prompt /end extension point. When mcp_mode=cli, rewrite
the rendered MCP prompt to "" so no schemas enter the system prompt; agents
discover and call MCP tools on demand via the mcp2cli tool instead.
"""
from helpers.extension import Extension


def _cli_mode_active(agent) -> bool:
    if not agent:
        return False
    try:
        from helpers import plugins

        if "_mcp2cli" not in plugins.get_enabled_plugins(agent):
            return False
        cfg = plugins.get_plugin_config("_mcp2cli", agent=agent) or {}
        return str(cfg.get("mcp_mode", "cli")).lower() == "cli"
    except Exception:
        return False


class SuppressInCliMode(Extension):
    async def execute(self, data: dict = None, **kwargs):
        if not self.agent or data is None:
            return
        if _cli_mode_active(self.agent) and data.get("result"):
            data["result"] = ""
