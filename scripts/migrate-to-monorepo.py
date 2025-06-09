#!/usr/bin/env python3
"""
Monorepo Migration Script

This script helps migrate the current project structure to the new monorepo structure
defined in docs/monorepo-structure-design.md and docs/migration-mapping.md.
"""

import os
import shutil
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MonorepoMigrator:
    """Class to handle monorepo migration."""
    
    def __init__(self, dry_run: bool = True):
        """Initialize the migrator."""
        self.dry_run = dry_run
        self.root_dir = Path(__file__).parent.parent
        self.mapping = self._load_mapping()
        
    def _load_mapping(self) -> Dict[str, str]:
        """Load the migration mapping from the documentation."""
        # This is a simplified mapping - in a real scenario, you might want to parse
        # the migration-mapping.md file or load from a JSON file
        return {
            # Backend
            'api/': 'apps/api/src/',
            'api/alembic/': 'apps/api/alembic/',
            'api/requirements': 'apps/api/requirements',
            'api/main.py': 'apps/api/src/main.py',
            'api/models.py': 'packages/database/src/models/',
            
            # Frontend
            'resume-builder-app/components/': 'apps/web/src/components/',
            'resume-builder-app/app/': 'apps/web/src/app/',
            'resume-builder-app/public/': 'apps/web/public/',
            'resume-builder-app/package.json': 'apps/web/package.json',
            'resume-builder-app/next.config.js': 'apps/web/next.config.js',
            'resume-builder-app/tsconfig.json': 'apps/web/tsconfig.json',
            
            # Shared
            'shared/': 'packages/shared/src/',
            'types/': 'packages/types/src/',
            
            # Config
            '.env': 'apps/api/.env',
            '.env.local': 'apps/web/.env.local',
            
            # Scripts
            'scripts/': 'scripts/tools/',
            
            # Tests
            'tests/unit/': 'tests/unit/backend/',
            'tests/integration/': 'tests/integration/',
            'tests/e2e/': 'tests/e2e/'
        }
    
    def create_directory_structure(self) -> None:
        """Create the target directory structure."""
        directories = [
            'apps/api/src',
            'apps/api/alembic',
            'apps/web/src',
            'apps/web/public',
            'packages/shared/src',
            'packages/types/src',
            'packages/database/src/models',
            'scripts/tools',
            'scripts/build',
            'scripts/deploy',
            'tests/unit/backend',
            'tests/unit/frontend',
            'tests/integration',
            'tests/e2e',
            'tests/__fixtures__',
            'docs/api',
            'docs/guides',
            'docs/architecture'
        ]
        
        for directory in directories:
            dir_path = self.root_dir / directory
            if not dir_path.exists():
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would create directory: {dir_path}")
                else:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created directory: {dir_path}")
    
    def migrate_files(self) -> None:
        """Migrate files according to the mapping."""
        for src_pattern, dest_pattern in self.mapping.items():
            # Handle directory moves
            if src_pattern.endswith('/'):
                src_dir = self.root_dir / src_pattern.rstrip('/')
                if src_dir.exists() and src_dir.is_dir():
                    for src_file in src_dir.rglob('*'):
                        if src_file.is_file():
                            try:
                                # Get the relative path from the source directory
                                rel_path = src_file.relative_to(src_dir)
                                dest_path = self.root_dir / dest_pattern / rel_path
                                self._move_file(src_file, dest_path)
                            except ValueError as e:
                                logger.warning(f"Skipping {src_file}: {e}")
            # Handle specific file moves
            else:
                src_path = self.root_dir / src_pattern
                if src_path.exists() and src_path.is_file():
                    dest_path = self.root_dir / dest_pattern
                    self._move_file(src_path, dest_path)
    
    def _move_file(self, src: Path, dest: Path) -> None:
        """Move a file from src to dest, creating parent directories if needed."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would move: {src} -> {dest}")
            return
            
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
            logger.info(f"Moved: {src} -> {dest}")
        except Exception as e:
            logger.error(f"Error moving {src} to {dest}: {e}")
    
    def update_imports(self) -> None:
        """Update import paths in source files."""
        # This is a simplified example - in a real scenario, you would use
        # a proper code parser to update import paths
        logger.info("Updating import paths...")
        
        # Example: Update Python imports
        for py_file in self.root_dir.rglob('*.py'):
            self._update_file_imports(py_file)
            
        # Example: Update TypeScript/JavaScript imports
        for js_file in self.root_dir.rglob('*.{ts,tsx,js,jsx}'):
            self._update_file_imports(js_file)
    
    def _update_file_imports(self, file_path: Path) -> None:
        """Update import paths in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # This is a simplified example - in a real scenario, you would use
            # a proper code parser to update import paths
            updated_content = content
            
            if updated_content != content:
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would update imports in: {file_path}")
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    logger.info(f"Updated imports in: {file_path}")
        except Exception as e:
            logger.error(f"Error updating imports in {file_path}: {e}")
    
    def run(self) -> None:
        """Run the migration process."""
        logger.info("Starting monorepo migration...")
        
        # 1. Create directory structure
        logger.info("Creating directory structure...")
        self.create_directory_structure()
        
        # 2. Migrate files
        logger.info("Migrating files...")
        self.migrate_files()
        
        # 3. Update imports
        logger.info("Updating imports...")
        self.update_imports()
        
        logger.info("Migration completed successfully!")
        if self.dry_run:
            logger.info("This was a dry run. No files were actually modified.")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Migrate to monorepo structure')
    parser.add_argument('--execute', action='store_true', help='Actually perform the migration (default: dry run)')
    args = parser.parse_args()
    
    migrator = MonorepoMigrator(dry_run=not args.execute)
    migrator.run()


if __name__ == '__main__':
    main()
