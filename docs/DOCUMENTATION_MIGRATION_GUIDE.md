# Documentation Migration and Consolidation Guide

This guide provides comprehensive instructions for migrating and consolidating documentation in the Resume Velvit Thunder project.

## Table of Contents
- [Overview](#overview)
- [Migration Process](#migration-process)
- [Configuration](#configuration)
- [Running the Migration](#running-the-migration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [MCP Integration](#mcp-integration)

## Overview

The documentation migration process helps standardize the documentation structure across the project, making it easier to maintain and find information. The migration:

1. Scans the project for documentation files
2. Categorizes them by type (API, guides, architecture, etc.)
3. Moves them to the appropriate location in the new structure
4. Updates internal links and references
5. Generates a migration report

## Migration Process

### 1. Pre-Migration Steps

1. **Backup your work**
   ```bash
   git add .
   git commit -m "Pre-documentation-migration backup"
   git tag -a pre-docs-migration -m "State before documentation migration"
   ```

2. **Install dependencies**
   Ensure you have Python 3.8+ and required packages:
   ```bash
   pip install -r requirements-dev.txt
   ```

### 2. Review Configuration

1. Copy the example config file:
   ```bash
   cp scripts/docs_migration_config.yaml docs_migration.yaml
   ```

2. Review and update the configuration in `docs_migration.yaml` as needed.

### 3. Run the Migration

Perform a dry run first to see what changes will be made:

```bash
python scripts/migrate_docs.py --dry-run --project-root .
```

If the dry run looks good, run the actual migration:

```bash
python scripts/migrate_docs.py --project-root .
```

### 4. Verify the Migration

1. Review the migration report at `docs/MIGRATION_REPORT.md`
2. Check for any broken links or missing files
3. Verify the new documentation structure

## Configuration

The migration is configured via `docs_migration.yaml`. Key sections:

### File Patterns

```yaml
include_patterns:
  - "**/*.md"
  - "**/*.mdx"
  - "**/*.rst"
  - "**/docs/**/*.*"
  - "**/documentation/**/*.*"
```

### Documentation Structure

```yaml
structure:
  api: "API Reference"
  guides: "Guides"
  architecture: "Architecture"
  tutorials: "Tutorials"
  examples: "Examples"
  resources: "Resources"
  changelog: "Changelog"
```

### MCP Integration

```yaml
mcp:
  enabled: true
  server_name: memory-bank
  collection: documentation
```

## Running the Migration

### Basic Usage

```bash
# Dry run (no changes)
python scripts/migrate_docs.py --dry-run

# Actual migration
python scripts/migrate_docs.py

# Specify custom config file
python scripts/migrate_docs.py --config custom_config.yaml
```

### Command Line Options

- `--dry-run`: Show what would be done without making changes
- `--project-root`: Path to the project root directory
- `--config`: Path to a custom configuration file
- `--scan-only`: Only scan for documentation files, do not migrate

## Verification

After migration:

1. Check the migration report:
   ```bash
   cat docs/MIGRATION_REPORT.md
   ```

2. Verify the new documentation structure:
   ```
   docs/
   ├── api/             # API Reference
   ├── guides/          # How-to guides
   ├── architecture/    # System design docs
   ├── tutorials/       # Step-by-step tutorials
   ├── examples/        # Code examples
   ├── resources/       # Additional resources
   ├── changelog/       # Release notes
   ├── README.md        # Main documentation index
   └── MIGRATION_REPORT.md  # Migration summary
   ```

3. Test internal links:
   ```bash
   # Install markdown-link-check
   npm install -g markdown-link-check
   
   # Check all markdown files
   find docs -name "*.md" -exec markdown-link-check {} \;
   ```

## Troubleshooting

### Common Issues

1. **Broken Links**
   - Check the migration report for any broken links
   - Update any hardcoded paths in documentation

2. **Missing Files**
   - Verify the file patterns in the configuration
   - Check the exclude patterns

3. **Permission Issues**
   - Ensure you have write permissions in the target directories
   - Run the script with appropriate permissions if needed

### Logs

Detailed logs are available in `docs_migration.log`:

```bash
tail -f docs_migration.log
```

## Best Practices

1. **Incremental Migration**
   - Migrate documentation in small batches
   - Commit after each successful batch

2. **Code Reviews**
   - Review the migration changes before merging
   - Pay special attention to link updates

3. **Documentation**
   - Update any documentation referencing old paths
   - Document the new structure for the team

4. **CI/CD**
   - Add a step to verify documentation structure
   - Consider adding link checking to your CI pipeline

## MCP Integration

The migration process can be tracked using MCP servers:

1. Enable MCP integration in the config:
   ```yaml
   mcp:
     enabled: true
     server_name: 'memory-bank'
     collection: 'documentation'
   ```

2. Migration metadata will be stored in the specified MCP collection

3. Query migration history:
   ```python
   migrations = mcp_client.query(
       server='memory-bank',
       collection='documentation',
       query={}
   )
   ```

## Post-Migration

After successful migration:

1. Update `.gitignore` to exclude temporary files
2. Update documentation with the new structure
3. Inform the team about the changes
4. Consider adding a documentation style guide

## Maintenance

### Adding New Documentation

1. Place new documentation in the appropriate directory:
   - API docs in `docs/api/`
   - Guides in `docs/guides/`
   - Architecture docs in `docs/architecture/`
   - Tutorials in `docs/tutorials/`
   - Examples in `docs/examples/`
   - Resources in `docs/resources/`
   - Changelog entries in `docs/changelog/`

2. Update the main README.md with links to new documentation

### Updating Documentation

1. Make changes directly in the appropriate file in the `docs/` directory
2. Update the last updated timestamp if present
3. Update any related documentation
4. Submit a pull request with your changes

### Removing Documentation

1. Remove the file from the `docs/` directory
2. Update any links to the removed documentation
3. Update the main README.md if needed
4. Submit a pull request with your changes

## Resources

- [Markdown Guide](https://www.markdownguide.org/)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [MCP Server Documentation](docs/MCP_INTEGRATION.md)
