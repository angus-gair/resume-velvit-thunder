# MCP Server Integration Guide

This document provides a comprehensive guide to configuring and using MCP (Model Control Protocol) servers with the Resume Velvit Thunder project. MCP servers allow for flexible integration of external model providers and services.

## Table of Contents
- [Overview](#overview)
- [Configuration](#configuration)
  - [Configuration File](#configuration-file)
  - [Environment Variables](#environment-variables)
  - [Provider Integration](#provider-integration)
- [Server Configuration Reference](#server-configuration-reference)
- [Example Configurations](#example-configurations)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Integration with Backup System](#integration-with-backup-system)

## Overview

MCP (Model Control Protocol) servers enable the Resume Velvit Thunder application to interact with various AI model providers through a standardized interface. This allows for:

- Easy switching between different model providers
- Custom model endpoints
- Local model serving
- Advanced configuration options
- Environment-specific overrides

## Configuration

### Configuration File

MCP servers can be configured using a JSON or YAML configuration file. By default, the application looks for `mcp-config.json` in the current working directory, but this can be overridden using the `MCP_CONFIG_FILE` environment variable.

#### Example Configuration (`mcp-config.json`)

```json
{
  "mcpServers": {
    "local_llm": {
      "command": "python -m mcp_server",
      "args": ["--model", "mistral-7b"],
      "env": {
        "MODEL_PATH": "/path/to/models"
      },
      "enabled": true,
      "port": 8000
    },
    "openai_compatible": {
      "command": "docker run -p 8080:8080 openai-compatible-server",
      "enabled": true,
      "port": 8080
    }
  }
}
```

### Environment Variables

MCP server configurations can be overridden or extended using environment variables with the following format:

```
MCP_SERVER_<NAME>_<SETTING>=<VALUE>
```

#### Supported Environment Variables

- `MCP_SERVER_<NAME>_COMMAND`: Command to start the server
- `MCP_SERVER_<NAME>_ARGS`: Space-separated command-line arguments (use quotes for arguments with spaces)
- `MCP_SERVER_<NAME>_ENV_<VAR>`: Environment variables for the server process
- `MCP_SERVER_<NAME>_PORT`: Port number the server listens on
- `MCP_SERVER_<NAME>_ENABLED`: Set to 'true' or 'false' to enable/disable the server

#### Example Environment Variables

```bash
# Configure a local LLM server
MCP_SERVER_LOCAL_LLM_COMMAND="python -m mcp_server"
MCP_SERVER_LOCAL_LLM_ARGS="--model mistral-7b --quantize"
MCP_SERVER_LOCAL_LLM_ENV_MODEL_PATH="/path/to/models"
MCP_SERVER_LOCAL_LLM_PORT=8000
MCP_SERVER_LOCAL_LLM_ENABLED=true

# Override the config file location
MCP_CONFIG_FILE="/path/to/alternative-config.json"
```

### Provider Integration

MCP servers can be referenced in provider configurations using the `mcp_server` field:

```yaml
providers:
  my_custom_provider:
    models: ["model1", "model2"]
    default_model: "model1"
    mcp_server: "local_llm"  # References the MCP server named "local_llm"
```

## Server Configuration Reference

### MCPServerConfig

| Field    | Type           | Required | Default | Description |
|----------|----------------|----------|---------|-------------|
| command  | string         | Yes      | -       | Command to start the MCP server |
| args     | array[string]  | No       | []      | Command-line arguments |
| env      | object         | No       | {}      | Environment variables |
| enabled  | boolean        | No       | true    | Whether the server is enabled |
| port     | integer        | No       | -       | Port number the server listens on |

## Example Configurations

### Local LLM with vLLM

```json
{
  "mcpServers": {
    "vllm": {
      "command": "python -m vllm.entrypoints.openai.api_server",
      "args": [
        "--model", "TheBloke/Mistral-7B-Instruct-v0.1-GPTQ",
        "--quantization", "gptq",
        "--dtype", "float16"
      ],
      "enabled": true,
      "port": 8000
    }
  }
}
```

### OpenAI-Compatible API

```yaml
mcpServers:
  openai_compatible:
    command: "docker run -p 8080:8080 tatsu-lab/stanford_alpaca"
    enabled: true
    port: 8080
```

## Troubleshooting

### Common Issues

1. **Server not starting**
   - Check the logs for error messages
   - Verify the command and arguments are correct
   - Ensure required environment variables are set

2. **Connection refused**
   - Verify the server is running and listening on the specified port
   - Check for firewall rules blocking the connection

3. **Invalid configuration**
   - Check for syntax errors in the configuration file
   - Verify all required fields are present

### Logging

Enable debug logging for more detailed information:

```bash
LOG_LEVEL=DEBUG python your_script.py
```

## Integration with Backup System

The MCP server integration includes support for the backup and version control system, allowing you to store backup metadata in MCP memory banks.

### Configuration

```yaml
# In your backup_config.yaml
mcp_servers:
  memory_bank:
    enabled: true
    server_name: "memory-bank"  # Name of MCP server in mcp-config.json
    collection: "backups"      # Collection to store backup metadata in
```

### Stored Metadata

When MCP integration is enabled, the following metadata is stored:

- Backup timestamps
- File hashes and sizes
- Git state (branch, commit hash)
- Backup locations
- Configuration hashes

### Querying Backup Information

You can query backup information through the MCP server:

```python
# Example: Get all backups
backups = mcp_client.query(server="memory-bank", collection="backups", query={})

# Example: Find backup by date
from datetime import datetime
backup = mcp_client.query_one(
    server="memory-bank",
    collection="backups",
    query={"timestamp": {"$gte": datetime(2025, 6, 1)}}
)
```

## Best Practices

1. **Use environment variables for sensitive data**
   ```yaml
   # config.yaml
   mcpServers:
     my_server:
       env:
         API_KEY: ${MY_API_KEY}  # Will be expanded from environment
   ```

2. **Provide default values**
   ```yaml
   # config.yaml
   mcpServers:
     my_server:
       port: ${MY_SERVER_PORT:-8000}  # Default to 8000 if not set
   ```

3. **Document your configurations**
   - Include comments in configuration files
   - Document required environment variables
   - Provide example configurations

4. **Test configurations locally** before deploying to production

5. **Use version control** for configuration files, but be careful with sensitive data

6. **Monitor server health** and set up alerts for failures

7. **Regularly backup MCP server data**
   - Include MCP server data in your backup strategy
   - Test restoration of MCP server data

8. **Secure MCP server communications**
   - Use HTTPS for remote MCP servers
   - Implement authentication where appropriate
   - Monitor access logs for suspicious activity
