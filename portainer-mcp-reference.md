# Portainer MCP — Ad-Hoc Connection Reference

## Working Configuration (Option A)

Use ad-hoc stdio mode with `mcp_env` to pass credentials:

```json
{
  "tool_name": "mcp2cli",
  "tool_args": {
    "mcp_stdio": "/usr/local/bin/portainer-mcp-wrapper.sh",
    "mcp_env": "PORTAINER_SERVER_URL=<YOUR_PORTAINER_SERVER>:9443,PORTAINER_ACCESS_TOKEN=<YOUR_PORTAINER_ACCESS_TOKEN>",
    "action": "list"
  }
}
```

## Why Ad-Hoc Instead of Configured Server

- A0 secret-alias values in settings.json args/env are NOT resolved by mcp2cli's subprocess
- A0 secret-alias values ARE resolved when passed through the Agent Zero `mcp_env` parameter
- The wrapper script (`/usr/local/bin/portainer-mcp-wrapper.sh`) reads env vars and passes them as `-server`/`-token` flags

## Setup Details

| Item | Value |
|------|-------|
| Binary | `/usr/local/bin/portainer-mcp` v0.7.0 |
| Wrapper | `/usr/local/bin/portainer-mcp-wrapper.sh` |
| Server | `<YOUR_PORTAINER_SERVER>:9443` (no `https://` prefix!) |
| Secret | `PORTAINER_ACCESS_TOKEN` (admin API token) |
| Version check | Disabled (`-disable-version-check`) — Portainer 2.33.6 > supported 2.31.2 |

## Common Calls

### List environments
```json
{
  "mcp_stdio": "/usr/local/bin/portainer-mcp-wrapper.sh",
  "mcp_env": "PORTAINER_SERVER_URL=<YOUR_PORTAINER_SERVER>:9443,PORTAINER_ACCESS_TOKEN=<YOUR_PORTAINER_ACCESS_TOKEN>",
  "action": "call",
  "tool_name": "list-environments",
  "params": "{}"
}
```

### List stacks
```json
{
  "mcp_stdio": "/usr/local/bin/portainer-mcp-wrapper.sh",
  "mcp_env": "PORTAINER_SERVER_URL=<YOUR_PORTAINER_SERVER>:9443,PORTAINER_ACCESS_TOKEN=<YOUR_PORTAINER_ACCESS_TOKEN>",
  "action": "call",
  "tool_name": "list-stacks",
  "params": "{}"
}
```

### List local stacks
```json
{
  "mcp_stdio": "/usr/local/bin/portainer-mcp-wrapper.sh",
  "mcp_env": "PORTAINER_SERVER_URL=<YOUR_PORTAINER_SERVER>:9443,PORTAINER_ACCESS_TOKEN=<YOUR_PORTAINER_ACCESS_TOKEN>",
  "action": "call",
  "tool_name": "list-local-stacks",
  "params": "{}"
}
```

## Available Tool Categories (39 tools)

| Category | Example Tools |
|----------|--------------|
| Environments | list-environments, update-environment-tags |
| Stacks | list-stacks, create-stack, update-stack, list-local-stacks |
| Access Groups | list-access-groups, create-access-group |
| Teams | list-teams, create-team, update-team-members |
| Users | list-users, update-user-role |
| Settings | get-settings |
| Docker Proxy | docker-proxy |
| K8s Proxy | kubernetes-proxy, get-kubernetes-resource-stripped |
