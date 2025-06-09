# Monorepo Structure Design

## Proposed Directory Structure

```
resume-velvit-thunder/
├── .github/                     # GitHub workflows and templates
│   └── workflows/               # CI/CD workflows
│
├── apps/
│   ├── api/                     # Backend API service
│   │   ├── src/                  # Source code
│   │   │   ├── api/              # API endpoints
│   │   │   ├── core/             # Core application logic
│   │   │   ├── db/               # Database models and migrations
│   │   │   ├── services/         # Business logic services
│   │   │   └── main.py           # Application entry point
│   │   ├── tests/                # API tests
│   │   └── requirements.txt       # Python dependencies
│   │
│   └── web/                     # Frontend application
│       ├── public/               # Static files
│       ├── src/                  # Source code
│       │   ├── app/             # Next.js app directory
│       │   ├── components/       # Shared UI components
│       │   ├── lib/             # Frontend libraries
│       │   └── styles/          # Global styles
│       ├── tests/               # Frontend tests
│       └── package.json         # Frontend dependencies
│
├── packages/
│   ├── config/                # Shared configuration
│   │   ├── eslint/              # ESLint config
│   │   ├── prettier/            # Prettier config
│   │   └── tsconfig/            # TypeScript config
│   │
│   ├── database/              # Database models and migrations
│   │   └── src/
│   │
│   └── shared/                # Shared code between frontend and backend
│       ├── src/
│       │   ├── types/         # Shared TypeScript types
│       │   ├── utils/          # Shared utilities
│       │   └── constants/      # Shared constants
│       └── package.json
│
├── scripts/                    # Build and utility scripts
│   ├── dev/                    # Development scripts
│   ├── deploy/                 # Deployment scripts
│   └── tools/                  # Helper scripts
│
├── docs/                      # Documentation
│   ├── api/                    # API documentation
│   ├── guides/                 # User and developer guides
│   └── decisions/              # Architecture Decision Records (ADRs)
│
└── tests/
    ├── unit/                  # Unit tests
    │   ├── api/               # API unit tests
    │   └── web/               # Web unit tests
    │
    ├── integration/          # Integration tests
    │   ├── api/               # API integration tests
    │   └── web/               # Web integration tests
    │
    └── e2e/                  # End-to-end tests
        ├── api/               # API E2E tests
        └── web/               # Web E2E tests
```

## Naming Conventions

### Directories
- Use kebab-case for all directory names (e.g., `user-profile`)
- Keep directory names short but descriptive
- Group related files in the same directory
- Use plural for directories containing multiple items of the same type (e.g., `components/`, `services/`)

### Files
- Use kebab-case for all file names (e.g., `user-service.ts`)
- For React components, use PascalCase (e.g., `UserProfile.tsx`)
- For test files, use the pattern `[filename].test.ts` or `[filename].spec.ts`
- For configuration files, use the pattern `.filenamerc` or `filename.config.js`

## Migration Plan

### Phase 1: Setup and Configuration
1. Create the new monorepo structure
2. Set up shared configuration (ESLint, Prettier, TypeScript)
3. Configure workspaces in root `package.json`
4. Set up CI/CD workflows

### Phase 2: Migrate Backend
1. Move API code to `apps/api`
2. Update import paths and configurations
3. Set up database migrations in `packages/database`
4. Move shared types to `packages/shared`

### Phase 3: Migrate Frontend
1. Move Next.js app to `apps/web`
2. Update import paths and configurations
3. Move shared components and utilities
4. Update build and deployment configurations

### Phase 4: Testing and Validation
1. Set up test environments
2. Update test configurations
3. Run full test suite
4. Perform integration testing

## Shared Resources

### Code Sharing
- Move database models to `packages/database`
- Shared types in `packages/shared/src/types`
- Common utilities in `packages/shared/src/utils`
- Configuration in `packages/config`

### Dependencies
- Use workspace protocol (`workspace:*`) for internal package references
- Keep shared dependencies in root `package.json`
- Use specific versions for all dependencies

## Migration Scripts

Create the following scripts to assist with migration:

1. `scripts/migrate/move-files.js` - For moving files to new locations
2. `scripts/migrate/update-imports.js` - For updating import paths
3. `scripts/validate/check-imports.js` - For validating import paths

## Next Steps

1. Review and approve the proposed structure
2. Create a migration branch
3. Begin Phase 1 implementation
4. Set up automated testing for the new structure
