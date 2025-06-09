# Backup and Version Control System

This document provides a comprehensive guide to the backup and version control features in the Resume Velvit Thunder project.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
  - [Backup Configuration](#backup-configuration)
  - [Git Integration](#git-integration)
  - [MCP Server Integration](#mcp-server-integration)
  - [Retention Policies](#retention-policies)
- [Usage](#usage)
- [Recovery](#recovery)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

The backup and version control system provides automated, reliable backups of your project with tight integration with git and MCP servers. It's designed to ensure data safety during migrations, updates, and other critical operations.

## Features

- **Comprehensive Backups**: Full project backup with customizable includes/excludes
- **Git Integration**: Automatic git state documentation and tagging
- **MCP Server Support**: Store backup metadata in MCP memory banks
- **Flexible Configuration**: YAML-based configuration with environment variable support
- **Rollback Documentation**: Automatic generation of rollback procedures
- **Retention Policies**: Configurable backup retention

## Quick Start

1. Run a basic backup:
   ```bash
   python scripts/backup_and_version_control.py
   ```

2. Backups will be stored in `backups/pre_migration_<timestamp>/`

## Configuration

### Backup Configuration

Create a `backup_config.yaml` file in the scripts directory:

```yaml
# Directories to include in the backup
include_dirs:
  - config
  - scripts
  - data
  - templates

# File patterns to exclude
exclude_patterns:
  - "*.pyc"
  - "__pycache__"
  - "*.log"
```

### Git Integration

```yaml
git:
  create_tag: true
  tag_prefix: "pre-migration"
  push_tags: false
```

### MCP Server Integration

```yaml
mcp_servers:
  memory_bank:
    enabled: true
    server_name: "memory-bank"
    collection: "backups"
```

### Retention Policies

```yaml
retention:
  keep_daily: 7
  keep_weekly: 4
  keep_monthly: 12
  keep_yearly: 2
```

## Usage

### Basic Usage

```bash
# Run with default settings
python scripts/backup_and_version_control.py

# Specify a custom config file
python scripts/backup_and_version_control.py --config /path/to/config.yaml

# Specify output directory
python scripts/backup_and_version_control.py --output /path/to/backups
```

### Integration with MCP Servers

When MCP server integration is enabled, backup metadata will be stored in the specified MCP memory bank. This includes:
- Backup timestamps
- File hashes
- Git state information
- Backup locations

## Recovery

### From a Backup

1. Locate the backup directory in `backups/pre_migration_<timestamp>/`
2. Extract the project backup:
   ```bash
   unzip project_backup_<timestamp>.zip -d /path/to/restore
   ```
3. Follow the instructions in `ROLLBACK.md` for additional recovery steps

### Using Git

If you need to rollback to a previous state:

```bash
# List tags
git tag -l

# Checkout a specific backup tag
git checkout tags/pre-migration-<timestamp>
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Ensure the script has write permissions to the backup directory
   - Run with appropriate permissions if needed

2. **Git Not Found**
   - Ensure git is installed and in your PATH
   - The script will continue with a warning if git is not available

3. **MCP Server Unavailable**
   - Check that the MCP server is running and accessible
   - Verify the server name and collection in the configuration

## Best Practices

1. **Regular Backups**
   - Set up a cron job or scheduled task for regular backups
   - Example cron job to run daily at 2 AM:
     ```
     0 2 * * * cd /path/to/project && python scripts/backup_and_version_control.py
     ```

2. **Secure Storage**
   - Store backups in a secure, off-site location
   - Encrypt sensitive backup data

3. **Test Restores**
   - Periodically test the restore process
   - Update documentation as needed

4. **Monitor Disk Space**
   - Configure appropriate retention policies
   - Monitor backup storage usage

5. **Version Control**
   - Commit all changes before major operations
   - Use meaningful commit messages and tags
