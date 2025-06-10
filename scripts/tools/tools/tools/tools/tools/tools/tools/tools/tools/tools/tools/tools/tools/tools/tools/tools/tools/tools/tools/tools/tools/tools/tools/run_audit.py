#!/usr/bin/env python3
"""
Run Project Audit for Task #82 - Comprehensive Project Audit and Inventory

This script runs the project audit and generates the required documentation
for Task #82, including the inventory spreadsheet and file status report.
"""

import os
import sys
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import the project auditor
from scripts.project_audit import ProjectAuditor

def generate_inventory_spreadsheet(audit_data: Dict[str, Any], output_dir: Path) -> Path:
    """Generate an inventory spreadsheet from the audit data."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"project_inventory_{timestamp}.xlsx"
    
    try:
        import pandas as pd
        
        # Prepare data for the spreadsheet
        files_data = []
        for file_info in audit_data['files']:
            files_data.append({
                'Path': file_info['path'],
                'Name': file_info['name'],
                'Extension': file_info['extension'],
                'Type': file_info['file_type'],
                'Category': file_info['category'],
                'Size (MB)': round(file_info['size_bytes'] / (1024 * 1024), 4),
                'Last Modified': datetime.fromtimestamp(file_info['last_modified']).strftime('%Y-%m-%d %H:%M:%S'),
                'References': ', '.join(file_info['references']),
                'Referenced By': ', '.join(file_info['referenced_by']),
                'MD5 Hash': file_info['md5_hash']
            })
        
        # Create a DataFrame and save to Excel
        df = pd.DataFrame(files_data)
        
        # Create a Pandas Excel writer using XlsxWriter as the engine
        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
        
        # Convert the dataframe to an XlsxWriter Excel object
        df.to_excel(writer, sheet_name='File Inventory', index=False)
        
        # Get the xlsxwriter workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['File Inventory']
        
        # Add some formats
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # Format the header row
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Set column widths
        worksheet.set_column('A:A', 50)  # Path
        worksheet.set_column('B:B', 25)  # Name
        worksheet.set_column('C:C', 10)  # Extension
        worksheet.set_column('D:D', 15)  # Type
        worksheet.set_column('E:E', 15)  # Category
        worksheet.set_column('F:F', 10)  # Size (MB)
        worksheet.set_column('G:G', 20)  # Last Modified
        worksheet.set_column('H:H', 30)  # References
        worksheet.set_column('I:I', 30)  # Referenced By
        worksheet.set_column('J:J', 35)  # MD5 Hash
        
        # Add summary sheet
        summary_data = []
        
        # File types summary
        summary_data.append(['FILE TYPES', ''])
        for file_type, count in audit_data['summary']['by_type'].items():
            summary_data.append([file_type or 'Unknown', count])
        
        # Categories summary
        summary_data.append(['', ''])
        summary_data.append(['CATEGORIES', ''])
        for category, count in audit_data['summary']['by_category'].items():
            summary_data.append([category, count])
        
        # Create summary sheet
        summary_df = pd.DataFrame(summary_data[2:], columns=summary_data[1])
        summary_df.to_excel(writer, sheet_name='Summary', index=False, header=False)
        
        # Format summary sheet
        summary_worksheet = writer.sheets['Summary']
        summary_worksheet.set_column('A:A', 30)
        summary_worksheet.set_column('B:B', 15)
        
        # Add headers
        summary_worksheet.write(0, 0, 'FILE TYPES', header_format)
        summary_worksheet.write(len(audit_data['summary']['by_type']) + 2, 0, 'CATEGORIES', header_format)
        
        # Close the Pandas Excel writer and output the Excel file
        writer.close()
        
        print(f"Inventory spreadsheet generated: {output_file}")
        return output_file
        
    except ImportError:
        print("Warning: pandas or xlsxwriter not installed. Falling back to CSV format.")
        return generate_inventory_csv(audit_data, output_dir)

def generate_inventory_csv(audit_data: Dict[str, Any], output_dir: Path) -> Path:
    """Generate a CSV inventory file (fallback if Excel is not available)."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"project_inventory_{timestamp}.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'path', 'name', 'extension', 'file_type', 'category',
            'size_mb', 'last_modified', 'references', 'referenced_by', 'md5_hash'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for file_info in audit_data['files']:
            row = file_info.copy()
            # Convert size to MB
            row['size_mb'] = round(row['size_bytes'] / (1024 * 1024), 4)
            # Format last modified date
            row['last_modified'] = datetime.fromtimestamp(row['last_modified']).strftime('%Y-%m-%d %H:%M:%S')
            # Convert lists to strings
            row['references'] = ', '.join(row['references'])
            row['referenced_by'] = ', '.join(row['referenced_by'])
            # Remove unused fields
            row.pop('size_bytes', None)
            writer.writerow(row)
    
    print(f"CSV inventory generated: {output_file}")
    return output_file

def generate_file_status_report(audit_data: Dict[str, Any], output_dir: Path) -> Path:
    """Generate a file status report with analysis of file status."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"file_status_report_{timestamp}.md"
    
    # Categorize files
    active_files = []
    potentially_outdated = []
    
    # Get current time for age calculation
    current_time = datetime.now().timestamp()
    SIX_MONTHS_AGO = current_time - (180 * 24 * 60 * 60)  # 6 months in seconds
    
    for file_info in audit_data['files']:
        # Active files: modified recently or referenced by other files
        if (file_info['last_modified'] > SIX_MONTHS_AGO or 
            file_info['referenced_by'] or 
            file_info['category'] in ['source', 'test']):
            active_files.append(file_info)
        else:
            potentially_outdated.append(file_info)
    
    # Generate markdown report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# File Status Report\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Summary
        f.write("## Summary\n\n")
        f.write(f"- **Total files scanned:** {len(audit_data['files'])}\n")
        f.write(f"- **Active files:** {len(active_files)} (recently modified or referenced)\n")
        f.write(f"- **Potentially outdated files:** {len(potentially_outdated)}\n")
        f.write(f"- **Duplicate files found:** {len(audit_data['summary']['duplicate_files'])}\n\n")
        
        # Active files
        f.write("## Active Files\n\n")
        f.write("These files have been recently modified or are referenced by other files.\n\n")
        f.write("| Path | Type | Category | Last Modified | References |\n")
        f.write("|------|------|----------|---------------|------------|\n")
        
        for file in sorted(active_files, key=lambda x: x['last_modified'], reverse=True)[:50]:  # Show top 50
            last_modified = datetime.fromtimestamp(file['last_modified']).strftime('%Y-%m-%d')
            f.write(f"| {file['path']} | {file['file_type']} | {file['category']} | {last_modified} | {len(file['referenced_by'])} |\n")
        
        if len(active_files) > 50:
            f.write(f"\n*... and {len(active_files) - 50} more active files ...*\n")
        
        # Potentially outdated files
        f.write("\n## Potentially Outdated Files\n\n")
        f.write("These files haven't been modified in the last 6 months and aren't referenced by other files.\n\n")
        f.write("| Path | Type | Category | Last Modified |\n")
        f.write("|------|------|----------|---------------|\n")
        
        for file in sorted(potentially_outdated, key=lambda x: x['last_modified'])[:50]:  # Show oldest 50
            last_modified = datetime.fromtimestamp(file['last_modified']).strftime('%Y-%m-%d')
            f.write(f"| {file['path']} | {file['file_type']} | {file['category']} | {last_modified} |\n")
        
        if len(potentially_outdated) > 50:
            f.write(f"\n*... and {len(potentially_outdated) - 50} more potentially outdated files ...*\n")
        
        # Duplicate files
        if audit_data['summary']['duplicate_files']:
            f.write("\n## Duplicate Files\n\n")
            f.write("The following files have identical content (based on MD5 hash):\n\n")
            
            for dup in audit_data['summary']['duplicate_files']:
                f.write(f"### Hash: {dup['hash'][:8]}...\n")
                for file_path in dup['files']:
                    f.write(f"- `{file_path}`\n")
                f.write("\n")
    
    print(f"File status report generated: {output_file}")
    return output_file

def main():
    """Main function to run the project audit and generate reports."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Project Audit for Task #82')
    parser.add_argument('directories', nargs='+', help='Directories to audit')
    parser.add_argument('--output', '-o', default='audit_reports', 
                        help='Output directory for reports (default: audit_reports)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run the audit
    print("Starting project audit...")
    auditor = ProjectAuditor(args.directories)
    
    # Scan directories
    for directory in args.directories:
        auditor.scan_directory(Path(directory).resolve())
    
    # Analyze references
    auditor.analyze_references()
    
    # Generate report data
    report = auditor.generate_report(str(output_dir))
    
    # Generate additional reports
    print("\nGenerating additional reports...")
    try:
        inventory_file = generate_inventory_spreadsheet(report, output_dir)
    except Exception as e:
        print(f"Error generating inventory spreadsheet: {e}")
        inventory_file = generate_inventory_csv(report, output_dir)
    
    status_report_file = generate_file_status_report(report, output_dir)
    
    print("\n=== Audit Complete ===")
    print(f"Reports generated in: {output_dir.absolute()}")
    print(f"- Project inventory: {inventory_file.name}")
    print(f"- File status report: {status_report_file.name}")
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Total files scanned: {len(report['files'])}")
    print(f"File types: {len(report['summary']['by_type'])}")
    print(f"Categories: {len(report['summary']['by_category'])}")
    print(f"Duplicate files found: {len(report['summary']['duplicate_files'])}")

if __name__ == '__main__':
    main()
