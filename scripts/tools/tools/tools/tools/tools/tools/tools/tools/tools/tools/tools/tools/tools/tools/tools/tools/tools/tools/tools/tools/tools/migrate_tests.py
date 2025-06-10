#!/usr/bin/env python3
"""
Test File Migration and Reorganization Script

This script helps migrate and reorganize test files into a standardized monorepo structure.
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
        self.project_root = project_root
        self.dry_run = dry_run
        
        # Define source and target directories
        self.src_dirs = {
            'backend': [
                project_root / 'api',
                project_root / 'scripts',
                project_root
            ],
            'frontend': [
                project_root / 'v0-resume-creation-framework',
                project_root / 'resume-builder-app'
            ]
        }
        
        # Define test directory structure
        self.test_structure = {
            'unit': {
                'backend': 'tests/unit/backend',
                'frontend': 'tests/unit/frontend',
                'shared': 'tests/unit/shared'
            },
            'integration': {
                'backend': 'tests/integration/backend',
                'frontend': 'tests/integration/frontend',
                'fullstack': 'tests/integration/fullstack'
            },
            'e2e': 'tests/e2e',
            'mocks': 'tests/__mocks__',
            'fixtures': 'tests/__fixtures__',
            'utils': 'tests/utils'
        }
        
        # File patterns to identify test files
        self.test_patterns = {
            'python': [
                'test_*.py',
                '*_test.py',
                'test_*.pyi',
                '*_test.pyi'
            ],
            'javascript': [
                '*.test.*',
                '*.spec.*',
                '**/__tests__/**/*.*',
                '**/test/**/*.*'
            ]
        }
        
        # Initialize MCP client if available
        self.mcp_client = self._init_mcp_client()
    
    def _init_mcp_client(self):
        """Initialize MCP client if available."""
        try:
            from mcp import MCPClient
            return MCPClient()
        except ImportError:
            logger.warning("MCP client not available. Running without MCP integration.")
            return None
    
    def log_to_mcp(self, message: str, level: str = 'info', metadata: Optional[dict] = None):
        """Log a message to MCP if available."""
        if self.mcp_client:
            try:
                self.mcp_client.log(
                    message=message,
                    level=level,
                    metadata=metadata or {}
                )
            except Exception as e:
                logger.warning(f"Failed to log to MCP: {e}")
    
    def find_test_files(self) -> Dict[str, List[Path]]:
        """Find all test files in the project."""
        test_files = {
            'backend': [],
            'frontend': [],
            'other': []
        }
        
        # Find Python test files
        for src_dir in self.src_dirs['backend']:
            if not src_dir.exists():
                continue
                
            for pattern in self.test_patterns['python']:
                for test_file in src_dir.rglob(pattern):
                    if 'test' in test_file.parts and 'node_modules' not in test_file.parts:
                        test_files['backend'].append(test_file)
        
        # Find JavaScript/TypeScript test files
        for src_dir in self.src_dirs['frontend']:
            if not src_dir.exists():
                continue
                
            for pattern in self.test_patterns['javascript']:
                for test_file in src_dir.rglob(pattern):
                    if 'node_modules' not in test_file.parts and not any(
                        p.startswith('.') or p == 'node_modules' for p in test_file.parts
                    ):
                        test_files['frontend'].append(test_file)
        
        return test_files
    
    def determine_test_type(self, file_path: Path) -> Tuple[str, str]:
        """Determine the test type and scope."""
        rel_path = file_path.relative_to(self.project_root)
        path_str = str(rel_path).replace('\\', '/')
        
        # Check for end-to-end tests
        if 'e2e' in path_str.lower() or 'cypress' in path_str.lower():
            return 'e2e', 'e2e'
            
        # Check for integration tests
        if 'integration' in path_str.lower() or 'test_integration' in path_str.lower():
            if 'frontend' in path_str.lower() or any(p in path_str.lower() for p in ['.tsx', '.jsx', '.ts', '.js']):
                return 'integration', 'frontend'
            elif 'backend' in path_str.lower() or file_path.suffix == '.py':
                return 'integration', 'backend'
            else:
                return 'integration', 'fullstack'
        
        # Default to unit tests
        if file_path.suffix in ['.tsx', '.jsx', '.ts', '.js']:
            return 'unit', 'frontend'
        elif file_path.suffix == '.py':
            return 'unit', 'backend'
        else:
            return 'unit', 'other'
    
    def get_target_path(self, src_path: Path, test_type: str, scope: str) -> Path:
        """Determine the target path for a test file."""
        rel_path = src_path.relative_to(self.project_root)
        
        # Handle special cases first
        if test_type == 'e2e':
            return self.project_root / self.test_structure['e2e'] / rel_path.name
            
        # Handle integration tests
        if test_type == 'integration':
            base_dir = self.test_structure['integration'].get(scope, self.test_structure['integration']['fullstack'])
            return self.project_root / base_dir / rel_path.relative_to(*rel_path.parts[:1])
        
        # Handle unit tests
        base_dir = self.test_structure['unit'].get(scope, self.test_structure['unit']['backend'])
        return self.project_root / base_dir / rel_path.relative_to(*rel_path.parts[:1])
    
    def update_imports(self, file_path: Path, old_base: Path, new_base: Path) -> bool:
        """Update import paths in a file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Skip binary files
            if '\x00' in content:
                return False
                
            # Update Python imports
            if file_path.suffix == '.py':
                # Convert paths to module paths
                rel_path = file_path.relative_to(self.project_root)
                module_path = str(rel_path.with_suffix('')).replace(os.sep, '.')
                
                # Find and update imports
                lines = content.splitlines()
                updated = False
                
                for i, line in enumerate(lines):
                    # Handle from ... import ...
                    match = re.match(r'^(\s*from\s+["\']?)(\.*?)(["\']?\s+import\s+.*)$', line)
                    if match and match.group(2).startswith('.'):
                        old_import = match.group(2)
                        # Calculate new relative import
                        # This is a simplified version - might need adjustment based on project structure
                        new_import = old_import  # Placeholder for actual calculation
                        if new_import != old_import:
                            lines[i] = f"{match.group(1)}{new_import}{match.group(3)}"
                            updated = True
                
                if updated:
                    if not self.dry_run:
                        file_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
                    return True
            
            # Update JavaScript/TypeScript imports
            elif file_path.suffix in ['.ts', '.tsx', '.js', '.jsx']:
                # Similar logic for JS/TS imports
                pass
                
            return False
            
        except Exception as e:
            logger.error(f"Error updating imports in {file_path}: {e}")
            return False
    
    def migrate_tests(self):
        """Migrate test files to the new structure."""
        test_files = self.find_test_files()
        migration_plan = {
            'moved': [],
            'updated': [],
            'errors': []
        }
        
        # Create target directories
        for dir_type in self.test_structure.values():
            if isinstance(dir_type, dict):
                for dir_path in dir_type.values():
                    target_dir = self.project_root / dir_path
                    if not target_dir.exists() and not self.dry_run:
                        target_dir.mkdir(parents=True, exist_ok=True)
            else:
                target_dir = self.project_root / dir_type
                if not target_dir.exists() and not self.dry_run:
                    target_dir.mkdir(parents=True, exist_ok=True)
        
        # Process test files
        for category, files in test_files.items():
            for src_path in files:
                try:
                    test_type, scope = self.determine_test_type(src_path)
                    target_path = self.get_target_path(src_path, test_type, scope)
                    
                    # Skip if already in the right place
                    if src_path.resolve() == target_path.resolve():
                        continue
                    
                    # Create target directory if it doesn't exist
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move the file
                    if not self.dry_run:
                        shutil.move(str(src_path), str(target_path))
                        
                        # Update imports in the moved file
                        self.update_imports(target_path, src_path.parent, target_path.parent)
                        
                        # Update imports in other files that reference this file
                        self.update_references(src_path, target_path)
                    
                    migration_plan['moved'].append({
                        'from': str(src_path.relative_to(self.project_root)),
                        'to': str(target_path.relative_to(self.project_root)),
                        'type': test_type,
                        'scope': scope
                    })
                    
                    logger.info(f"Moved {src_path} to {target_path}")
                    
                except Exception as e:
                    error_msg = f"Error processing {src_path}: {e}"
                    logger.error(error_msg)
                    migration_plan['errors'].append({
                        'file': str(src_path.relative_to(self.project_root)),
                        'error': str(e)
                    })
                    self.log_to_mcp(error_msg, level='error')
        
        # Generate migration report
        self._generate_report(migration_plan)
        return migration_plan
    
    def update_references(self, old_path: Path, new_path: Path):
        """Update references to a moved file."""
        # This would search through the codebase and update import paths
        # Implementation depends on the project's specific needs
        pass
    
    def _generate_report(self, migration_plan: dict):
        """Generate a migration report."""
        report_path = self.project_root / 'test_migration_report.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Test Migration Report\n\n")
            f.write(f"Generated at: {datetime.datetime.now().isoformat()}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Files moved: {len(migration_plan['moved'])}\n")
            f.write(f"- Files updated: {len(migration_plan['updated'])}\n")
            f.write(f"- Errors: {len(migration_plan['errors'])}\n\n")
            
            if migration_plan['moved']:
                f.write("## Moved Files\n\n")
                f.write("| From | To | Type | Scope |\n")
                f.write("|------|----|------|-------|\n")
                for item in migration_plan['moved']:
                    f.write(f"| `{item['from']}` | `{item['to']}` | {item['type']} | {item['scope']} |\n")
                f.write("\n")
            
            if migration_plan['errors']:
                f.write("## Errors\n\n")
                f.write("| File | Error |\n")
                f.write("|------|-------|\n")
                for error in migration_plan['errors']:
                    f.write(f"| `{error['file']}` | `{error['error']}` |\n")
                f.write("\n")
        
        logger.info(f"Migration report generated at: {report_path}")
        self.log_to_mcp(
            f"Test migration completed. Moved {len(migration_plan['moved'])} files with {len(migration_plan['errors'])} errors.",
            metadata={
                'moved': len(migration_plan['moved']),
                'updated': len(migration_plan['updated']),
                'errors': len(migration_plan['errors'])
            }
        )

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Migrate test files to the new structure.')
    parser.add_argument('--dry-run', action='store_true', help='Perform a dry run without making changes')
    parser.add_argument('--project-root', type=Path, default=Path.cwd(),
                      help='Path to the project root directory')
    
    args = parser.parse_args()
    
    migrator = TestMigrator(args.project_root, dry_run=args.dry_run)
    
    if args.dry_run:
        logger.info("Running in dry-run mode. No changes will be made.")
    
    migration_plan = migrator.migrate_tests()
    
    if args.dry_run:
        logger.info("Dry run completed. Review the migration plan above.")
    else:
        logger.info("Migration completed. Review the migration report for details.")

if __name__ == "__main__":
    main()
