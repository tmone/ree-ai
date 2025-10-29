# REE AI Platform - Backup Automation Suite

## Welcome to Backup Automation

This directory contains a complete backup and restore automation solution for the REE AI Platform. Whether you're using Linux, Mac, or Windows, this suite provides all the tools needed to protect your data.

## Start Here

### Choosing Your Path

**First time setting up?**
1. Read: [Quick Start Guide](#quick-start) below
2. Run: `./backup-setup.sh` (Linux/Mac) or `.\backup-setup.ps1` (Windows)
3. Review: [BACKUP_README.md](BACKUP_README.md)

**Already familiar with backup/restore?**
1. Copy: `.backup.env.example` to `.backup.env`
2. Edit: `.backup.env` with your configuration
3. Run: `./backup.sh` or `.\backup.ps1`

**Need help with specific environment?**
1. Read: [BACKUP_INTEGRATION_GUIDE.md](BACKUP_INTEGRATION_GUIDE.md)
2. Follow: Environment-specific setup instructions

## Quick Start

### Linux & Mac Users

```bash
# Step 1: Interactive setup (recommended)
./backup-setup.sh

# Step 2: Test backup (preview only, no changes)
./backup.sh --dry-run

# Step 3: Run your first backup
./backup.sh

# Step 4: List and verify backups
./restore.sh list
./restore.sh verify ree-ai-backup_YYYYMMDD_HHMMSS

# Step 5: Schedule automatic backups
# The setup script offers this, or manually add to crontab:
# 0 2 * * * cd /path/to/ree-ai && ./scripts/backup.sh >> ./scripts/backup.log 2>&1
```

### Windows Users

```powershell
# Step 1: Check execution policy
Get-ExecutionPolicy

# If Restricted, run in admin terminal:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Step 2: Interactive setup (recommended)
.\backup-setup.ps1

# Step 3: Test backup (preview only, no changes)
.\backup.ps1 -DryRun

# Step 4: Run your first backup
.\backup.ps1

# Step 5: Schedule automatic backups
# The setup script creates a Windows Task Scheduler job for you
```

## File Guide

### Backup Scripts

| File | Purpose | Platform |
|------|---------|----------|
| `backup.sh` | Main backup script | Linux/Mac |
| `backup.ps1` | Main backup script | Windows |
| `restore.sh` | Restore from backups | Linux/Mac |

### Setup Wizards

| File | Purpose | Platform |
|------|---------|----------|
| `backup-setup.sh` | Interactive setup | Linux/Mac |
| `backup-setup.ps1` | Interactive setup | Windows |

### Configuration

| File | Purpose |
|------|---------|
| `.backup.env.example` | Configuration template (copy to `.backup.env` and customize) |
| `.backup.env` | Your actual configuration (created after setup) |

### Documentation

| File | Read This For |
|------|---------------|
| `README_BACKUP_AUTOMATION.md` | This file - overview and navigation |
| `BACKUP_README.md` | Complete user guide, configuration reference, examples |
| `BACKUP_INTEGRATION_GUIDE.md` | Docker, Kubernetes, remote server, S3, email setup |
| `BACKUP_FILES_SUMMARY.txt` | Quick reference, features, maintenance schedule |

## What Gets Backed Up

- **PostgreSQL Database**: Complete database dump with schema and data
- **OpenSearch**: Cluster state and index metadata (optional)
- **Configuration Files**: .env, docker-compose.yml, Makefile, and custom files
- **Compression**: Automatic tar.gz compression with timestamps

## Storage Options

- **Local Storage** (default): `backups/` directory
- **Amazon S3** (optional): Automatic upload with configurable prefix
- **Automatic Cleanup**: Old backups deleted based on retention (default: 30 days)

## Key Features

| Feature | Benefit |
|---------|---------|
| Automated Backup | Run on schedule (daily, hourly, etc.) |
| Dry-Run Mode | Test without making changes |
| Email Alerts | Get notified of backup failures |
| S3 Integration | Off-site backup with automatic upload |
| Restore Testing | Verify backups before disaster strikes |
| Comprehensive Logging | Track what happened and when |
| Configuration Validation | Catch issues before backup runs |
| Error Handling | Graceful failure with detailed messages |

## Configuration Basics

### Minimal Setup (Just Database)

```bash
# Set password and run
export POSTGRES_PASSWORD="your_password"
./backup.sh
```

### Standard Setup (With File)

```bash
# Copy and edit template
cp .backup.env.example .backup.env
nano .backup.env

# Protect sensitive file
chmod 600 .backup.env

# Run backup
./backup.sh
```

### Full Setup (With All Features)

Run the interactive setup wizard:

```bash
./backup-setup.sh  # Linux/Mac
.\backup-setup.ps1 # Windows
```

The wizard will ask about:
- PostgreSQL connection details
- Backup location and retention
- OpenSearch backup (yes/no)
- S3 upload (with credentials)
- Email notifications (with SMTP details)
- Automatic scheduling (cron/Task Scheduler)

## Common Commands

```bash
# Backup Operations
./backup.sh                      # Run backup now
./backup.sh --dry-run            # Preview without backup
DRY_RUN=true ./backup.sh         # Alternative dry-run syntax
S3_ENABLED=true ./backup.sh      # Force S3 upload
RETENTION_DAYS=7 ./backup.sh     # Use 7-day retention

# Restore Operations
./restore.sh list                          # Show available backups
./restore.sh verify backup_name            # Check backup integrity
./restore.sh restore backup_name           # Restore specific backup
./restore.sh restore latest                # Restore latest backup
DRY_RUN=true ./restore.sh restore latest   # Preview restore

# Configuration
cp .backup.env.example .backup.env  # Create config file
chmod 600 .backup.env               # Protect sensitive file
nano .backup.env                    # Edit configuration
./backup-setup.sh                   # Interactive setup
```

## Scheduling Backups

### Linux/Mac (Cron)

```bash
# Edit crontab
crontab -e

# Examples:
# Daily at 2 AM
0 2 * * * cd /path/to/ree-ai && ./scripts/backup.sh >> ./scripts/backup.log 2>&1

# Every 6 hours
0 0,6,12,18 * * * cd /path/to/ree-ai && ./scripts/backup.sh >> ./scripts/backup.log 2>&1

# Every day at 2 AM with S3 upload
0 2 * * * cd /path/to/ree-ai && S3_ENABLED=true ./scripts/backup.sh >> ./scripts/backup.log 2>&1
```

### Windows (Task Scheduler)

The setup script (`backup-setup.ps1`) creates this automatically.

To manually create:
```powershell
$trigger = New-ScheduledTaskTrigger -Daily -At 02:00
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-NoProfile -File C:\path\to\backup-task.ps1"
Register-ScheduledTask -TaskName "REE-AI-Backup" `
  -Trigger $trigger -Action $action -RunLevel Highest
```

## Monitoring Backups

```bash
# Check latest backup
ls -lh backups/ | tail -5

# Monitor backup size
du -sh backups/

# View backup log
tail -f ./backup.log

# Verify backup integrity
./restore.sh verify ree-ai-backup_TIMESTAMP

# Count successful backups
grep SUCCESS ./backup.log | wc -l
```

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Test connection
psql -h localhost -U ree_ai_user -d ree_ai -c "SELECT version();"

# If fails, check:
# 1. POSTGRES_PASSWORD environment variable
# 2. POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER
# 3. PostgreSQL service is running: systemctl status postgresql
```

### S3 Upload Fails

```bash
# Verify credentials
aws sts get-caller-identity
aws s3 ls s3://my-bucket/

# Check permissions
aws s3api get-bucket-acl --bucket my-bucket
```

### Email Not Sending

```bash
# Test SMTP connection
telnet smtp.gmail.com 587

# For Gmail, use app password not regular password
# For other SMTP, verify SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
```

### Insufficient Disk Space

```bash
# Check available space
df -h

# Check backup size
du -sh backups/

# Reduce retention
RETENTION_DAYS=7 ./backup.sh

# Or manually delete old backups
rm backups/ree-ai-backup_old_timestamp.tar.gz
```

## Documentation Map

```
Backup Automation Suite
├── Scripts/
│   ├── backup.sh              [Production backup - Linux/Mac]
│   ├── backup.ps1             [Production backup - Windows]
│   ├── restore.sh             [Restore from backups - Linux/Mac]
│   ├── backup-setup.sh        [Setup wizard - Linux/Mac]
│   └── backup-setup.ps1       [Setup wizard - Windows]
│
├── Configuration/
│   ├── .backup.env.example    [Configuration template]
│   └── .backup.env            [Your actual config - keep secret!]
│
├── Documentation/
│   ├── README_BACKUP_AUTOMATION.md     [This file]
│   ├── BACKUP_README.md                [Complete guide & reference]
│   ├── BACKUP_INTEGRATION_GUIDE.md     [Environment-specific setup]
│   └── BACKUP_FILES_SUMMARY.txt        [Quick reference]
│
└── Backups/
    └── backups/               [Local backup storage]
        └── ree-ai-backup_*.tar.gz
```

## Security Best Practices

1. **Protect Configuration**
   ```bash
   chmod 600 .backup.env
   # Never commit to git
   echo ".backup.env" >> ../.gitignore
   ```

2. **Use Strong Passwords**
   - PostgreSQL: 20+ random characters
   - AWS: Use IAM roles, not long-term keys
   - SMTP: Use app passwords, not main account

3. **Secure Storage**
   - Keep backups on secure storage
   - Use S3 with encryption
   - Test restore procedures
   - Monitor access logs

4. **Monitor Backups**
   - Enable email notifications
   - Review logs weekly
   - Test restore monthly
   - Verify S3 uploads

## Getting Help

1. **Check the logs** (most common issues are documented there):
   ```bash
   tail -100 backup.log
   grep ERROR backup.log
   ```

2. **Read the appropriate guide**:
   - General use: [BACKUP_README.md](BACKUP_README.md)
   - Specific environment: [BACKUP_INTEGRATION_GUIDE.md](BACKUP_INTEGRATION_GUIDE.md)
   - Quick reference: [BACKUP_FILES_SUMMARY.txt](BACKUP_FILES_SUMMARY.txt)

3. **Test connectivity** to each service:
   ```bash
   psql -h localhost -U ree_ai_user -d ree_ai
   curl http://localhost:9200/
   aws s3 ls s3://my-bucket/
   ```

4. **Run dry-run mode** to preview:
   ```bash
   ./backup.sh --dry-run
   ./restore.sh verify backup_name
   ```

## Common Configurations

### Development Environment (Daily Backups)

```bash
# .backup.env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
BACKUP_DIR=./backups
RETENTION_DAYS=7
OPENSEARCH_ENABLED=false
S3_ENABLED=false
```

### Staging Environment (With S3)

```bash
# .backup.env
POSTGRES_HOST=postgres  # Docker container name
S3_ENABLED=true
S3_BUCKET=staging-backups
RETENTION_DAYS=14
ENABLE_EMAIL=true
```

### Production Environment (Full Setup)

```bash
# .backup.env
POSTGRES_HOST=prod-db.example.com
S3_ENABLED=true
S3_BUCKET=prod-backups-critical
RETENTION_DAYS=30
ENABLE_EMAIL=true
OPENSEARCH_ENABLED=true
```

## Performance Expectations

| Database Size | Backup Time | Compressed Size |
|---------------|-------------|-----------------|
| < 1 GB | 1-5 min | 100-300 MB |
| 1-10 GB | 5-30 min | 100MB-3GB |
| > 10 GB | 30+ min | 3GB+ |

## Version Information

- **Version**: 1.0
- **Created**: October 29, 2024
- **Status**: Production Ready
- **Platform Support**: Linux, Mac, Windows
- **Database**: PostgreSQL 15+
- **Search Engine**: OpenSearch 2.x

## What's Next?

1. **Immediate** (Today):
   - Run `backup-setup.sh` (or `backup-setup.ps1` on Windows)
   - Test with `./backup.sh --dry-run`
   - Run first backup: `./backup.sh`

2. **Short Term** (This Week):
   - Verify backups: `./restore.sh list`
   - Test restore: `./restore.sh restore latest`
   - Review logs

3. **Medium Term** (This Month):
   - Setup scheduling (cron/Task Scheduler)
   - Configure S3 if desired
   - Enable email notifications
   - Document your backup strategy

4. **Long Term** (Ongoing):
   - Monitor backups weekly
   - Test restore monthly
   - Review logs and performance
   - Update credentials annually

## Support Resources

- **Official Guides**: [BACKUP_README.md](BACKUP_README.md)
- **Integration Help**: [BACKUP_INTEGRATION_GUIDE.md](BACKUP_INTEGRATION_GUIDE.md)
- **Quick Reference**: [BACKUP_FILES_SUMMARY.txt](BACKUP_FILES_SUMMARY.txt)
- **PostgreSQL Docs**: https://www.postgresql.org/docs/current/backup.html
- **AWS S3**: https://docs.aws.amazon.com/s3/

---

**Ready to begin?** Start with `./backup-setup.sh` or `.\backup-setup.ps1` depending on your platform.

For detailed information, see [BACKUP_README.md](BACKUP_README.md).
