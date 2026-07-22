"""In cli mode, strip the hardcoded MCP dot-prefixed routing line from the
tools prompt and replace it with an mcp2cli redirect.

The core file agent.system.tools.md always lists 'gtm.*', 'google_analytics_mcp.*',
'deep_wiki.*' as directly-callable tools. In cli mode that contradicts the
mcp2cli discover->help->call workflow. This extension rewrites that line when
cli mode is active, without modifying any core file.
"""
import re

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


# Matches the MCP routing bullet line added during the context-engineering audit.
# Captures from "- **MCP" through the end of that bullet.
_MCP_ROUTING_RE = re.compile(
    r"\n?- \*\*MCP \(remote, dot-prefixed\):\*\*[^\n]*(?:\n(?![-*]\s)[^\n]*)*"
)

_CLI_REPLACEMENT = (
    "\n- **MCP (remote):** discover and call via `mcp2cli` tool "
    "(load skill `mcp2cli` first if not in EXTRAS); "
    "do NOT use dot-prefixed `server.tool` names directly"
)


class StripMcpRoutingInCliMode(Extension):
    async def execute(self, data: dict = None, **kwargs):
        if not self.agent or data is None:
            return
        if not _cli_mode_active(self.agent):
            return
        result = data.get("result")
        if not isinstance(result, str) or "dot-prefixed" not in result:
            return
        data["result"] = _MCP_ROUTING_RE.sub(_CLI_REPLACEMENT, result, count=1)
