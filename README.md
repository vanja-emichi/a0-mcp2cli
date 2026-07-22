# MCP2CLI — Agent Zero Plugin

Token-efficient bridge to any MCP server. Instead of injecting all MCP tool schemas into every LLM turn, agents discover and call tools **on demand** via `code_execution_tool` + the `mcp2cli` CLI binary — saving **96–99% of tokens** compared to native MCP injection.

---

## How It Works

1. **System prompt extensions** suppress native MCP schema injection (cli mode) and strip the dot-prefixed routing line, redirecting the agent to mcp2cli.
2. **A skill** teaches the agent to run `uvx mcp2cli` commands via the standard `code_execution_tool`.
3. **A helper script** (`helpers/mcp_servers.py`) resolves configured server connection strings with credentials so the agent never handles secrets directly.

No dedicated tool class — the agent uses `code_execution_tool` (runtime=terminal) for everything.

---

## Setup

1. Enable **MCP2CLI** in Agent Zero → Settings → Agent tab.
2. Click **Initialize** to verify `mcp2cli` availability (falls back to `uvx` automatically).
3. Set mode to `cli` in the plugin config to suppress native MCP schema injection.

The `mcp2cli` binary is the upstream [knowsuchagency/mcp2cli](https://github.com/knowsuchagency/mcp2cli) (PyPI, v3.3.1), run via `uvx`.

---

## Modes

| Mode | Behavior |
|---|---|
| `default` | Native MCP schemas injected as usual (no change from stock Agent Zero) |
| `cli` | Native injection suppressed; agent uses `code_execution_tool` + `mcp2cli` CLI on demand |

Switch via the plugin config dropdown (per-project and per-agent supported).

---

## Files

| Path | Purpose |
|---|---|
| `skills/mcp2cli/SKILL.md` | Teaches the agent the discover → help → call workflow via `code_execution_tool` |
| `helpers/mcp_servers.py` | Resolves server connection strings with credentials from settings |
| `extensions/.../_12_mcp_prompt/.../end/_10_cli_mode.py` | Suppresses native MCP schema in cli mode |
| `extensions/.../_11_tools_prompt/.../end/_10_strip_mcp_routing.py` | Strips dot-prefixed routing line in cli mode |
| `extensions/python/system_prompt/_30_mcp2cli_skill_hint.py` | Injects "load mcp2cli skill" hint |
| `hooks.py` / `execute.py` | Plugin lifecycle (install/uninstall binary) |

---

## Token Savings

| Approach | Tokens per turn |
|---|---|
| Native MCP (all schemas) | 5,000–20,000 |
| mcp2cli on-demand | 100–300 |
| mcp2cli + `--compact` / `--toon` | 60–180 |
