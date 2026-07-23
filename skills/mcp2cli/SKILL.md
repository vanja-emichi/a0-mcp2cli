---
name: "mcp2cli"
description: "Token-efficient CLI bridge to any MCP server. Use this skill when you need to discover or call tools on an MCP server without loading all tool schemas into context. Triggers: mcp2cli, call mcp, list mcp tools, use mcp server, mcp bridge."
version: "2.0.0"
author: "Agent Zero"
tags: ["mcp", "tools", "token-efficiency", "integration"]
trigger_patterns:
  - "mcp2cli"
  - "call mcp"
  - "list mcp tools"
  - "use mcp server"
  - "mcp bridge"
---

# MCP2CLI — via code_execution_tool

The `mcp2cli` CLI binary bridges to any MCP server. Instead of injecting all tool schemas into context every turn, you run commands on demand through `code_execution_tool` (runtime=terminal). The binary is cached after first `uvx` use.

## Step 0 — Discover configured servers

Always start by listing configured servers to get the exact connection command with credentials already resolved:

```bash
python /a0/usr/plugins/mcp2cli/helpers/mcp_servers.py
```

For a single server's command:

```bash
python /a0/usr/plugins/mcp2cli/helpers/mcp_servers.py <server-name>
```

This prints the full `uvx mcp2cli <connection-flags>` prefix — **copy it exactly**, credentials are embedded.

## Step 1 — List or search tools

Append `--list` (or `--compact` for space-separated names only, ~2 tokens/tool):

```bash
uvx mcp2cli <connection-flags> --compact --list
```

Search instead of listing everything:

```bash
uvx mcp2cli <connection-flags> --search "tag"
```

## Step 2 — Inspect a tool's parameters

```bash
uvx mcp2cli <connection-flags> <tool-name> --help
```

## Step 3 — Call a tool

With CLI flags (simple args):

```bash
uvx mcp2cli <connection-flags> <tool-name> --param-name value
```

With JSON via stdin (complex args):

```bash
uvx mcp2cli <connection-flags> <tool-name> --stdin <<'EOF'
{"paramName": "value"}
EOF
```

## Complete example via code_execution_tool

~~~json
{
    "thoughts": ["I need to see which MCP servers are configured"],
    "headline": "Listing configured MCP servers",
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "terminal",
        "code": "python /a0/usr/plugins/mcp2cli/helpers/mcp_servers.py"
    }
}
~~~

Then copy the printed command to list, inspect, and call tools via `code_execution_tool`.

> Credentials are resolved by the helper script — never include them manually. Use `--compact` for large tool lists to save tokens.
