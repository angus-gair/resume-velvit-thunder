# Test Migration and Reorganization Guide

This guide provides comprehensive instructions for migrating and reorganizing test files in the Resume Velvit Thunder project.

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

The test migration process helps standardize the test directory structure across the project, making it easier to maintain and scale the test suite. The migration:

1. Identifies test files throughout the codebase
2. Categorizes them by type (unit, integration, e2e)
3. Moves them to the appropriate location in the new structure
4. Updates import paths and references

## Migration Process

### 1. Pre-Migration Steps

1. **Backup your work**
   ```bash
   git add .
   git commit -m "Pre-test-migration backup"
   git tag -a pre-test-migration -m "State before test migration"
   ```

2. **Install dependencies**
   Ensure you have Python 3.8+ and required packages:
   ```bash
   pip install -r requirements-dev.txt
   ```

### 2. Review Configuration

1. Copy the example config file:
   ```bash
   cp scripts/test_migration_config.yaml test_migration.yaml
   ```

2. Review and update the configuration in `test_migration.yaml` as needed.

### 3. Run the Migration

Perform a dry run first to see what changes will be made:

```bash
python scripts/migrate_tests.py --dry-run --project-root .
```

If the dry run looks good, run the actual migration:

```bash
python scripts/migrate_tests.py --project-root .
```

### 4. Verify the Migration

1. Review the migration report at `test_migration_report.md`
2. Run the test suite to ensure all tests still pass
3. Check for any remaining import issues

## Configuration

The migration is configured via `test_migration.yaml`. Key sections:

### Source Directories

```yaml
source_directories:
  backend:
    - api
    - scripts
  frontend:
    - v0-resume-creation-framework
```

### Test Patterns

```yaml
test_patterns:
  python:
    - 'test_*.py'
    - '*_test.py'
  javascript:
    - '*.test.*'
    - '*.spec.*'
```

### Target Structure

```yaml
target_structure:
  unit:
    backend: 'tests/unit/backend'
    frontend: 'tests/unit/frontend'
  integration:
    backend: 'tests/integration/backend'
    frontend: 'tests/integration/frontend'
  e2e: 'tests/e2e'
```

## Running the Migration

### Basic Usage

```bash
# Dry run (no changes)
python scripts/migrate_tests.py --dry-run

# Actual migration
python scripts/migrate_tests.py

# Specify custom config file
python scripts/migrate_tests.py --config custom_config.yaml
```

### Command Line Options

- `--dry-run`: Show what would be done without making changes
- `--project-root`: Path to the project root directory
- `--config`: Path to a custom configuration file
- `--verbose`: Enable verbose output

## Verification

After migration:

1. Run the full test suite:
   ```bash
   # Backend tests
   pytest
   
   # Frontend tests
   cd v0-resume-creation-framework
   npm test
   ```

2. Check for any test failures or import errors

3. Verify the new test structure:
   ```
   tests/
   ├── unit/
   │   ├── backend/
   │   └── frontend/
   ├── integration/
   │   ├── backend/
   │   └── frontend/
   └── e2e/
   ```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Check the migration report for any import-related warnings
   - Update any hardcoded import paths in test utilities

2. **Test Failures**
   - Some tests might fail due to path changes
   - Update test fixtures and mocks to use the new paths

3. **Missing Test Files**
   - Check the configuration for correct source directories and patterns
   - Ensure all test file extensions are included

### Logs

Detailed logs are available in `test_migration.log`:

```bash
tail -f test_migration.log
```

## Best Practices

1. **Incremental Migration**
   - Migrate tests in small batches
   - Commit after each successful batch

2. **Code Reviews**
   - Review the migration changes before merging
   - Pay special attention to import path updates

3. **Documentation**
   - Update any documentation referencing test file locations
   - Document the new test structure for the team

4. **CI/CD**
   - Update CI/CD pipelines to use the new test paths
   - Add a step to verify the test structure

## MCP Integration

The migration process can be tracked using MCP servers:

1. Enable MCP integration in the config:
   ```yaml
   mcp_integration:
     enabled: true
     server_name: 'memory-bank'
     collection: 'test_migrations'
   ```

2. Migration metadata will be stored in the specified MCP collection

3. Query migration history:
   ```python
   migrations = mcp_client.query(
       server='memory-bank',
       collection='test_migrations',
       query={}
   )
   ```

## Post-Migration

After successful migration:

1. Update `.gitignore` to exclude test artifacts
2. Update documentation with the new test structure
3. Inform the team about the changes
4. Consider adding a CONTRIBUTING.md section about the test structure
