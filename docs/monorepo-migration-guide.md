# Monorepo Migration Guide

This guide provides step-by-step instructions for migrating the Resume Velvit Thunder project to the new monorepo structure.

## Overview

The migration involves:
1. Setting up the new directory structure
2. Moving files to their new locations
3. Updating import paths and configurations
4. Verifying the migration

## Prerequisites

- Python 3.8+
- Node.js 16+
- Git

## Migration Steps

### 1. Backup Your Work

Before starting the migration, make sure to commit or back up any uncommitted changes:

```bash
git add .
git commit -m "Backup before monorepo migration"
```

### 2. Run the Migration Script

We've provided a migration script to help with the process. First, run it in dry-run mode to see what changes will be made:

```bash
python scripts/migrate-to-monorepo.py
```

Review the output to ensure the changes look correct. When you're ready to perform the actual migration, run:

```bash
python scripts/migrate-to-monorepo.py --execute
```

### 3. Manual Steps

After running the migration script, there are a few manual steps to complete:

#### Update Package.jsons

1. **Root package.json**:
   - Add workspaces configuration
   - Update scripts for the monorepo

2. **API package.json**:
   - Update paths to reflect the new structure
   - Add workspace dependencies

3. **Web package.json**:
   - Update paths and dependencies
   - Add workspace dependencies

#### Update Configuration Files

1. **TypeScript Configs**:
   - Update `tsconfig.json` files to work with the new structure
   - Set up project references

2. **ESLint/Prettier**:
   - Update configuration files for the new structure
   - Ensure consistent rules across packages

3. **Environment Variables**:
   - Move and update `.env` files as needed
   - Update any hardcoded paths

### 4. Test the Migration

Run the test suite to ensure everything is working correctly:

```bash
# Install dependencies
npm install

# Run backend tests
cd apps/api
pytest

# Run frontend tests
cd ../web
npm test

# Run end-to-end tests
cd ../..
npm run test:e2e
```

### 5. Update CI/CD Pipelines

Update your CI/CD configuration to work with the new monorepo structure:

1. Update build and test steps
2. Configure caching for workspaces
3. Update deployment configurations

## Directory Structure

After migration, your project should have the following structure:

```
resume-velvit-thunder/
├── apps/
│   ├── api/              # Backend API
│   └── web/              # Frontend application
├── packages/
│   ├── shared/         # Shared utilities
│   ├── types/           # Shared TypeScript types
│   └── database/        # Database models and migrations
├── scripts/             # Build and utility scripts
├── tests/               # Test files
├── docs/                # Documentation
└── config/              # Global configuration
```

## Common Issues and Solutions

### Import Errors

If you encounter import errors after migration:

1. Check that all paths in import statements are correct
2. Verify that `tsconfig.json` paths are properly configured
3. Ensure all workspace dependencies are properly linked

### Missing Dependencies

If you're missing dependencies:

1. Run `npm install` in the root directory
2. Check that all workspace dependencies are listed in the appropriate `package.json`
3. Verify that the workspace protocol is used for internal dependencies (e.g., `"@your-org/shared": "workspace:*"`)

### Build Failures

If the build fails:

1. Check for TypeScript errors
2. Verify that all configuration files are updated for the new structure
3. Ensure environment variables are properly set

## Rollback Plan

If you need to rollback the migration:

1. Use Git to revert to the previous commit:
   ```bash
   git reset --hard HEAD~1
   git clean -fd
   ```

2. If you've made additional commits after the migration, use:
   ```bash
   git revert <commit-hash>
   ```

## Post-Migration Tasks

After a successful migration:

1. Update documentation to reflect the new structure
2. Inform the team about the changes
3. Update any deployment scripts or documentation

## Support

If you encounter any issues during the migration, please:

1. Check the [migration mapping document](./migration-mapping.md)
2. Review the [monorepo structure design](./monorepo-structure-design.md)
3. Open an issue in the project repository

## Conclusion

This migration will help improve code organization, facilitate code sharing, and support future growth of the project. If you have any questions or run into issues, don't hesitate to reach out to the development team for assistance.
