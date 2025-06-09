# Monorepo Structure Design

## Overview
This document outlines the proposed monorepo structure for the Resume Velvit Thunder project, based on the audit findings from Task 82 and the requirements in Task 83.

## Directory Structure

```
resume-velvit-thunder/
├── apps/                    # All applications
│   ├── api/                 # Backend API service
│   │   ├── src/             # Source code
│   │   ├── tests/           # API-specific tests
│   │   └── package.json     # API dependencies
│   │
│   └── web/                # Frontend application
│       ├── public/          # Static files
│       ├── src/             # Source code
│       ├── tests/           # Frontend-specific tests
│       └── package.json     # Frontend dependencies
│
├── packages/               # Shared packages
│   ├── shared/             # Shared utilities and libraries
│   │   ├── src/
│   │   └── package.json
│   │
│   ├── config/            # Shared configuration
│   │   ├── frontend/       # Frontend config
│   │   ├── backend/        # Backend config
│   │   └── package.json
│   │
│   └── types/             # Shared TypeScript types
│       ├── src/
│       └── package.json
│
├── scripts/               # Build and utility scripts
│   ├── build/             # Build scripts
│   ├── deploy/            # Deployment scripts
│   └── utils/             # Utility scripts
│
├── docs/                  # Project documentation
│   ├── api/               # API documentation
│   ├── guides/            # User and developer guides
│   ├── architecture/      # System architecture
│   └── adr/               # Architecture Decision Records
│
├── tests/                # Test files
│   ├── unit/             # Unit tests
│   │   ├── backend/
│   │   └── frontend/
│   │
│   ├── integration/      # Integration tests
│   ├── e2e/              # End-to-end tests
│   └── __fixtures__/     # Test fixtures
│
├── tools/                # Development tools
│   ├── eslint/           # ESLint configs
│   ├── prettier/         # Prettier config
│   └── typescript/       # TypeScript configs
│
├── config/              # Global configuration files
│   ├── jest.config.js
│   ├── tsconfig.base.json
│   └── .eslintrc.js
│
├── package.json         # Root package.json
└── README.md             # Project README
```

## Naming Conventions

### Directories
- Use **kebab-case** for all directory names
- Keep names short but descriptive
- Use plural nouns for directories containing multiple items (e.g., `tests/`, `scripts/`)

### Files
- **Source files**: `kebab-case` for all platforms
- **Test files**: `*.test.ts`, `*.spec.ts`, or `*.test.js`, `*.spec.js`
- **Configuration files**: Match the tool's convention (e.g., `.eslintrc.js`, `tsconfig.json`)
- **Documentation**: Use `README.md` for directories, `kebab-case.md` for other docs

### Code
- **TypeScript/JavaScript**: `camelCase` for variables and functions, `PascalCase` for classes and interfaces
- **Python**: `snake_case` for variables and functions, `PascalCase` for classes
- **CSS/SCSS**: `kebab-case` for class names

## Migration Mapping

| Current Location | New Location | Notes |
|-----------------|--------------|-------|
| `/api` | `/apps/api` | Move backend API code |
| `/resume-builder-app` | `/apps/web` | Move frontend code |
| `/scripts` | `/scripts` | Review and reorganize |
| `/*.md` | `/docs` | Move and reorganize documentation |
| `/tests` | `/tests/unit` | Reorganize test files |

## Shared Resources

### TypeScript Types
- Location: `/packages/types`
- Shared between frontend and backend
- Published as a private package

### Configuration
- Shared configurations in `/packages/config`
- Environment-specific overrides in respective apps

### Utilities
- Common utilities in `/packages/shared`
- Published as a private package
- Imported by both frontend and backend

## Implementation Plan

1. **Phase 1: Setup**
   - Create the new directory structure
   - Set up workspaces in root `package.json`
   - Configure TypeScript project references

2. **Phase 2: Migrate Backend**
   - Move API code to `/apps/api`
   - Update import paths
   - Test functionality

3. **Phase 3: Migrate Frontend**
   - Move frontend code to `/apps/web`
   - Update build configurations
   - Test functionality

4. **Phase 4: Shared Code**
   - Move shared code to `/packages`
   - Set up internal package linking
   - Update imports

5. **Phase 5: Documentation**
   - Update documentation
   - Create migration guides
   - Update README files

## Dependencies

- **Node.js** v16+
- **Yarn** workspaces or **npm** workspaces
- **TypeScript** project references
- **ESLint** and **Prettier** for code style

## Future Considerations

- **CI/CD Pipeline**: Update to support monorepo
- **Code Ownership**: Define ownership boundaries
- **Performance**: Monitor build and test performance
- **Documentation**: Keep documentation up-to-date with structure changes
