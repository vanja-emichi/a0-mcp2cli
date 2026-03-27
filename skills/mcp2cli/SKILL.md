---
name: "mcp2cli"
description: "Token-efficient CLI bridge to any MCP server configured in Agent Zero. Use this skill when you need to discover or call tools on a MCP server (GTM, deep-wiki, or any other) without loading all tool schemas into context. Saves 96-99% of tokens compared to native MCP injection. Triggers: mcp2cli, call mcp, gtm tool, list mcp tools, use mcp server, mcp bridge, deepwiki mcp, gtm containers, gtm tags."
version: "1.0.0"
author: "Agent Zero"
tags: ["mcp", "gtm", "tools", "token-efficiency", "integration"]
trigger_patterns:
  - "mcp2cli"
  - "call mcp"
  - "list mcp tools"
  - "use mcp server"
  - "gtm tool"
  - "gtm containers"
  - "gtm tags"
  - "deepwiki mcp"
  - "mcp bridge"
---

# MCP2CLI — Agent Zero Tool

The `mcp2cli` plugin provides a **token-efficient bridge** to any MCP server. Instead of injecting all tool schemas into the LLM context on every turn, call individual tools on demand through this tool.

> **Token savings**: 96–99% fewer tokens vs native MCP schema injection.

## When to Use

- You need to interact with a configured MCP server (GTM, deep-wiki, etc.)
- You want to discover what tools are available on an MCP server
- You want to call a specific MCP tool without loading all schemas into context
- You need to connect to an ad-hoc MCP server not pre-configured in settings

## Core Workflow

Always follow this 4-step discovery pattern:

```
1. (no args)         → see all configured servers
2. action=list       → discover tools on a server
3. action=help       → inspect parameters of a specific tool
4. action=call       → execute the tool with params
```

## Tool Arguments

| Argument | Type | Description |
|---|---|---|
| `server` | string | Name of a configured server (e.g. `gtm`, `deep-wiki`) |
| `action` | string | `servers` \| `list` \| `search` \| `help` \| `call` |
| `tool_name` | string | Tool to inspect or call (for `help` / `call`) |
| `params` | string | JSON object `{"key": "val"}` or CLI flags `--key val` |
| `search_query` | string | Keyword to filter tools (for `search`) |
| `mcp_url` | string | Ad-hoc HTTP/SSE MCP server URL |
| `mcp_stdio` | string | Ad-hoc stdio command e.g. `npx some-mcp-server` |
| `mcp_env` | string | Comma-separated env vars for stdio: `KEY=val,KEY2=val2` |
| `toon` | string | `true` for TOON output (40-60% fewer tokens on large lists) |

---

## Step 1 — See Configured Servers

Call with no arguments to see all MCP servers configured in Agent Zero settings:

```json
{
    "tool_name": "mcp2cli",
    "tool_args": {}
}
```

This shows each server's name, status (enabled/disabled), and connection type.

---

## Step 2 — List Available Tools

### On a configured server
```json
{
    "tool_name": "mcp2cli",
    "tool_args": {
        "server": "gtm",
        "action": "list"
    }
}
```

### On a disabled/ad-hoc HTTP server
```json
{
    "tool_name": "mcp2cli",
    "tool_args": {
        "mcp_url": "https://mcp.deepwiki.com/mcp",
        "action": "list"
    }
}
```

### On an ad-hoc stdio server
```json
{
    "tool_name": "mcp2cli",
    "tool_args": {
        "mcp_stdio": "npx some-mcp-server",
        "mcp_env": "API_KEY=sk-abc,DEBUG=1",
        "action": "list"
    }
}
```

### Search instead of listing everything
```json
{
    "tool_name": "mcp2cli",
    "tool_args": {
        "server": "gtm",
        "action": "search",
        "search_query": "tag"
    }
}
```

---

## Step 3 — Inspect a Tool's Parameters

Before calling, always check exact required parameters from the tool itself:

```json
{
    "tool_name": "mcp2cli",
    "tool_args": {
        "server": "YOUR_SERVER",
        "action": "help",
        "tool_name": "TOOL_NAME_FROM_LIST"
    }
}
```

---

## Step 4 — Call a Tool

### With JSON params (preferred)
```json
{
    "tool_name": "mcp2cli",
    "tool_args": {
        "server": "YOUR_SERVER",
        "action": "call",
        "tool_name": "TOOL_NAME_FROM_LIST",
        "params": "{\"param_from_help\": \"value\"}"
    }
}
```

### With CLI-style params
```json
{
    "tool_name": "mcp2cli",
    "tool_args": {
        "server": "YOUR_SERVER",
        "action": "call",
        "tool_name": "TOOL_NAME_FROM_LIST",
        "params": "--param-from-help value"
    }
}
```

### With TOON output (token-efficient for large results)
```json
{
    "tool_name": "mcp2cli",
    "tool_args": {
        "server": "YOUR_SERVER",
        "action": "call",
        "tool_name": "TOOL_NAME_FROM_LIST",
        "params": "{\"param_from_help\": \"value\"}",
        "toon": "true"
    }
}
```


---

## Server-Specific Reference (Known Tool Names)

> ⚠️ **These are reference notes only.** Always use `action=list` and `action=help` to discover current tool names and params — never call tools based on examples alone. Tool names and parameters can change between server versions.

### GTM known tool categories (use `--search` to find current names)

| Category | Search term | Example known tools (verify with list first) |
|---|---|---|
| Accounts | `account` | `list-gtm-accounts`, `get-gtm-account` |
| Containers | `container` | `list-gtm-containers`, `get-gtm-container` |
| Tags | `tag` | `list-gtm-tags`, `get-gtm-tag`, `create-gtm-tag` |
| Triggers | `trigger` | `list-gtm-triggers`, `create-gtm-trigger` |
| Variables | `variable` | `list-gtm-variables`, `create-gtm-variable` |
| Workspaces | `workspace` | `list-gtm-workspaces`, `get-gtm-workspace` |
| Versions | `version` | `list-gtm-versions`, `publish-gtm-version` |

### Correct GTM workflow (always follow this order)

```
1. Search for tools in the category you need:
   action=search, search_query="account"

2. Inspect parameters before calling:
   action=help, tool_name="<name from search results>"

3. Call with exact params from help output:
   action=call, tool_name="<verified name>", params="{...}"
```


## Any MCP Server — Discovery-First Workflow

> ⚠️ **Never hardcode tool names or parameter names from examples.** Tool names and params vary per server and can change. Always discover first.

### Step 1 — List tools on any server
```json
{
    "tool_name": "mcp2cli",
    "tool_args": {
        "server": "deep-wiki",
        "action": "list"
    }
}
```

### Step 2 — Inspect parameters of the tool you want
```json
{
    "tool_name": "mcp2cli",
    "tool_args": {
        "server": "deep-wiki",
        "action": "help",
        "tool_name": "TOOL_NAME_FROM_LIST"
    }
}
```

### Step 3 — Call with exact params from help output
```json
{
    "tool_name": "mcp2cli",
    "tool_args": {
        "server": "deep-wiki",
        "action": "call",
        "tool_name": "TOOL_NAME_FROM_LIST",
        "params": "{\"param_name_from_help\": \"value\"}"
    }
}
```

This pattern works identically for **any** configured server — `gtm`, `deep-wiki`, or any ad-hoc URL.

---

## Best Practices

### ✅ Do
- **Always discover first**: use `list` or `search` before calling unknown tools
- **Use `help`** to check required parameters before calling
- **Use `toon: true`** for large list responses to save tokens
- **Use JSON params** `{"key": "value"}` for clarity over CLI-style flags
- **Reference servers by name** from settings when possible (`server: gtm`)

### ❌ Don't
- Don't guess tool names — always `list` or `search` first
- Don't pass credentials as literal values in `params` — they are already in the server's env config
- Don't call `action=servers` repeatedly — do it once to orient yourself

---

## Configured Servers Reference

| Server name | Type | Notes |
|---|---|---|
| `gtm` | stdio (`npx gtm-mcp`) | Google Tag Manager — disabled in native MCP, use mcp2cli |
| `deep-wiki` | HTTP (`https://mcp.deepwiki.com/mcp`) | GitHub repo analysis — disabled in native MCP, use mcp2cli |

> ℹ️ Credentials for GTM (`GTM_CREDENTIALS_FILE`, `GTM_TOKEN_FILE`) are automatically passed via env — no need to include them in params.

---

## Token Savings Reference

| Approach | Tokens/turn | Notes |
|---|---|---|
| Native MCP (all schemas) | 5,000–20,000 | Schemas loaded every turn |
| mcp2cli (on-demand) | 100–300 | Only result of one call |
| mcp2cli + `--toon` | 60–180 | TOON encoding for large arrays |
