#!/usr/bin/env python3
"""
Project Audit and Inventory Tool

This script performs a comprehensive audit of the project files and generates
an inventory report. It integrates with MCP servers for enhanced analysis.
"""

import os
import sys
import json
import csv
import hashlib
import logging
import platform
import socket
import argparse
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set, DefaultDict
from collections import defaultdict
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum, auto

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import MCP client
try:
    from mcp.client import MCPClient
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("MCP client not available. Running without MCP integration.")

class FileCategory(str, Enum):
    """Categories for files in the project."""
    SOURCE = "source"
    TEST = "test"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"
    BUILD_ARTIFACT = "build_artifact"
    DATA = "data"
    ASSET = "asset"
    OTHER = "other"

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
    lines_of_code: int = 0
    has_tests: bool = False
    test_coverage: Optional[float] = None
    complexity: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    referenced_by: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ProjectAuditor:
    """Class to perform project audit and inventory with MCP integration."""
    
    # File type mappings with comprehensive type detection
    SOURCE_EXTENSIONS = {
        # Python
        '.py': 'Python', '.pyi': 'Python Stub', '.pyd': 'Python Dynamic Module',
        # TypeScript/JavaScript
        '.ts': 'TypeScript', '.tsx': 'TypeScript React',
        '.js': 'JavaScript', '.jsx': 'JavaScript React',
        '.mjs': 'JavaScript Module', '.cjs': 'CommonJS',
        # Web
        '.html': 'HTML', '.htm': 'HTML', '.css': 'CSS',
        '.scss': 'SCSS', '.sass': 'SASS', '.less': 'LESS',
        # Configuration
        '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML',
        '.toml': 'TOML', '.ini': 'INI', '.env': 'Environment',
        # Documentation
        '.md': 'Markdown', '.mdx': 'MDX', '.rst': 'reStructuredText',
        # Data
        '.csv': 'CSV', '.tsv': 'TSV', '.jsonl': 'JSON Lines',
        '.sql': 'SQL', '.db': 'SQLite Database',
        # Build/Deployment
        'Dockerfile': 'Dockerfile',
        # Shell
        '.sh': 'Shell Script', '.bash': 'Bash Script',
        # Images
        '.png': 'PNG Image', '.jpg': 'JPEG Image',
        '.jpeg': 'JPEG Image', '.gif': 'GIF Image',
        '.svg': 'SVG Image', '.webp': 'WebP Image',
        # Archives
        '.zip': 'ZIP Archive', '.tar': 'TAR Archive',
        # Documents
        '.pdf': 'PDF Document', '.doc': 'Word Document',
        '.docx': 'Word Document', '.xls': 'Excel Spreadsheet',
        '.xlsx': 'Excel Spreadsheet', '.ppt': 'PowerPoint',
        '.pptx': 'PowerPoint'
    }
    
    # Test-related patterns and directories
    TEST_DIRS = {'tests', '__tests__', 'test', 'spec', 'specs'}
    TEST_FILE_PATTERNS = {
        'test_', '_test.', '.spec.', '.test.',
        '_spec.', '.specs.', 'test-', '-test-'
    }
    
    # Ignore patterns
    IGNORE_DIRS = {
        '.git', '.github', '.vscode', '.idea',
        'node_modules', '__pycache__', '.pytest_cache',
        'build', 'dist', 'out', 'target', 'bin', 'obj',
        'coverage', '.nyc_output', 'temp', 'tmp',
        'vendor', 'bower_components', '.cache',
        'logs', '.logs', 'log'
    }
    
    IGNORE_PATTERNS = {
        '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.dylib',
        '*.class', '*.jar', '*.war', '*.ear', '*.o', '*.a',
        '*.lib', '*.dll', '*.so', '*.dylib', '*.obj', '*.exe',
        '*.bin', '*.dat', '*.data', '*.db', '*.sqlite', '*.sqlite3',
        '*.log', '*.lock', '*.swp', '*.swo', '*.swn', '*.swo',
        '*.DS_Store', 'Thumbs.db', 'desktop.ini'
    }
    
    def __init__(self, root_dirs: List[str], mcp_config: Optional[Dict] = None):
        """Initialize the auditor with root directories to scan and MCP configuration."""
        self.root_dirs = [Path(d).resolve() for d in root_dirs]
        self.files: Dict[str, FileInfo] = {}
        self.duplicates: Dict[str, List[str]] = {}
        self.file_hashes: Dict[str, str] = {}
        
        # MCP Integration
        self.mcp_enabled = MCP_AVAILABLE and mcp_config and mcp_config.get('enabled', False)
        self.mcp_client = None
        self.mcp_collection = mcp_config.get('collection', 'project_audit') if mcp_config else 'project_audit'
        
        if self.mcp_enabled:
            try:
                self.mcp_client = MCPClient(
                    server_url=mcp_config.get('server_url', 'http://localhost:8000'),
                    api_key=mcp_config.get('api_key', ''),
                    project_id=mcp_config.get('project_id', 'resume-velvit-thunder')
                )
                logger.info(f"MCP client initialized with collection: {self.mcp_collection}")
            except Exception as e:
                logger.error(f"Failed to initialize MCP client: {e}")
                self.mcp_enabled = False
    
    def log_to_mcp(self, message: str, level: str = 'info', metadata: Optional[Dict] = None) -> None:
        """Log a message to MCP if available."""
        if self.mcp_enabled and self.mcp_client:
            try:
                self.mcp_client.log(
                    message=message,
                    level=level,
                    metadata=metadata or {},
                    collection=self.mcp_collection
                )
            except Exception as e:
                logger.warning(f"Failed to log to MCP: {e}")
    
    def get_file_category(self, filepath: Path) -> str:
        """Determine the category of a file."""
        # Check for test files
        if (any(part in self.TEST_DIRS for part in filepath.parts) or
            any(pattern in filepath.name for pattern in self.TEST_FILE_PATTERNS)):
            return FileCategory.TEST
            
        # Check for documentation
        doc_extensions = {'.md', '.rst', '.txt', '.pdf', '.adoc', '.tex'}
        if filepath.suffix.lower() in doc_extensions:
            return FileCategory.DOCUMENTATION
            
        # Check for configuration
        config_extensions = {'.json', '.yaml', '.yml', '.toml', '.ini', '.env', '.properties', '.cfg'}
        if (filepath.suffix.lower() in config_extensions or 
            filepath.name in {'.gitignore', '.gitattributes', '.gitmodules'}):
            return FileCategory.CONFIGURATION
            
        # Check for source code
        source_extensions = {
            '.py', '.pyi', '.pyx', '.pxd', '.pyd',
            '.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs',
            '.html', '.htm', '.css', '.scss', '.sass', '.less',
            '.c', '.h', '.cpp', '.hpp', '.cc', '.cxx', '.hxx',
            '.java', '.kt', '.kts', '.scala', '.go', '.rs',
            '.rb', '.php', '.swift', '.m', '.mm', '.dart',
            '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd'
        }
        if filepath.suffix.lower() in source_extensions:
            return FileCategory.SOURCE
            
        # Check for build artifacts
        if any(part in self.IGNORE_DIRS for part in filepath.parts):
            return FileCategory.BUILD_ARTIFACT
            
        # Check for data files
        data_extensions = {'.csv', '.tsv', '.jsonl', '.sql', '.db', '.sqlite', '.sqlite3', '.xls', '.xlsx', '.ods'}
        if filepath.suffix.lower() in data_extensions:
            return FileCategory.DATA
            
        # Check for assets
        asset_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico',
            '.mp3', '.wav', '.ogg', '.mp4', '.webm', '.mov', '.avi',
            '.woff', '.woff2', '.ttf', '.eot', '.otf'
        }
        if filepath.suffix.lower() in asset_extensions:
            return FileCategory.ASSET
            
        return FileCategory.OTHER
    
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
    
    def count_lines_of_code(self, filepath: Path) -> int:
        """Count the number of lines of code in a file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except (UnicodeDecodeError, IOError):
            return 0
    
    def scan_directory(self, directory: Path) -> None:
        """Recursively scan a directory and collect file information."""
        logger.info(f"Scanning directory: {directory}")
        
        for item in directory.rglob('*'):
            try:
                # Skip ignored directories
                if any(part in self.IGNORE_DIRS for part in item.parts):
                    continue
                    
                # Skip ignored patterns
                if any(item.match(pattern) for pattern in self.IGNORE_PATTERNS):
                    continue
                    
                if item.is_file() and not item.is_symlink():
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
                    
                    # Calculate hash and LOC for non-binary files
                    if file_info.size_bytes < 10 * 1024 * 1024:  # Skip files larger than 10MB
                        file_info.md5_hash = self.calculate_md5(item)
                        
                        # Count lines of code for text files
                        if file_info.category in {FileCategory.SOURCE, FileCategory.TEST, 
                                              FileCategory.CONFIGURATION, FileCategory.DOCUMENTATION}:
                            file_info.lines_of_code = self.count_lines_of_code(item)
                        
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
                self.log_to_mcp(
                    f"Error processing {item}",
                    level='error',
                    metadata={'error': str(e), 'file': str(item)}
                )
    
    def analyze_references(self) -> None:
        """Analyze file references between files."""
        logger.info("Analyzing file references...")
        
        source_files = [
            (path, info) for path, info in self.files.items() 
            if info.category in (FileCategory.SOURCE, FileCategory.CONFIGURATION, FileCategory.TEST)
        ]
        
        for path, file_info in source_files:
            try:
                with open(Path(file_info.path), 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Look for imports/requires/references to other files
                    for ref_path, ref_info in self.files.items():
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
                'hostname': socket.gethostname(),
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'total_files_scanned': len(self.files),
            },
            'summary': {
                'by_type': {},
                'by_category': {},
                'largest_files': [],
                'oldest_files': [],
                'unreferenced_files': [],
                'duplicate_files': [
                    {'hash': h, 'files': files, 'size_mb': 0}
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
            if (not file_info.referenced_by and 
                file_info.category in (FileCategory.SOURCE, FileCategory.CONFIGURATION)):
                report['summary']['unreferenced_files'].append({
                    'path': file_info.path,
                    'type': file_info.file_type,
                    'category': file_info.category,
                    'size_mb': round(file_info.size_bytes / (1024 * 1024), 2)
                })
        
        # Calculate duplicate sizes
        for dup in report['summary']['duplicate_files']:
            if dup['files']:
                file_path = dup['files'][0]
                if file_path in self.files:
                    dup['size_mb'] = round(self.files[file_path].size_bytes / (1024 * 1024), 2)
        
        # Write JSON report
        json_path = output_path / f'project_audit_{timestamp}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        # Generate HTML report
        self._generate_html_report(report, output_path / f'project_audit_{timestamp}.html')
        
        # Generate CSV for spreadsheet analysis
        csv_path = output_path / f'file_inventory_{timestamp}.csv'
        self._generate_csv_report(report, csv_path)
        
        # Log to MCP
        self.log_to_mcp(
            "Project audit completed",
            level='info',
            metadata={
                'report_path': str(json_path),
                'total_files': len(self.files),
                'file_types': len(report['summary']['by_type']),
                'duplicates_found': len(report['summary']['duplicate_files'])
            }
        )
        
        logger.info(f"Audit report generated at {json_path}")
        return report
    
    def _get_recently_modified_files(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get files modified in the last N days."""
        cutoff = time.time() - (days * 24 * 60 * 60)
        recent_files = [
            {
                'path': f.path,
                'name': Path(f.path).name,
                'last_modified': datetime.fromtimestamp(f.last_modified).strftime('%Y-%m-%d %H:%M:%S'),
                'days_ago': int((time.time() - f.last_modified) / (24 * 60 * 60)),
                'size_mb': round(f.size_bytes / (1024 * 1024), 2),
                'type': f.file_type,
                'category': f.category
            }
            for f in self.files.values() 
            if f.last_modified >= cutoff
        ]
        return sorted(recent_files, key=lambda x: x['last_modified'], reverse=True)[:50]

    def _get_file_type_stats(self, files: List[Dict]) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics for file types."""
        type_stats = {}
        for file_info in files:
            f_type = file_info.get('type', 'Unknown')
            if f_type not in type_stats:
                type_stats[f_type] = {
                    'count': 0,
                    'total_size': 0,
                    'extensions': defaultdict(int)
                }
            type_stats[f_type]['count'] += 1
            type_stats[f_type]['total_size'] += file_info.get('size_mb', 0)
            
            # Track extensions for this file type
            ext = Path(file_info.get('path', '')).suffix.lower()
            if ext:
                type_stats[f_type]['extensions'][ext] += 1
        
        # Calculate average size and sort extensions
        for f_type, stats in type_stats.items():
            stats['avg_size'] = stats['total_size'] / stats['count'] if stats['count'] > 0 else 0
            stats['extensions'] = dict(sorted(
                stats['extensions'].items(), 
                key=lambda x: x[1], 
                reverse=True
            ))
        
        return type_stats

    def _generate_html_report(self, report: Dict[str, Any], output_path: Path) -> None:
        """Generate an HTML version of the report."""
        try:
            from jinja2 import Environment, FileSystemLoader
            
            # Set up Jinja2 environment
            env = Environment(loader=FileSystemLoader(Path(__file__).parent / 'templates'))
            template = env.get_template('audit_report.html')
            
            # Calculate additional statistics
            file_list = [asdict(f) for f in self.files.values()]
            file_type_stats = self._get_file_type_stats(file_list)
            recently_modified = self._get_recently_modified_files()
            
            # Calculate category distribution
            category_distribution = [
                {'category': cat, 'count': count, 'percentage': (count / len(file_list)) * 100}
                for cat, count in report['summary']['by_category'].items()
            ]
            
            # Calculate type distribution
            type_distribution = [
                {'type': t, 'count': c, 'percentage': (c / len(file_list)) * 100}
                for t, c in report['summary']['by_type'].items()
            ]
            
            # Prepare data for charts
            chart_data = {
                'categories': {
                    'labels': list(report['summary']['by_category'].keys()),
                    'data': list(report['summary']['by_category'].values()),
                    'colors': [
                        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', 
                        '#e74a3b', '#858796', '#5a5c69', '#e83e8c',
                        '#20c9a6', '#fd7e14', '#6f42c1', '#6c757d'
                    ]
                },
                'types': {
                    'labels': list(report['summary']['by_type'].keys()),
                    'data': list(report['summary']['by_type'].values()),
                    'colors': [
                        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', 
                        '#e74a3b', '#858796', '#5a5c69', '#e83e8c',
                        '#20c9a6', '#fd7e14', '#6f42c1', '#6c757d'
                    ]
                }
            }
            
            # Calculate total size by category
            size_by_category = {}
            for file_info in file_list:
                category = file_info.get('category', 'other')
                size_mb = file_info.get('size_bytes', 0) / (1024 * 1024)
                if category not in size_by_category:
                    size_by_category[category] = 0
                size_by_category[category] += size_mb
            
            # Sort files by size for the largest files table
            largest_files = sorted(
                file_list,
                key=lambda x: x.get('size_bytes', 0),
                reverse=True
            )[:50]  # Top 50 largest files
            
            # Prepare context for template
            context = {
                # Metadata
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'scanned_dirs': report['metadata']['scanned_directories'],
                'total_files': report['metadata']['total_files_scanned'],
                'total_size_mb': sum(f.get('size_bytes', 0) for f in file_list) / (1024 * 1024),
                'hostname': report['metadata'].get('hostname', 'N/A'),
                'platform': report['metadata'].get('platform', 'N/A'),
                
                # Statistics
                'by_type': report['summary']['by_type'],
                'by_category': report['summary']['by_category'],
                'category_distribution': category_distribution,
                'type_distribution': type_distribution,
                'file_type_stats': file_type_stats,
                'size_by_category': size_by_category,
                
                # File lists
                'largest_files': [
                    {**f, 'size_mb': round(f.get('size_bytes', 0) / (1024 * 1024), 2)}
                    for f in largest_files
                ],
                'oldest_files': report['summary']['oldest_files'],
                'recently_modified': recently_modified,
                'unreferenced_files': report['summary']['unreferenced_files'],
                'duplicate_files': report['summary']['duplicate_files'],
                
                # Chart data
                'chart_data': chart_data,
                
                # Additional metadata
                'source_files': report['summary']['by_category'].get('source', 0),
                'documentation_files': report['summary']['by_category'].get('documentation', 0),
                'test_files': report['summary']['by_category'].get('test', 0),
                'asset_files': report['summary']['by_category'].get('asset', 0),
                'configuration_files': report['summary']['by_category'].get('configuration', 0),
                'build_artifact_files': report['summary']['by_category'].get('build_artifact', 0),
                'data_files': report['summary']['by_category'].get('data', 0),
                'other_files': report['summary']['by_category'].get('other', 0),
                
                # Duplicate files info
                'total_duplicate_groups': len(report['summary']['duplicate_files']),
                'total_duplicate_files': sum(len(g['files']) for g in report['summary']['duplicate_files']),
                'duplicate_size_mb': sum(g.get('size_mb', 0) * (len(g.get('files', [])) - 1) 
                                      for g in report['summary']['duplicate_files']),
                
                # Unreferenced files info
                'total_unreferenced_files': len(report['summary']['unreferenced_files']),
                'unreferenced_size_mb': sum(f.get('size_mb', 0) 
                                         for f in report['summary']['unreferenced_files']),
                
                # File type specific stats
                'python_files': report['summary']['by_type'].get('Python', 0),
                'javascript_files': report['summary']['by_type'].get('JavaScript', 0) + \
                                  report['summary']['by_type'].get('TypeScript', 0),
                'html_files': report['summary']['by_type'].get('HTML', 0),
                'css_files': report['summary']['by_type'].get('CSS', 0) + \
                            report['summary']['by_type'].get('SCSS', 0) + \
                            report['summary']['by_type'].get('SASS', 0) + \
                            report['summary']['by_type'].get('LESS', 0),
                'image_files': sum(
                    report['summary']['by_type'].get(img_type, 0) 
                    for img_type in ['PNG Image', 'JPEG Image', 'GIF Image', 'SVG Image', 'WebP Image']
                ),
                'document_files': sum(
                    report['summary']['by_type'].get(doc_type, 0)
                    for doc_type in ['PDF Document', 'Word Document', 'Excel Spreadsheet', 'PowerPoint']
                ),
                'archive_files': sum(
                    report['summary']['by_type'].get(arch_type, 0)
                    for arch_type in ['ZIP Archive', 'TAR Archive']
                )
            }
            
            # Render template with the complete context
            html_content = template.render(**context)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            logger.info(f"HTML report generated at {output_path}")
                
        except ImportError:
            logger.warning("Jinja2 not installed, skipping HTML report generation")
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}", exc_info=True)
            
    def _generate_csv_report(self, report: Dict[str, Any], output_path: Path) -> None:
        """Generate a CSV version of the file inventory."""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'path', 'name', 'extension', 'file_type', 'category',
                    'size_mb', 'last_modified', 'lines_of_code', 
                    'has_tests', 'test_coverage', 'complexity',
                    'dependencies', 'references', 'referenced_by', 'tags'
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
                    row['dependencies'] = ', '.join(row.get('dependencies', []))
                    row['references'] = ', '.join(row.get('references', []))
                    row['referenced_by'] = ', '.join(row.get('referenced_by', []))
                    row['tags'] = ', '.join(row.get('tags', []))
                    # Remove unused fields
                    for field in ['size_bytes', 'md5_hash', 'metadata']:
                        row.pop(field, None)
                    writer.writerow(row)
                    
        except Exception as e:
            logger.error(f"Error generating CSV report: {e}")


def main():
    """Main function to run the project audit."""
    parser = argparse.ArgumentParser(description='Project Audit and Inventory Tool')
    parser.add_argument('directories', nargs='+', help='Directories to audit')
    parser.add_argument('--output', '-o', default='reports', help='Output directory for reports')
    parser.add_argument('--mcp', action='store_true', help='Enable MCP integration')
    parser.add_argument('--mcp-url', default='http://localhost:8000', help='MCP server URL')
    parser.add_argument('--mcp-key', default='', help='MCP API key')
    parser.add_argument('--mcp-collection', default='project_audit', help='MCP collection name')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # MCP configuration
    mcp_config = {
        'enabled': args.mcp and MCP_AVAILABLE,
        'server_url': args.mcp_url,
        'api_key': args.mcp_key,
        'collection': args.mcp_collection
    }
    
    # Create and run auditor
    auditor = ProjectAuditor(args.directories, mcp_config=mcp_config)
    
    # Log start of audit
    auditor.log_to_mcp(
        f"Starting project audit of {len(args.directories)} directories",
        level='info',
        metadata={'directories': args.directories}
    )
    
    # Scan directories
    start_time = time.time()
    for directory in args.directories:
        auditor.scan_directory(Path(directory))
    
    # Analyze references
    auditor.analyze_references()
    
    # Generate report
    report = auditor.generate_report(args.output)
    
    # Print summary
    duration = time.time() - start_time
    print("\n=== Audit Summary ===")
    print(f"Scanned {len(auditor.files)} files in {len(args.directories)} directories")
    print(f"Time taken: {duration:.2f} seconds")
    
    print("\nFile types:")
    for ftype, count in sorted(report['summary']['by_type'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {ftype}: {count}")
    
    print("\nCategories:")
    for category, count in sorted(report['summary']['by_category'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count}")
    
    print(f"\nReport generated in {args.output}")


if __name__ == '__main__':
    main()
