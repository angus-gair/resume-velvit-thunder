#!/usr/bin/env python3
"""
Task #82: Comprehensive Project Audit and Inventory

This script performs a complete audit of the project files and generates:
1. An inventory spreadsheet with file details
2. A file status report
3. A summary of findings
"""

import os
import sys
import csv
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass, asdict, field

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class FileInfo:
    """Class to store file information."""
    path: str
    name: str
    extension: str
    size_bytes: int
    last_modified: float
    file_type: str = ""
    category: str = ""
    md5_hash: str = ""
    references: List[str] = field(default_factory=list)
    referenced_by: List[str] = field(default_factory=list)
    status: str = "active"
    notes: str = ""

class ProjectAuditor:
    """Class to perform project audit and inventory."""
    
    # File type mappings
    SOURCE_EXTENSIONS = {
        # Python
        '.py': 'Python',
        # TypeScript/JavaScript
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript',
        '.js': 'JavaScript',
        '.jsx': 'JavaScript',
        # HTML/CSS
        '.html': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        # Configuration
        '.json': 'JSON',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.toml': 'TOML',
        '.ini': 'INI',
        '.env': 'Environment',
        # Documentation
        '.md': 'Markdown',
        '.rst': 'reStructuredText',
        '.txt': 'Text',
        '.pdf': 'PDF',
        # Data
        '.csv': 'CSV',
        '.sql': 'SQL',
        # Images
        '.png': 'Image',
        '.jpg': 'Image',
        '.jpeg': 'Image',
        '.gif': 'Image',
        '.svg': 'Vector Image',
    }
    
    # Test directories and file patterns
    TEST_DIRS = {'tests', '__tests__', 'test'}
    TEST_FILE_PATTERNS = {'test_', '_test.', '.spec.', '.test.'}
    
    # Build/artifact directories to exclude
    EXCLUDE_DIRS = {
        '__pycache__', '.pytest_cache', 'node_modules', 'dist', 'build',
        '.git', '.github', '.vscode', '.idea', 'venv', 'env', '.venv',
        'coverage', '.coverage', 'htmlcov', '.mypy_cache', '.ruff_cache'
    }
    
    # File patterns to exclude
    EXCLUDE_PATTERNS = {'*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.dylib',
                      '*.o', '*.obj', '*.a', '*.lib', '*.exe', '*.dll', '*.so.*',
                      '*.class', '*.jar', '*.war', '*.ear', '*.zip', '*.tar.gz',
                      '*.tar', '*.tgz', '*.7z', '*.dmg', '*.pkg', '*.deb',
                      '*.rpm', '*.msi', '*.bak', '*.swp', '*.swo', '*.swn',
                      '*.swo', '*.swp', '*.swn', '*.DS_Store', 'Thumbs.db',
                      'desktop.ini', '*.log', '*.tmp', '*.temp', '*.cache'}
    
    def __init__(self, root_dirs: List[str]):
        """Initialize the auditor with root directories to scan."""
        self.root_dirs = [Path(d).resolve() for d in root_dirs]
        self.files: Dict[str, FileInfo] = {}
        self.duplicates: Dict[str, List[str]] = {}
        self.file_hashes: Dict[str, str] = {}
        self.file_extensions: Dict[str, int] = {}
        self.categories: Dict[str, int] = {}
        self.file_types: Dict[str, int] = {}
        
    def should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded from the audit."""
        # Check if any part of the path matches exclude dirs
        if any(part in self.EXCLUDE_DIRS for part in path.parts):
            return True
            
        # Check file patterns
        if any(path.match(pattern) for pattern in self.EXCLUDE_PATTERNS):
            return True
            
        return False
    
    def get_file_category(self, filepath: Path) -> str:
        """Determine the category of a file."""
        # Check for test files
        if any(part in self.TEST_DIRS for part in filepath.parts):
            return 'test'
            
        if any(pattern in filepath.name for pattern in self.TEST_FILE_PATTERNS):
            return 'test'
            
        # Check for documentation
        if filepath.suffix in {'.md', '.rst', '.txt', '.pdf', '.html'}:
            return 'documentation'
            
        # Check for configuration
        if filepath.suffix in {'.json', '.yaml', '.yml', '.toml', '.ini', '.env'}:
            return 'configuration'
            
        # Check for source code
        if filepath.suffix in self.SOURCE_EXTENSIONS:
            return 'source'
            
        # Check for build artifacts
        build_dirs = {'dist', 'build', 'node_modules', '__pycache__', '.pytest_cache'}
        if any(part in build_dirs for part in filepath.parts):
            return 'build_artifact'
            
        return 'other'
    
    def calculate_md5(self, filepath: Path) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (IOError, PermissionError) as e:
            logger.warning(f"Could not read {filepath}: {e}")
            return ""
    
    def scan_directory(self, directory: Path) -> None:
        """Recursively scan a directory and collect file information."""
        logger.info(f"Scanning directory: {directory}")
        
        for item in directory.rglob('*'):
            try:
                if self.should_exclude(item):
                    continue
                    
                if item.is_file():
                    # Skip symlinks
                    if item.is_symlink():
                        continue
                        
                    # Get file stats
                    stat = item.stat()
                    
                    # Create file info
                    rel_path = str(item.relative_to(directory.parent))
                    file_info = FileInfo(
                        path=rel_path,
                        name=item.name,
                        extension=item.suffix.lower(),
                        size_bytes=stat.st_size,
                        last_modified=stat.st_mtime,
                        file_type=self.SOURCE_EXTENSIONS.get(item.suffix.lower(), 'Unknown'),
                        category=self.get_file_category(item),
                    )
                    
                    # Track file types and categories
                    self.file_extensions[item.suffix.lower()] = self.file_extensions.get(item.suffix.lower(), 0) + 1
                    self.categories[file_info.category] = self.categories.get(file_info.category, 0) + 1
                    self.file_types[file_info.file_type] = self.file_types.get(file_info.file_type, 0) + 1
                    
                    # Calculate hash for non-binary files
                    if file_info.size_bytes < 10 * 1024 * 1024:  # Skip files larger than 10MB
                        file_info.md5_hash = self.calculate_md5(item)
                        
                        # Check for duplicates
                        if file_info.md5_hash:
                            if file_info.md5_hash in self.file_hashes:
                                if file_info.md5_hash not in self.duplicates:
                                    self.duplicates[file_info.md5_hash] = [self.file_hashes[file_info.md5_hash]]
                                self.duplicates[file_info.md5_hash].append(rel_path)
                            else:
                                self.file_hashes[file_info.md5_hash] = rel_path
                    
                    self.files[rel_path] = file_info
                    
            except Exception as e:
                logger.error(f"Error processing {item}: {e}")
    
    def analyze_file_status(self) -> None:
        """Analyze file status based on modification time and references."""
        logger.info("Analyzing file status...")
        
        current_time = time.time()
        six_months_ago = current_time - (180 * 24 * 60 * 60)  # 180 days in seconds
        
        for file_info in self.files.values():
            # Check for potentially outdated files (not modified in 6 months)
            if file_info.last_modified < six_months_ago:
                file_info.status = "potentially_outdated"
                file_info.notes = "Not modified in the last 6 months"
            
            # Check for orphaned files (not referenced by any other file)
            if not file_info.referenced_by and file_info.category not in ['documentation', 'configuration']:
                if file_info.status == "active":
                    file_info.status = "potentially_orphaned"
                    file_info.notes = "Not referenced by any other files"
    
    def generate_inventory_csv(self, output_dir: Path) -> Path:
        """Generate a CSV inventory of all files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"file_inventory_{timestamp}.csv"
        
        logger.info(f"Generating inventory CSV: {output_file}")
        
        fieldnames = [
            'path', 'name', 'extension', 'file_type', 'category',
            'size_bytes', 'last_modified', 'status', 'notes',
            'reference_count', 'referenced_by_count', 'md5_hash'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for file_info in self.files.values():
                row = {
                    'path': file_info.path,
                    'name': file_info.name,
                    'extension': file_info.extension,
                    'file_type': file_info.file_type,
                    'category': file_info.category,
                    'size_bytes': file_info.size_bytes,
                    'last_modified': datetime.fromtimestamp(file_info.last_modified).strftime('%Y-%m-%d %H:%M:%S'),
                    'status': file_info.status,
                    'notes': file_info.notes,
                    'reference_count': len(file_info.references),
                    'referenced_by_count': len(file_info.referenced_by),
                    'md5_hash': file_info.md5_hash
                }
                writer.writerow(row)
        
        return output_file
    
    def generate_summary_report(self, output_dir: Path) -> Path:
        """Generate a summary report of the audit findings."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"audit_summary_{timestamp}.md"
        
        logger.info(f"Generating summary report: {output_file}")
        
        # Count files by status
        status_counts = {}
        for file_info in self.files.values():
            status_counts[file_info.status] = status_counts.get(file_info.status, 0) + 1
        
        # Generate report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Project Audit Summary\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary Statistics
            f.write("## Summary Statistics\n\n")
            f.write(f"- **Total Files Scanned:** {len(self.files)}\n")
            f.write(f"- **Unique File Types:** {len(self.file_types)}\n")
            f.write(f"- **Duplicate Files Found:** {len(self.duplicates)}\n\n")
            
            # File Status
            f.write("## File Status\n\n")
            for status, count in status_counts.items():
                f.write(f"- **{status.replace('_', ' ').title()}:** {count} files\n")
            f.write("\n")
            
            # File Categories
            f.write("## File Categories\n\n")
            for category, count in sorted(self.categories.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{category.title()}:** {count} files\n")
            f.write("\n")
            
            # File Types
            f.write("## File Types\n\n")
            for ext, count in sorted(self.file_extensions.items(), key=lambda x: x[1], reverse=True)[:20]:  # Top 20
                if ext:  # Skip empty extensions
                    f.write(f"- **{ext or 'No Extension'}:** {count} files\n")
            f.write("\n")
            
            # Duplicate Files
            if self.duplicates:
                f.write("## Duplicate Files\n\n")
                f.write("The following files have identical content (MD5 hash):\n\n")
                for hash_val, files in self.duplicates.items():
                    f.write(f"### Hash: `{hash_val[:8]}...`\n")
                    for file_path in files:
                        f.write(f"- `{file_path}`\n")
                    f.write("\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            f.write("1. **Review Potentially Outdated Files**\n")
            f.write("   - Consider archiving or removing files not modified in the last 6 months\n\n")
            f.write("2. **Address Orphaned Files**\n")
            f.write("   - Review files that aren't referenced by any other files\n\n")
            f.write("3. **Consolidate Duplicate Files**\n")
            f.write("   - Remove or consolidate duplicate files to reduce redundancy\n\n")
            f.write("4. **Standardize File Organization**\n")
            f.write("   - Consider reorganizing files to follow a consistent structure\n")
        
        return output_file
    
    def run_audit(self) -> Dict[str, Any]:
        """Run the complete audit process."""
        logger.info("Starting project audit...")
        
        # Scan all directories
        for directory in self.root_dirs:
            if directory.exists() and directory.is_dir():
                self.scan_directory(directory)
        
        # Analyze file status
        self.analyze_file_status()
        
        # Create output directory
        output_dir = Path("audit_reports")
        output_dir.mkdir(exist_ok=True)
        
        # Generate reports
        inventory_csv = self.generate_inventory_csv(output_dir)
        summary_report = self.generate_summary_report(output_dir)
        
        logger.info(f"Audit complete. Reports generated in: {output_dir}")
        
        return {
            'inventory': str(inventory_csv),
            'summary': str(summary_report),
            'file_count': len(self.files),
            'duplicate_count': len(self.duplicates),
            'file_types': len(self.file_types),
            'categories': len(self.categories)
        }

def main():
    """Main function to run the audit."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Project Audit Tool')
    parser.add_argument('directories', nargs='+', help='Directories to audit')
    parser.add_argument('--output', '-o', default='audit_reports', help='Output directory for reports')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Run audit
    auditor = ProjectAuditor(args.directories)
    results = auditor.run_audit()
    
    print(f"\nAudit completed successfully!")
    print(f"- Files scanned: {results['file_count']}")
    print(f"- File types: {results['file_types']}")
    print(f"- Duplicate files found: {results['duplicate_count']}")
    print(f"\nReports generated:")
    print(f"- Inventory: {results['inventory']}")
    print(f"- Summary: {results['summary']}")

if __name__ == '__main__':
    import time
    main()
