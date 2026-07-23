---
topic: MCP Server-Level Tools — one tool per server, subtools dispatched inside
status: active
updated: 2026-07-23
---

# PLAN — MCP Server-Level Tools

## Problem

Native MCP renders every server tool as its own `server.tool` entry with full
input schema — 5,000–20,000 tok/turn and up to 136 native function definitions
(400s on models capped at ~20 tools). The mcp2cli plugin patches this by
blanking the prompt and routing through `code_execution_tool` + a CLI — token
win, but ergonomic debt: no first-class dispatch/logging, agents must learn a
skill, `uvx` dependency in the exec runtime.

## Design

New mode `mcp_serve_tools: server` (core setting, not plugin-owned):

- **One `MCPServerTool` per server** — tool name = normalized server name
  (`gtm`, `deepwiki`). Args: `subtool` (str) + `tool_args` (dict). Dispatches
  through existing `server.call_tool(subtool, tool_args)` — all transport,
  media, artifact, and error handling already lives there.
- **Prompt** — one compact entry per server: name, description, subtool names
  as a comma list (no schemas), single shared Usage template. Agent learns
  schemas on demand: calling with `subtool=""` (or unknown) returns a
  validation error listing valid subtools — self-correcting discovery loop,
  same pattern the framework already uses for tool errors.
- **Native function tools** — `_mcp_tools()` in `helpers/responses_tools.py`
  returns one schema per server (subtool: string, tool_args: object) instead of
  N×M. 136 → ~3 definitions. Capped models stay under limit without any
  plugin capability flag.
- **Modes**: `native` (today's default, unchanged), `server` (new), plus
  plugin `suppress` capability stays as escape hatch. Dispatch in `agent.py`
  stays untouched: `has_tool`/`get_tool` route by exact name — server mode
  registers names = server names.

## Changes (core, small labeled commits per CAP-4 contract)

1. `helpers/mcp_handler.py`
   - `MCPServerTool(Tool)` class — wraps server, executes subtool dispatch.
   - `MCPConfig.get_server_tools_prompt()` — compact prompt renderer.
   - `MCPConfig.has_tool/get_tool` — in server mode, match server names,
     return `MCPServerTool`.
2. `helpers/responses_tools.py` — `_mcp_tools()` emits per-server schemas in
   server mode.
3. `extensions/python/system_prompt/_12_mcp_prompt.py` — picks renderer by mode.
4. Setting: `mcp_serve_tools` in settings (default `native`).

## Verification (3-tier, same discipline as context-optimization)

- **Tier 1 (pytest, deterministic):** server mode → prompt contains one entry
  per server, zero `Input schema` blocks, tools-section budget holds; native
  function tools count == #servers + #local; `has_tool("gtm")` true,
  `has_tool("gtm.create_variable")` false in server mode.
- **Tier 2 (live agent):** EVAL — "list the gtm workspaces" → agent calls
  `tool_name: gtm`, discovers subtools after the validation error, succeeds
  within 3 turns. Repeat with deepwiki.
- **Tier 3 (token measurement):** `tmp/analyze_tools_context.py` before/after;
  target: MCP section < 400 tok with gtm + deepwiki + google-analytics
  configured (vs ~5,000–20,000 native).

## Rollout / retirement

1. Implement + Tier 1 green → 2. Tier 2/3 green on loloi → 3. Switch instance
   to server mode → 4. mcp2cli plugin set to `default`/retired (kept in repo
   for older cores) → 5. DOX updates (root, helpers, plugins, project).
