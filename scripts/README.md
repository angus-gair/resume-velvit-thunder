# Project Audit Tool

This tool performs a comprehensive audit of project files and generates detailed reports about the project structure, file types, sizes, and relationships.

## Features

- Scans directories recursively to inventory all files
- Categorizes files by type (source code, tests, documentation, etc.)
- Identifies largest and oldest files
- Finds potentially unreferenced files
- Detects duplicate files using MD5 hashing
- Generates HTML, JSON, and CSV reports
- Analyzes file references between source files

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements-audit.txt
```

## Usage

### Basic Usage

To scan a single directory:

```bash
python project_audit.py path/to/directory
```

To scan multiple directories:

```bash
python project_audit.py path/to/dir1 path/to/dir2
```

### Options

- `-o, --output`: Output directory for reports (default: `reports`)
- `-v, --verbose`: Enable verbose output

Example:

```bash
python project_audit.py . -o my_reports --verbose
```

## Report Files

The tool generates the following report files in the output directory:

- `project_audit_<timestamp>.html`: Interactive HTML report
- `project_audit_<timestamp>.json`: Complete audit data in JSON format
- `file_inventory_<timestamp>.csv`: Detailed file inventory in CSV format

## Report Contents

The HTML report includes:

- Summary statistics
- File type distribution
- File category distribution
- Largest files
- Oldest files
- Potentially unreferenced files
- Duplicate files

## Integration with MCP Servers

The tool can be extended to integrate with MCP (Model Context Protocol) servers for enhanced analysis. To enable MCP integration, set the following environment variables:

```bash
export MCP_SERVER_URL=http://your-mcp-server:port
```

## License

This tool is part of the Resume Velvit Thunder project and is licensed under the project's license.
