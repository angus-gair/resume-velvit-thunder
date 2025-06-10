#!/usr/bin/env python3
"""
Documentation Migration and Consolidation Script

This script helps migrate and consolidate documentation into a standardized structure.
It analyzes existing documentation, organizes it, and generates a new documentation structure.
"""

import os
import re
import shutil
import logging
import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('doc_migration.log')
    ]
)
logger = logging.getLogger(__name__)

class DocumentationMigrator:
    """Handles the migration and consolidation of documentation."""
    
    def __init__(self, project_root: Path, config_path: Optional[Path] = None, dry_run: bool = False):
        """Initialize the documentation migrator."""
        self.project_root = project_root
        self.dry_run = dry_run
        self.config = self._load_config(config_path)
        self.mcp_client = self._init_mcp_client()
        
        # Set up documentation structure
        self.docs_dir = project_root / 'docs'
        self.doc_structure = {
            'api': 'API Reference',
            'guides': 'Guides',
            'architecture': 'Architecture',
            'tutorials': 'Tutorials',
            'examples': 'Examples',
            'resources': 'Resources',
            'changelog': 'Changelog',
        }
        
        # File patterns to identify documentation files
        self.doc_patterns = [
            'README.md',
            '*.md',
            '*.mdx',
            '*.rst',
            '*.txt',
            '*.adoc',
            '**/docs/**/*.*',
            '**/documentation/**/*.*',
        ]
        
        # Initialize documentation inventory
        self.inventory = {
            'found': [],
            'moved': [],
            'updated': [],
            'errors': [],
            'stats': {
                'total_files': 0,
                'markdown_files': 0,
                'other_files': 0,
                'duplicates': 0,
                'outdated': 0
            }
        }
    
    def _load_config(self, config_path: Optional[Path]) -> dict:
        """Load configuration from file."""
        default_config = {
            'exclude_dirs': [
                'node_modules',
                '.git',
                '.github',
                '__pycache__',
                'build',
                'dist',
                'venv',
                'env',
                '*.egg-info',
                '.mypy_cache',
                '.pytest_cache',
                '.vscode',
                '.idea',
            ],
            'exclude_files': [
                'package-lock.json',
                'yarn.lock',
                '*.pyc',
                '*.pyo',
                '*.pyd',
                '*.so',
                '*.dll',
                '*.dylib',
                '*.out',
                '*.exe',
            ],
            'mcp': {
                'enabled': True,
                'server_name': 'memory-bank',
                'collection': 'documentation',
            },
            'structure': {
                'api': 'API Reference',
                'guides': 'Guides',
                'architecture': 'Architecture',
                'tutorials': 'Tutorials',
                'examples': 'Examples',
                'resources': 'Resources',
                'changelog': 'Changelog',
            },
            'templates': {
                'api': 'templates/api.md',
                'guide': 'templates/guide.md',
                'tutorial': 'templates/tutorial.md',
            },
        }
        
        if not config_path:
            return default_config
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f) or {}
                # Merge with default config
                return {**default_config, **user_config}
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            return default_config
    
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
        if self.mcp_client and self.config['mcp']['enabled']:
            try:
                self.mcp_client.log(
                    message=message,
                    level=level,
                    metadata={
                        'project': 'resume-velvit-thunder',
                        'component': 'documentation-migration',
                        **(metadata or {})
                    },
                    collection=self.config['mcp']['collection']
                )
            except Exception as e:
                logger.warning(f"Failed to log to MCP: {e}")
    
    def scan_documentation(self) -> dict:
        """Scan the project for documentation files."""
        logger.info("Scanning for documentation files...")
        
        for pattern in self.doc_patterns:
            for file_path in self.project_root.rglob(pattern):
                # Skip excluded directories and files
                if self._should_skip(file_path):
                    continue
                
                # Skip binary files and non-text files
                if not self._is_text_file(file_path):
                    continue
                
                # Add to inventory
                self._add_to_inventory(file_path)
        
        logger.info(f"Found {self.inventory['stats']['total_files']} documentation files")
        logger.info(f"- Markdown files: {self.inventory['stats']['markdown_files']}")
        logger.info(f"- Other files: {self.inventory['stats']['other_files']}")
        
        # Log to MCP
        self.log_to_mcp(
            "Documentation scan completed",
            metadata={
                'total_files': self.inventory['stats']['total_files'],
                'markdown_files': self.inventory['stats']['markdown_files'],
                'other_files': self.inventory['stats']['other_files']
            }
        )
        
        return self.inventory
    
    def _should_skip(self, file_path: Path) -> bool:
        """Check if a file should be skipped based on configuration."""
        # Skip hidden files and directories
        if any(part.startswith('.') for part in file_path.parts):
            return True
            
        # Skip excluded directories
        for exclude_dir in self.config['exclude_dirs']:
            if exclude_dir in file_path.parts:
                return True
                
        # Skip excluded files
        if file_path.name in self.config['exclude_files']:
            return True
            
        # Skip files in the new docs directory
        if file_path.is_relative_to(self.docs_dir):
            return True
            
        return False
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Check if a file is a text file."""
        try:
            # Check common binary file extensions
            binary_exts = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', 
                          '.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg', '.woff', 
                          '.woff2', '.ttf', '.eot', '.otf', '.zip', '.tar', '.gz', 
                          '.7z', '.rar', '.exe', '.dll', '.so', '.dylib', '.pyc', 
                          '.pyo', '.pyd', '.class', '.jar', '.war', '.ear', '.o', '.a',
                          '.lib', '.dll', '.so', '.dylib', '.obj', '.exe', '.bin']
            
            if file_path.suffix.lower() in binary_exts:
                return False
                
            # Check file content
            try:
                with open(file_path, 'rb') as f:
                    # Read first 1024 bytes to check for binary content
                    chunk = f.read(1024)
                    # Check for null bytes which indicate binary content
                    if b'\x00' in chunk:
                        return False
                    # Check if the content is valid UTF-8
                    chunk.decode('utf-8', errors='strict')
                return True
            except (UnicodeDecodeError, PermissionError):
                return False
        except Exception as e:
            logger.warning(f"Error checking if file is text: {file_path}: {e}")
            return False
    
    def _add_to_inventory(self, file_path: Path):
        """Add a file to the documentation inventory."""
        try:
            rel_path = file_path.relative_to(self.project_root)
            file_info = {
                'path': str(rel_path),
                'name': file_path.name,
                'size': file_path.stat().st_size,
                'modified': file_path.stat().st_mtime,
                'type': 'markdown' if file_path.suffix.lower() in ['.md', '.markdown', '.mdx'] else 'other',
                'category': self._categorize_file(file_path)
            }
            
            self.inventory['found'].append(file_info)
            self.inventory['stats']['total_files'] += 1
            
            if file_info['type'] == 'markdown':
                self.inventory['stats']['markdown_files'] += 1
            else:
                self.inventory['stats']['other_files'] += 1
                
            # Check for duplicates
            if any(f['name'] == file_path.name for f in self.inventory['found'][:-1]):
                self.inventory['stats']['duplicates'] += 1
                file_info['duplicate'] = True
            
            # Check for outdated files (older than 1 year)
            import time
            one_year_ago = time.time() - (365 * 24 * 60 * 60)
            if file_info['modified'] < one_year_ago:
                self.inventory['stats']['outdated'] += 1
                file_info['outdated'] = True
                
        except Exception as e:
            logger.error(f"Error adding {file_path} to inventory: {e}")
            self.inventory['errors'].append({
                'file': str(file_path),
                'error': str(e)
            })
    
    def _categorize_file(self, file_path: Path) -> str:
        """Categorize a documentation file."""
        path_str = str(file_path).lower()
        
        # Check for API documentation
        if 'api' in path_str or 'reference' in path_str or 'docs/api' in path_str:
            return 'api'
            
        # Check for guides
        if 'guide' in path_str or 'tutorial' in path_str or 'howto' in path_str:
            return 'guides'
            
        # Check for architecture
        if 'arch' in path_str or 'design' in path_str or 'structure' in path_str:
            return 'architecture'
            
        # Check for examples
        if 'example' in path_str or 'demo' in path_str or 'sample' in path_str:
            return 'examples'
            
        # Default category
        return 'other'
    
    def create_docs_structure(self):
        """Create the new documentation structure."""
        logger.info("Creating documentation structure...")
        
        # Create main directories
        for dir_name in self.doc_structure.keys():
            dir_path = self.docs_dir / dir_name
            if not dir_path.exists() and not self.dry_run:
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {dir_path.relative_to(self.project_root)}")
        
        # Create main README if it doesn't exist
        readme_path = self.docs_dir / 'README.md'
        if not readme_path.exists() and not self.dry_run:
            self._generate_main_readme(readme_path)
        
        # Create category READMEs
        for category, title in self.doc_structure.items():
            cat_readme = self.docs_dir / category / 'README.md'
            if not cat_readme.exists() and not self.dry_run:
                self._generate_category_readme(cat_readme, category, title)
    
    def _generate_main_readme(self, readme_path: Path):
        """Generate the main README for the docs directory."""
        content = """# Project Documentation

Welcome to the project documentation! This directory contains comprehensive documentation for the Resume Velvit Thunder project.

## Documentation Structure

- **API Reference**: Detailed API documentation
- **Guides**: Tutorials and how-to guides
- **Architecture**: System design and architecture decisions
- **Tutorials**: Step-by-step tutorials
- **Examples**: Code examples and snippets
- **Resources**: Additional resources and references
- **Changelog**: Release notes and version history

## Getting Started

1. Browse the documentation using the navigation menu
2. Use the search functionality to find specific topics
3. Check the [Guides](./guides/README.md) for tutorials and how-tos
4. Explore the [API Reference](./api/README.md) for detailed API documentation

## Contributing

Contributions to the documentation are welcome! Please see the [Contributing Guide](../CONTRIBUTING.md) for more information.
"""
        if not self.dry_run:
            readme_path.write_text(content, encoding='utf-8')
        logger.info(f"Generated main README: {readme_path.relative_to(self.project_root)}")
    
    def _generate_category_readme(self, readme_path: Path, category: str, title: str):
        """Generate a category README file."""
        content = f"""# {title}

This directory contains {title.lower()} documentation for the project.

## Contents

<!-- Add links to documentation files in this category -->

## Related Documentation

- [Main Documentation](../README.md)
"""
        if not self.dry_run:
            readme_path.write_text(content, encoding='utf-8')
        logger.info(f"Generated {category} README: {readme_path.relative_to(self.project_root)}")
    
    def migrate_documentation(self):
        """Migrate documentation to the new structure."""
        logger.info("Starting documentation migration...")
        
        # Create the documentation structure
        self.create_docs_structure()
        
        # Process each found documentation file
        for doc_file in self.inventory['found']:
            try:
                src_path = self.project_root / doc_file['path']
                
                # Skip files that are already in the new docs directory
                if str(src_path).startswith(str(self.docs_dir)):
                    continue
                
                # Determine target path
                target_dir = self.docs_dir / doc_file['category']
                target_path = target_dir / src_path.name
                
                # Handle naming conflicts
                counter = 1
                while target_path.exists():
                    target_path = target_dir / f"{src_path.stem}_{counter}{src_path.suffix}"
                    counter += 1
                
                # Move or copy the file
                if not self.dry_run:
                    # Create target directory if it doesn't exist
                    target_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Copy the file
                    shutil.copy2(src_path, target_path)
                    
                    # Update references if it's a markdown file
                    if doc_file['type'] == 'markdown':
                        self._update_markdown_links(target_path, src_path.parent, target_path.parent)
                
                # Record the move
                self.inventory['moved'].append({
                    'from': str(src_path.relative_to(self.project_root)),
                    'to': str(target_path.relative_to(self.project_root)),
                    'category': doc_file['category']
                })
                
                logger.info(f"Migrated: {src_path.relative_to(self.project_root)} -> {target_path.relative_to(self.project_root)}")
                
            except Exception as e:
                error_msg = f"Error migrating {doc_file['path']}: {e}"
                logger.error(error_msg)
                self.inventory['errors'].append({
                    'file': doc_file['path'],
                    'error': str(e)
                })
                self.log_to_mcp(error_msg, level='error')
        
        # Generate migration report
        self._generate_report()
        
        logger.info("Documentation migration completed!")
        self.log_to_mcp(
            "Documentation migration completed",
            metadata={
                'moved_files': len(self.inventory['moved']),
                'errors': len(self.inventory['errors'])
            }
        )
    
    def _update_markdown_links(self, file_path: Path, old_base: Path, new_base: Path):
        """Update markdown links in a file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Update relative links
            # This is a simplified version - a full implementation would need to handle more cases
            updated_content = content
            
            # Update image references
            updated_content = re.sub(
                r'(!\[[^\]]*\]\()([^:)]+\.(?:png|jpg|jpeg|gif|svg|webp))\)',
                lambda m: f"{m.group(1)}{self._update_link_path(m.group(2), old_base, new_base)}",
                updated_content,
                flags=re.IGNORECASE
            )
            
            # Update markdown links
            updated_content = re.sub(
                r'(\[([^\]]+)\]\()([^:)]+\.(?:md|markdown|mdx|txt|rst))([^)]*\))',
                lambda m: f"{m.group(1)}{self._update_link_path(m.group(3), old_base, new_base)}{m.group(4)}",
                updated_content,
                flags=re.IGNORECASE
            )
            
            if updated_content != content and not self.dry_run:
                file_path.write_text(updated_content, encoding='utf-8')
                self.inventory['updated'].append(str(file_path.relative_to(self.project_root)))
                
        except Exception as e:
            logger.warning(f"Error updating links in {file_path}: {e}")
    
    def _update_link_path(self, link_path: str, old_base: Path, new_base: Path) -> str:
        """Update a single link path."""
        # Handle absolute paths
        if link_path.startswith('/'):
            # Convert to relative path from project root
            rel_path = Path(link_path[1:])
        else:
            # Handle relative paths
            rel_old_base = old_base.relative_to(self.project_root)
            rel_path = (rel_old_base / link_path).resolve()
        
        # Make path relative to new base
        try:
            rel_to_new = os.path.relpath(
                self.project_root / rel_path,
                new_base
            ).replace('\\', '/')
            return rel_to_new
        except ValueError:
            # If the path is outside the project, return as-is
            return link_path
    
    def _generate_report(self):
        """Generate a migration report."""
        report_path = self.project_root / 'docs' / 'MIGRATION_REPORT.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Documentation Migration Report\n\n")
            f.write(f"Generated at: {self._get_timestamp()}\n\n")
            
            # Summary
            f.write("## Summary\n\n")
            f.write(f"- Total files found: {self.inventory['stats']['total_files']}\n")
            f.write(f"- Markdown files: {self.inventory['stats']['markdown_files']}\n")
            f.write(f"- Other files: {self.inventory['stats']['other_files']}\n")
            f.write(f"- Files moved: {len(self.inventory['moved'])}\n")
            f.write(f"- Files updated: {len(self.inventory['updated'])}\n")
            f.write(f"- Duplicate files found: {self.inventory['stats']['duplicates']}\n")
            f.write(f"- Outdated files: {self.inventory['stats']['outdated']}\n")
            f.write(f"- Errors: {len(self.inventory['errors'])}\n\n")
            
            # Moved files
            if self.inventory['moved']:
                f.write("## Moved Files\n\n")
                f.write("| From | To | Category |\n")
                f.write("|------|----|----------|\n")
                for item in self.inventory['moved']:
                    f.write(f"| `{item['from']}` | `{item['to']}` | {item['category']} |\n")
                f.write("\n")
            
            # Updated files
            if self.inventory['updated']:
                f.write("## Updated Files\n\n")
                for file_path in self.inventory['updated']:
                    f.write(f"- `{file_path}`\n")
                f.write("\n")
            
            # Errors
            if self.inventory['errors']:
                f.write("## Errors\n\n")
                f.write("| File | Error |\n")
                f.write("|------|-------|\n")
                for error in self.inventory['errors']:
                    f.write(f"| `{error['file']}` | `{error['error']}` |\n")
                f.write("\n")
        
        logger.info(f"Migration report generated: {report_path.relative_to(self.project_root)}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in a readable format."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Migrate and consolidate documentation.')
    parser.add_argument('--project-root', type=Path, default=Path.cwd(),
                      help='Path to the project root directory')
    parser.add_argument('--config', type=Path, help='Path to configuration file')
    parser.add_argument('--dry-run', action='store_true',
                      help='Perform a dry run without making changes')
    parser.add_argument('--scan-only', action='store_true',
                      help='Only scan for documentation files, do not migrate')
    
    args = parser.parse_args()
    
    migrator = DocumentationMigrator(
        project_root=args.project_root,
        config_path=args.config,
        dry_run=args.dry_run
    )
    
    # Scan for documentation files
    inventory = migrator.scan_documentation()
    
    # Only proceed with migration if not in scan-only mode
    if not args.scan_only:
        migrator.migrate_documentation()
    
    logger.info("Documentation processing completed!")

if __name__ == "__main__":
    main()
