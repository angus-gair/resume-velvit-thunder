#!/usr/bin/env python3
"""
Test File Migration and Reorganization Script

This script helps migrate and reorganize test files into the new monorepo structure.
It handles both backend (Python) and frontend (TypeScript/JavaScript) test files.
"""

import os
import re
import shutil
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestMigrator:
    """Handles the migration and reorganization of test files."""
    
    def __init__(self, project_root: Path, dry_run: bool = False):
        """Initialize the test migrator."""
        self.project_root = project_root.resolve()
        self.dry_run = dry_run
        
        # Define source and target directories
        self.src_dirs = {
            'backend': [
                self.project_root / 'api',
                self.project_root / 'scripts',
                self.project_root
            ],
            'frontend': [
                self.project_root / 'v0-resume-creation-framework',
            ]
        }
        
        # Define test directory structure
        self.test_dirs = {
            'unit': {
                'backend': self.project_root / 'tests' / 'unit' / 'backend',
                'frontend': self.project_root / 'tests' / 'unit' / 'frontend',
            },
            'integration': self.project_root / 'tests' / 'integration',
            'e2e': self.project_root / 'tests' / 'e2e',
            'fixtures': self.project_root / 'tests' / '__fixtures__'
        }
        
        # File patterns to identify test files
        self.test_patterns = {
            'backend': [
                'test_*.py',
                '*_test.py',
                'test_*.pyi',
            ],
            'frontend': [
                '**/__tests__/**/*.test.{js,jsx,ts,tsx}',
                '**/__tests__/**/*.spec.{js,jsx,ts,tsx}',
                '**/*.test.{js,jsx,ts,tsx}',
                '**/*.spec.{js,jsx,ts,tsx}',
            ]
        }
        
        # Files to exclude from migration
        self.exclude_patterns = [
            '**/node_modules/**',
            '**/dist/**',
            '**/build/**',
            '**/.next/**',
            '**/.git/**',
            '**/__pycache__/**',
            '**/*.pyc',
            '**/*.pyo',
            '**/*.pyd',
        ]
    
    def find_test_files(self) -> Dict[str, List[Path]]:
        """Find all test files in the project."""
        test_files = {
            'backend': [],
            'frontend': [],
            'other': []
        }
        
        # Find backend test files
        for src_dir in self.src_dirs['backend']:
            if not src_dir.exists():
                logger.warning(f"Source directory does not exist: {src_dir}")
                continue
                
            for pattern in self.test_patterns['backend']:
                for test_file in src_dir.rglob(pattern):
                    if self._should_exclude(test_file):
                        continue
                    test_files['backend'].append(test_file)
        
        # Find frontend test files
        for src_dir in self.src_dirs['frontend']:
            if not src_dir.exists():
                logger.warning(f"Source directory does not exist: {src_dir}")
                continue
                
            for pattern in self.test_patterns['frontend']:
                for test_file in src_dir.rglob(pattern):
                    if self._should_exclude(test_file):
                        continue
                    test_files['frontend'].append(test_file)
        
        return test_files
    
    def _should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded from processing."""
        path_str = str(path.absolute())
        return any(
            re.search(pattern.replace('**', '.*').replace('*', '[^/]*'), path_str)
            for pattern in self.exclude_patterns
        )
    
    def determine_target_path(self, source_path: Path) -> Optional[Path]:
        """Determine the target path for a test file."""
        rel_path = source_path.relative_to(self.project_root)
        
        # Check if it's a backend test
        if any(part.startswith('test_') or part.endswith('_test.py') for part in source_path.parts):
            if source_path.suffix == '.py':
                # Move to unit/backend
                return self.test_dirs['unit']['backend'] / source_path.name
            
        # Check if it's in a __tests__ directory (frontend)
        if '__tests__' in source_path.parts:
            rel_to_tests = Path(*rel_path.parts[rel_path.parts.index('__tests__') + 1:])
            return self.test_dirs['unit']['frontend'] / rel_to_tests
        
        # Check for frontend test files
        if source_path.suffix in ('.test.js', '.test.ts', '.test.jsx', '.test.tsx', 
                                '.spec.js', '.spec.ts', '.spec.jsx', '.spec.tsx'):
            # Try to maintain directory structure
            rel_dir = source_path.parent.relative_to(self.project_root)
            return self.test_dirs['unit']['frontend'] / rel_dir.name / source_path.name
        
        logger.warning(f"Could not determine target for {source_path}")
        return None
    
    def migrate_test_file(self, source_path: Path, target_path: Path) -> None:
        """Migrate a single test file to its new location."""
        # Create target directory if it doesn't exist
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Migrating {source_path.relative_to(self.project_root)} -> {target_path.relative_to(self.project_root)}")
        
        if not self.dry_run:
            # Copy the file to maintain original
            shutil.copy2(source_path, target_path)
            
            # Update imports in the file if it's a Python file
            if source_path.suffix == '.py':
                self._update_python_imports(target_path)
    
    def _update_python_imports(self, file_path: Path) -> None:
        """Update import paths in a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple import path updates (this is a basic implementation)
            # In a real scenario, you'd want to use a proper Python AST parser
            updated_content = content
            
            # Update relative imports
            updated_content = re.sub(
                r'from\s+\.+\s+import', 
                'from ...' + str(file_path.relative_to(self.project_root).parent).replace('\\', '.') + ' import',
                updated_content
            )
            
            # Update absolute imports
            updated_content = re.sub(
                r'from\s+api\.', 
                'from apps.api.',
                updated_content
            )
            
            if updated_content != content and not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                    
        except Exception as e:
            logger.error(f"Error updating imports in {file_path}: {e}")
    
    def migrate_all(self) -> None:
        """Migrate all test files to the new structure."""
        test_files = self.find_test_files()
        
        # Create target directories
        if not self.dry_run:
            for dir_type in self.test_dirs.values():
                if isinstance(dir_type, dict):
                    for d in dir_type.values():
                        d.mkdir(parents=True, exist_ok=True)
                else:
                    dir_type.mkdir(parents=True, exist_ok=True)
        
        # Migrate backend tests
        for test_file in test_files['backend']:
            target_path = self.determine_target_path(test_file)
            if target_path:
                self.migrate_test_file(test_file, target_path)
        
        # Migrate frontend tests
        for test_file in test_files['frontend']:
            target_path = self.determine_target_path(test_file)
            if target_path:
                self.migrate_test_file(test_file, target_path)
        
        logger.info("Migration complete!")
        
        # Print summary
        self.print_summary(test_files)
    
    def print_summary(self, test_files: Dict[str, List[Path]]) -> None:
        """Print a summary of the migration."""
        print("\n" + "=" * 50)
        print("Test Migration Summary")
        print("=" * 50)
        print(f"Backend tests found: {len(test_files['backend'])}")
        print(f"Frontend tests found: {len(test_files['frontend'])}")
        print(f"Other test files found: {len(test_files['other'])}")
        print("\nTarget directories:")
        for dir_type, paths in self.test_dirs.items():
            if isinstance(paths, dict):
                for name, path in paths.items():
                    print(f"- {dir_type}/{name}: {path.relative_to(self.project_root)}")
            else:
                print(f"- {dir_type}: {paths.relative_to(self.project_root)}")
        
        if self.dry_run:
            print("\nNOTE: This was a dry run. No files were actually modified.")
        print("=" * 50 + "\n")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Migrate test files to the new monorepo structure.')
    parser.add_argument(
        '--dry-run', 
        action='store_true', 
        help='Run without making any changes'
    )
    parser.add_argument(
        '--project-dir',
        type=Path,
        default=Path.cwd(),
        help='Path to the project root directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    migrator = TestMigrator(project_root=args.project_dir, dry_run=args.dry_run)
    migrator.migrate_all()


if __name__ == "__main__":
    main()
