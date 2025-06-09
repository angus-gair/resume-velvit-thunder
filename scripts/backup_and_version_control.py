#!/usr/bin/env python3
"""
Backup and Version Control Preparation Script

This script handles creating comprehensive backups and preparing version control
for the project migration. It integrates with MCP servers for enhanced functionality.

Features:
- Create full backups of the project
- Generate database dumps (if applicable)
- Document git repository state
- Create pre-migration tags/branches
- Generate rollback documentation
"""

import os
import sys
import json
import shutil
import logging
import zipfile
import datetime
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backup_script.log')
    ]
)
logger = logging.getLogger(__name__)

class BackupManager:
    """Manages backup and version control operations."""
    
    def __init__(self, config_path: str = None):
        """Initialize the backup manager with optional configuration."""
        self.project_root = Path(__file__).parent.parent
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.project_root / 'backups' / f'pre_migration_{self.timestamp}'
        self.mcp_servers = {}
        
        # Load configuration if provided
        self.config = {}
        if config_path and Path(config_path).exists():
            self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> None:
        """Load configuration from file."""
        try:
            with open(config_path, 'r') as f:
                if config_path.endswith(('.yaml', '.yml')):
                    import yaml
                    self.config = yaml.safe_load(f) or {}
                else:
                    self.config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    def _run_command(self, command: List[str], cwd: Optional[Path] = None) -> Tuple[bool, str]:
        """Run a shell command and return success status and output."""
        if cwd is None:
            cwd = self.project_root
            
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                check=True,
                capture_output=True,
                text=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {' '.join(command)}")
            logger.error(f"Error: {e.stderr}")
            return False, e.stderr
    
    def _ensure_backup_dir(self) -> bool:
        """Ensure backup directory exists."""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create backup directory: {e}")
            return False
    
    def backup_files(self) -> bool:
        """Create a backup of important files and directories."""
        if not self._ensure_backup_dir():
            return False
        
        backup_success = True
        backup_items = [
            'config',
            'scripts',
            'data',
            'templates',
            'tests',
            'requirements.txt',
            'README.md',
            'mcp-config.json',
            'config.json'
        ]
        
        # Create zip archive of the project
        zip_path = self.backup_dir / f'project_backup_{self.timestamp}.zip'
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for item in backup_items:
                    path = self.project_root / item
                    if not path.exists():
                        logger.warning(f"Skipping non-existent path: {path}")
                        continue
                        
                    if path.is_file():
                        zipf.write(path, arcname=path.relative_to(self.project_root))
                    else:
                        for root, _, files in os.walk(path):
                            for file in files:
                                file_path = Path(root) / file
                                try:
                                    zipf.write(
                                        file_path, 
                                        arcname=file_path.relative_to(self.project_root)
                                    )
                                except Exception as e:
                                    logger.error(f"Failed to add {file_path} to backup: {e}")
                                    backup_success = False
            
            logger.info(f"Created project backup: {zip_path}")
            return backup_success
            
        except Exception as e:
            logger.error(f"Failed to create zip backup: {e}")
            return False
    
    def backup_database(self) -> bool:
        """Create a database backup if applicable."""
        # This is a placeholder - implement database-specific backup logic
        logger.info("Skipping database backup (no database configured)")
        return True
    
    def document_git_state(self) -> bool:
        """Document the current git repository state."""
        if not (self.project_root / '.git').exists():
            logger.warning("Not a git repository, skipping git state documentation")
            return False
        
        try:
            git_info = {}
            
            # Get current branch
            success, output = self._run_command(['git', 'branch', '--show-current'])
            if success:
                git_info['current_branch'] = output.strip()
            
            # Get commit hash
            success, output = self._run_command(['git', 'rev-parse', 'HEAD'])
            if success:
                git_info['commit_hash'] = output.strip()
            
            # Get git status
            success, output = self._run_command(['git', 'status', '--porcelain'])
            if success:
                git_info['uncommitted_changes'] = bool(output.strip())
            
            # Save git info to file
            git_info_path = self.backup_dir / 'git_state.json'
            with open(git_info_path, 'w') as f:
                json.dump(git_info, f, indent=2)
            
            logger.info(f"Documented git state to {git_info_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to document git state: {e}")
            return False
    
    def create_pre_migration_tag(self) -> bool:
        """Create a pre-migration tag in git."""
        if not (self.project_root / '.git').exists():
            logger.warning("Not a git repository, skipping tag creation")
            return False
        
        tag_name = f"pre-migration-{self.timestamp}"
        success, _ = self._run_command(['git', 'tag', '-a', tag_name, '-m', f'Pre-migration backup {self.timestamp}'])
        
        if success:
            logger.info(f"Created pre-migration tag: {tag_name}")
            return True
        else:
            logger.error("Failed to create pre-migration tag")
            return False
    
    def generate_rollback_docs(self) -> bool:
        """Generate rollback documentation."""
        try:
            rollback_path = self.backup_dir / 'ROLLBACK.md'
            with open(rollback_path, 'w') as f:
                f.write(f"# Rollback Procedure\n\n")
                f.write(f"## Backup Information\n")
                f.write(f"- Backup created: {datetime.datetime.now().isoformat()}\n")
                f.write(f"- Backup location: {self.backup_dir.absolute()}\n\n")
                
                f.write("## Rollback Steps\n")
                f.write("1. Stop any running services\n")
                f.write("2. Restore from backup:\n")
                f.write(f"   ```bash\n   unzip {self.backup_dir.name}/project_backup_*.zip -d /path/to/restore\n   ```\n\n")
                f.write("3. If needed, restore the database from the backup\n")
                f.write("4. Verify the restored application\n")
                f.write("5. Restart services\n")
            
            logger.info(f"Generated rollback documentation: {rollback_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate rollback documentation: {e}")
            return False
    
    def run_backup(self) -> bool:
        """Run the complete backup and version control preparation process."""
        logger.info("Starting backup and version control preparation")
        
        if not self._ensure_backup_dir():
            return False
        
        steps = [
            ("Backing up project files", self.backup_files),
            ("Backing up database", self.backup_database),
            ("Documenting git state", self.document_git_state),
            ("Creating pre-migration tag", self.create_pre_migration_tag),
            ("Generating rollback documentation", self.generate_rollback_docs)
        ]
        
        success = True
        for step_name, step_func in steps:
            logger.info(step_name)
            if not step_func():
                logger.warning(f"Step failed: {step_name}")
                success = False
        
        if success:
            logger.info("Backup and version control preparation completed successfully")
        else:
            logger.warning("Backup and version control preparation completed with warnings")
        
        return success

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup and version control preparation')
    parser.add_argument('--config', '-c', help='Path to configuration file')
    parser.add_argument('--output', '-o', help='Output directory for backups')
    
    args = parser.parse_args()
    
    backup_mgr = BackupManager(args.config)
    if args.output:
        backup_mgr.backup_dir = Path(args.output)
    
    if not backup_mgr.run_backup():
        logger.error("Backup and version control preparation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
