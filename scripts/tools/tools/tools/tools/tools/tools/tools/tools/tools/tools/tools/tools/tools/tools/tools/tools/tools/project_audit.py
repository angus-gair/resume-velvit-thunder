#!/usr/bin/env python3
"""
Project Audit and Inventory Tool

This script performs a comprehensive audit of the project files and generates
an inventory report. It integrates with MCP servers for enhanced analysis.
"""

import os
import csv
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict, field
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
        # Documentation
        '.md': 'Markdown',
        '.rst': 'reStructuredText',
        '.txt': 'Text',
        # Data
        '.csv': 'CSV',
        '.sql': 'SQL',
    }
    
    TEST_DIRS = {'tests', '__tests__', 'test'}
    TEST_FILE_PATTERNS = {'test_', '_test.', '.spec.', '.test.'}
    
    def __init__(self, root_dirs: List[str]):
        """Initialize the auditor with root directories to scan."""
        self.root_dirs = [Path(d).resolve() for d in root_dirs]
        self.files: Dict[str, FileInfo] = {}
        self.duplicates: Dict[str, List[str]] = {}
        self.file_hashes: Dict[str, str] = {}
        
    def get_file_category(self, filepath: Path) -> str:
        """Determine the category of a file."""
        rel_path = str(filepath).lower()
        
        # Check for test files
        if any(part in self.TEST_DIRS for part in filepath.parts):
            return 'test'
            
        if any(pattern in filepath.name for pattern in self.TEST_FILE_PATTERNS):
            return 'test'
            
        # Check for documentation
        if filepath.suffix in {'.md', '.rst', '.txt', '.pdf'}:
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
    
    def analyze_references(self) -> None:
        """Analyze file references between files."""
        logger.info("Analyzing file references...")
        
        source_files = [
            (path, info) for path, info in self.files.items() 
            if info.category in ('source', 'configuration')
        ]
        
        for path, file_info in source_files:
            try:
                with open(Path(file_info.path), 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Look for imports/requires/references to other files
                    for ref_path in self.files:
                        if ref_path == path:
                            continue
                            
                        ref_name = Path(ref_path).name
                        if ref_name in content:
                            # Simple check - could be enhanced with AST parsing
                            file_info.references.append(ref_path)
                            self.files[ref_path].referenced_by.append(path)
                            
            except (UnicodeDecodeError, IOError) as e:
                logger.warning(f"Could not read {path} for reference analysis: {e}")
    
    def generate_report(self, output_dir: str = "reports") -> Dict[str, Any]:
        """Generate audit report."""
        logger.info("Generating audit report...")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Prepare report data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report = {
            'metadata': {
                'timestamp': timestamp,
                'scanned_directories': [str(d) for d in self.root_dirs],
                'total_files_scanned': len(self.files),
            },
            'summary': {
                'by_type': {},
                'by_category': {},
                'largest_files': [],
                'oldest_files': [],
                'unreferenced_files': [],
                'duplicate_files': [
                    {'hash': h, 'files': files}
                    for h, files in self.duplicates.items()
                ]
            },
            'files': [asdict(f) for f in self.files.values()]
        }
        
        # Generate statistics
        for file_info in self.files.values():
            # Count by type
            report['summary']['by_type'][file_info.file_type] = \
                report['summary']['by_type'].get(file_info.file_type, 0) + 1
                
            # Count by category
            report['summary']['by_category'][file_info.category] = \
                report['summary']['by_category'].get(file_info.category, 0) + 1
        
        # Find largest files
        largest = sorted(
            self.files.values(),
            key=lambda x: x.size_bytes,
            reverse=True
        )[:20]
        report['summary']['largest_files'] = [
            {
                'path': f.path,
                'size_mb': round(f.size_bytes / (1024 * 1024), 2),
                'type': f.file_type,
                'category': f.category
            }
            for f in largest
        ]
        
        # Find oldest files
        oldest = sorted(
            self.files.values(),
            key=lambda x: x.last_modified
        )[:20]
        report['summary']['oldest_files'] = [
            {
                'path': f.path,
                'last_modified': datetime.fromtimestamp(f.last_modified).strftime('%Y-%m-%d'),
                'type': f.file_type,
                'category': f.category
            }
            for f in oldest
        ]
        
        # Find unreferenced files
        for file_info in self.files.values():
            if not file_info.referenced_by and file_info.category in ('source', 'configuration'):
                report['summary']['unreferenced_files'].append({
                    'path': file_info.path,
                    'type': file_info.file_type,
                    'category': file_info.category,
                    'size_mb': round(file_info.size_bytes / (1024 * 1024), 2)
                })
        
        # Write JSON report
        json_path = output_path / f'project_audit_{timestamp}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        # Generate HTML report
        self._generate_html_report(report, output_path / f'project_audit_{timestamp}.html')
        
        # Generate CSV for spreadsheet analysis
        csv_path = output_path / f'file_inventory_{timestamp}.csv'
        self._generate_csv_report(report, csv_path)
        
        logger.info(f"Audit report generated at {json_path}")
        return report
    
    def _generate_html_report(self, report: Dict[str, Any], output_path: Path) -> None:
        """Generate an HTML version of the report."""
        try:
            from jinja2 import Environment, FileSystemLoader
            
            # Set up Jinja2 environment
            env = Environment(loader=FileSystemLoader(Path(__file__).parent / 'templates'))
            template = env.get_template('audit_report.html')
            
            # Render template
            html_content = template.render(
                timestamp=report['metadata']['timestamp'],
                scanned_dirs=report['metadata']['scanned_directories'],
                total_files=report['metadata']['total_files_scanned'],
                by_type=report['summary']['by_type'],
                by_category=report['summary']['by_category'],
                largest_files=report['summary']['largest_files'],
                oldest_files=report['summary']['oldest_files'],
                unreferenced_files=report['summary']['unreferenced_files'],
                duplicate_files=report['summary']['duplicate_files']
            )
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        except ImportError:
            logger.warning("Jinja2 not installed, skipping HTML report generation")
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            
    def _generate_csv_report(self, report: Dict[str, Any], output_path: Path) -> None:
        """Generate a CSV version of the file inventory."""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'path', 'name', 'extension', 'file_type', 'category',
                    'size_mb', 'last_modified', 'references', 'referenced_by'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for file_info in report['files']:
                    row = file_info.copy()
                    # Convert size to MB
                    row['size_mb'] = round(row['size_bytes'] / (1024 * 1024), 4)
                    # Format last modified date
                    row['last_modified'] = datetime.fromtimestamp(row['last_modified']).strftime('%Y-%m-%d %H:%M:%S')
                    # Convert lists to strings
                    row['references'] = ', '.join(row['references'])
                    row['referenced_by'] = ', '.join(row['referenced_by'])
                    # Remove unused fields
                    for field in ['size_bytes', 'md5_hash']:
                        row.pop(field, None)
                    writer.writerow(row)
                    
        except Exception as e:
            logger.error(f"Error generating CSV report: {e}")

def main():
    """Main function to run the project audit."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Project Audit and Inventory Tool')
    parser.add_argument('directories', nargs='+', help='Directories to audit')
    parser.add_argument('--output', '-o', default='reports', help='Output directory for reports')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Create and run auditor
    auditor = ProjectAuditor(args.directories)
    
    # Scan directories
    for directory in args.directories:
        auditor.scan_directory(Path(directory))
    
    # Analyze references
    auditor.analyze_references()
    
    # Generate report
    report = auditor.generate_report(args.output)
    
    # Print summary
    print("\n=== Audit Summary ===")
    print(f"Scanned {len(auditor.files)} files in {len(args.directories)} directories")
    print("\nFile types:")
    for ftype, count in report['summary']['by_type'].items():
        print(f"  {ftype}: {count}")
    
    print("\nCategories:")
    for category, count in report['summary']['by_category'].items():
        print(f"  {category}: {count}")
    
    print(f"\nReport generated in {args.output}")

if __name__ == '__main__':
    main()
