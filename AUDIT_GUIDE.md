# Project Audit Guide

This guide explains how to use the project audit tools to analyze the codebase and generate reports.

## Overview

The project includes a comprehensive audit system that can:

1. Scan the entire codebase and generate an inventory of all files
2. Analyze file relationships and dependencies
3. Identify duplicate files using content hashing
4. Generate detailed reports in multiple formats (HTML, JSON, CSV, Excel)
5. Integrate with MCP servers for enhanced analysis

## Quick Start

### Prerequisites

- Python 3.8+
- Required Python packages (install with `pip install -r scripts/requirements-audit.txt`)

### Running a Basic Audit

To run a basic audit of the project:

```bash
# Navigate to the project root
cd /path/to/resume-velvit-thunder

# Run the audit script
python scripts/run_audit.py .
```

This will generate reports in the `audit_reports` directory by default.

## Audit Reports

The audit generates several types of reports:

1. **HTML Report** - Interactive web-based report with visualizations
2. **Excel Spreadsheet** - Detailed file inventory with multiple sheets
3. **CSV File** - Raw data for further analysis
4. **Status Report** - Markdown file with analysis of file status

## Advanced Usage

### Specifying Multiple Directories

You can audit multiple directories by specifying them as arguments:

```bash
python scripts/run_audit.py frontend/ backend/ shared/
```

### Custom Output Directory

Use the `-o` or `--output` flag to specify a custom output directory:

```bash
python scripts/run_audit.py . -o my_audit_reports
```

### Verbose Output

Add the `-v` or `--verbose` flag for more detailed output:

```bash
python scripts/run_audit.py . -v
```

## MCP Server Integration

The audit tool can integrate with MCP (Model Context Protocol) servers for enhanced analysis:

1. **Code Quality Analysis** - Get detailed code quality metrics
2. **Duplicate Detection** - Advanced duplicate file detection
3. **Dependency Analysis** - Analyze project dependencies

### Configuring MCP Servers

1. Copy the example config file:
   ```bash
   cp scripts/mcp-config.example.json mcp-config.json
   ```

2. Edit `mcp-config.json` to add your MCP server details

3. Run the audit with MCP integration:
   ```bash
   python scripts/run_audit.py . --mcp-config mcp-config.json
   ```

### Environment Variables

You can also configure MCP servers using environment variables:

```bash
# Enable MCP integration
export MCP_ENABLED=true

# MCP server configuration
export MCP_SERVERS=code_analyzer,duplicate_finder
export MCP_SERVER_CODE_ANALYZER_URL=http://localhost:8000/api/analyze
export MCP_SERVER_CODE_ANALYZER_API_KEY=your-api-key
```

## Automated Auditing

You can integrate the audit into your CI/CD pipeline. Example GitHub Actions workflow:

```yaml
name: Project Audit

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  audit:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r scripts/requirements-audit.txt
    
    - name: Run audit
      run: python scripts/run_audit.py . -o audit-reports
    
    - name: Upload reports
      uses: actions/upload-artifact@v2
      with:
        name: audit-reports
        path: audit-reports/
```

## Interpreting Results

### File Categories

Files are categorized as:

- **Source**: Application source code
- **Test**: Test files and test data
- **Documentation**: Project documentation
- **Configuration**: Configuration files
- **Build Artifact**: Generated build files
- **Other**: Files that don't match other categories

### Status Indicators

- **Active**: Recently modified or referenced by other files
- **Potentially Outdated**: Not modified in the last 6 months and not referenced
- **Duplicate**: Files with identical content (based on MD5 hash)

## Maintenance

### Updating the Audit Tool

To update the audit tool:

1. Pull the latest changes from the repository
2. Update the requirements if needed:
   ```bash
   pip install -r scripts/requirements-audit.txt --upgrade
   ```

### Adding Custom Analyzers

You can extend the audit tool by adding custom analyzers in the `scripts/analyzers` directory. Each analyzer should implement a standard interface.

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   - Ensure all required packages are installed
   - Run `pip install -r scripts/requirements-audit.txt`

2. **Permission Errors**
   - Make sure the script has read access to all files being audited
   - Run with appropriate permissions if needed

3. **MCP Server Connection Issues**
   - Verify the MCP server is running and accessible
   - Check the server URL and API key in the configuration

### Getting Help

For issues with the audit tool, please open an issue in the project repository with:

1. The command you ran
2. The complete error message
3. Your environment details (OS, Python version, etc.)
