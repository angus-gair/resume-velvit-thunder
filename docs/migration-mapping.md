# Migration Mapping Document

This document outlines the mapping of files from the current structure to the new monorepo structure.

## Backend (API) Migration

| Current Location | New Location | Status | Notes |
|-----------------|--------------|--------|-------|
| `/api/*` | `/apps/api/src/*` | Pending | Move all API source files |
| `/api/alembic` | `/apps/api/alembic` | Pending | Database migrations |
| `/api/requirements*.txt` | `/apps/api/requirements*.txt` | Pending | Python dependencies |
| `/api/main.py` | `/apps/api/src/main.py` | Pending | Entry point |
| `/api/models.py` | `/packages/database/src/models/` | Pending | Move to shared database package |

## Frontend Migration

| Current Location | New Location | Status | Notes |
|-----------------|--------------|--------|-------|
| `/resume-builder-app/*` | `/apps/web/` | Pending | Move Next.js app |
| `/resume-builder-app/components/*` | `/apps/web/src/components/` | Pending | UI components |
| `/resume-builder-app/app/*` | `/apps/web/src/app/` | Pending | Next.js app directory |
| `/resume-builder-app/public/*` | `/apps/web/public/` | Pending | Static assets |

## Shared Code

| Current Location | New Location | Status | Notes |
|-----------------|--------------|--------|-------|
| `*.d.ts` files | `/packages/shared/src/types/` | Pending | Shared TypeScript types |
| Common utilities | `/packages/shared/src/utils/` | Pending | Shared utility functions |
| Constants | `/packages/shared/src/constants/` | Pending | Shared constants |

## Configuration Files

| Current Location | New Location | Status | Notes |
|-----------------|--------------|--------|-------|
| `.env*` | `/apps/api/.env*` | Pending | API environment variables |
| `.env*` | `/apps/web/.env*` | Pending | Web environment variables |
| `tsconfig.json` | `/packages/config/tsconfig/` | Pending | Shared TypeScript config |
| `.eslintrc` | `/packages/config/eslint/` | Pending | Shared ESLint config |
| `.prettierrc` | `/packages/config/prettier/` | Pending | Shared Prettier config |

## Scripts

| Current Location | New Location | Status | Notes |
|-----------------|--------------|--------|-------|
| `/scripts/*` | `/scripts/tools/` | Pending | Utility scripts |
| Build scripts | `/scripts/build/` | Pending | Build-related scripts |
| Deployment scripts | `/scripts/deploy/` | Pending | Deployment scripts |

## Documentation

| Current Location | New Location | Status | Notes |
|-----------------|--------------|--------|-------|
| `/*.md` | `/docs/guides/` | Pending | Move root markdown files |
| `/docs/*` | `/docs/` | Pending | Keep existing docs |
| API docs | `/docs/api/` | Pending | API documentation |

## Tests

| Current Location | New Location | Status | Notes |
|-----------------|--------------|--------|-------|
| `test_*.py` | `/tests/unit/api/` | Pending | API unit tests |
| Frontend tests | `/tests/unit/web/` | Pending | Web unit tests |
| Integration tests | `/tests/integration/` | Pending | Integration tests |
| E2E tests | `/tests/e2e/` | Pending | End-to-end tests |

## Special Handling

### Files to be Deleted
- Duplicate configuration files
- Old build artifacts
- Temporary files
- IDE-specific files that should be in `.gitignore`

### Files to be Archived
- Old database backups
- Legacy code that's no longer used but should be kept for reference
- Previous versions of files that were significantly modified

## Migration Scripts

1. **File Mover Script**
   ```bash
   # Example command to move files
   ./scripts/migrate/move-files.js --from=/api --to=/apps/api --dry-run
   ```

2. **Import Updater Script**
   ```bash
   # Update import paths in files
   ./scripts/migrate/update-imports.js --dir=/apps --old-path=../../api --new-path=@resume-velvit-thunder/api
   ```

3. **Validation Script**
   ```bash
   # Validate import paths and file references
   ./scripts/validate/check-imports.js --dir=/apps
   ```

## Post-Migration Steps

1. Verify all tests pass
2. Check for broken imports
3. Update CI/CD pipelines
4. Update documentation
5. Clean up old files
6. Update README with new setup instructions
