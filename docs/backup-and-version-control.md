# Backup and Version Control Preparation

## 1. Current Repository Status

### Git Status
- **Current Branch**: `main`
- **Uncommitted Changes**:
  - Modified: `README.md`, `api/main.py`, `config_manager.py`
  - Deleted: Several debug and test files in `api/`
  - Untracked: Multiple new files and directories including `docs/`, `scripts/`, and configuration files

### Branch Structure
```
* main
  remotes/origin/HEAD -> origin/main
  remotes/origin/main
```

## 2. Backup Plan

### 2.1 Create Full Backups

#### File System Backup
```powershell
# Create timestamp for backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "C:\Backups\resume-velvit-thunder_$timestamp"

# Create backup directory
New-Item -ItemType Directory -Path $backupDir -Force

# Create zip archive of the entire project (excluding .git, node_modules, __pycache__, etc.)
Compress-Archive -Path ".\*" -DestinationPath "$backupDir\resume-velvit-thunder_$timestamp.zip" -CompressionLevel Optimal
```

#### Database Backup
```powershell
# Backup SQLite database (if using SQLite)
Copy-Item -Path ".\resume_builder.db" -Destination "$backupDir\resume_builder_$timestamp.db"

# For other database systems, use appropriate backup commands
# Example for PostgreSQL:
# pg_dump -U username -d database_name -f "$backupDir\database_backup_$timestamp.sql"
```

#### Git Commit Hash Documentation
```powershell
# Save current commit hashes
git rev-parse HEAD > "$backupDir\git_commit_hashes.txt"
git log -n 5 --oneline >> "$backupDir\git_commit_hashes.txt"
```

### 2.2 Backup Verification

1. **Verify Zip Archive**
   - Check that the zip file exists and has a reasonable size
   - Extract to a temporary location and verify critical files

2. **Verify Database Backup**
   - For SQLite: `sqlite3 backup_file.db "PRAGMA integrity_check;"`
   - For other databases, perform a test restore if possible

## 3. Version Control Preparation

### 3.1 Current Branch Cleanup

1. **Commit Current Changes**
   ```powershell
   # Stage all changes
   git add .
   
   # Create a commit with all current changes
   git commit -m "Pre-migration commit: Save all current work before monorepo migration"
   ```

2. **Create Pre-Migration Branch**
   ```powershell
   # Create and switch to a new branch for the current state
   git checkout -b pre-monorepo-migration-$(Get-Date -Format "yyyyMMdd")
   
   # Push the branch to remote
   git push -u origin HEAD
   ```

3. **Create Pre-Migration Tag**
   ```powershell
   # Create an annotated tag for the pre-migration state
   git tag -a v0.1.0-pre-migration -m "Pre-monorepo migration state"
   
   # Push the tag to remote
   git push origin v0.1.0-pre-migration
   ```

### 3.2 Git History Preservation Strategy

1. **Preserve History in New Structure**
   - Use `git filter-branch` or `git filter-repo` to restructure while preserving history
   - Example:
     ```bash
     # Create a backup of the repository first
     git clone --mirror . ../resume-velvit-thunder-backup.git
     
     # Use git filter-repo to restructure (install with: pip install git-filter-repo)
     git filter-repo --path-rename api/:apps/api/ --path-rename resume-builder-app/:apps/web/
     ```

2. **Documentation of History**
   - Document the original repository structure and important commit hashes
   - Keep a record of any complex history rewriting operations

## 4. Rollback Plan

### 4.1 Rollback Triggers
- Failed migration steps
- Critical bugs discovered post-migration
- Performance degradation
- Data integrity issues

### 4.2 Rollback Steps

1. **Immediate Rollback (First 24 hours)**
   ```powershell
   # Switch back to the pre-migration branch
   git checkout pre-monorepo-migration-$(Get-Date -Format "yyyyMMdd")
   
   # Reset working directory to match the branch
   git reset --hard
   git clean -fd
   ```

2. **Database Rollback**
   ```powershell
   # Restore database from backup
   Stop-Service -Name "YourDatabaseService" -Force
   Copy-Item -Path "C:\Backups\resume-velvit-thunder_<timestamp>\resume_builder_<timestamp>.db" -Destination ".\resume_builder.db" -Force
   Start-Service -Name "YourDatabaseService"
   ```

3. **File System Rollback**
   - Extract the backup zip to a temporary location
   - Replace modified files with versions from backup
   - Restore any deleted files

### 4.3 Rollback Verification

1. **Verify Application Functionality**
   - Run test suite
   - Check critical user flows
   - Verify data integrity

2. **Post-Rollback Steps**
   - Document the rollback in the issue tracker
   - Create a post-mortem analysis
   - Update the migration plan based on lessons learned

## 5. Critical Paths for Quick Rollback

1. **Configuration Files**
   - `config.json`
   - `.env` files
   - Database connection strings

2. **Core Application Code**
   - `api/main.py`
   - `config_manager.py`
   - Frontend entry points

3. **Database**
   - Schema definitions
   - Migration scripts
   - Seed data

## 6. Pre-Migration Checklist

- [ ] All changes committed to version control
- [ ] Full backup completed and verified
- [ ] Pre-migration branch and tag created
- [ ] Team notified of maintenance window
- [ ] Rollback plan documented and tested
- [ ] Critical paths identified and documented

## 7. Post-Migration Verification

- [ ] All services start correctly
- [ ] Test suite passes
- [ ] Critical user flows tested
- [ ] Performance benchmarks within expected ranges
- [ ] Monitoring and logging operational

## 8. Emergency Contacts

- **Primary Contact**: [Name] - [Phone] - [Email]
- **Secondary Contact**: [Name] - [Phone] - [Email]
- **Database Administrator**: [Name] - [Phone] - [Email]
- **Infrastructure Team**: [Contact Information]

## 9. Next Steps

1. Review and approve this backup and rollback plan
2. Schedule a maintenance window for the migration
3. Notify all stakeholders of the planned migration
4. Perform a dry run of the migration and rollback procedures
5. Execute the migration according to the plan
