# REE AI Platform - Backup Integration Guide

This guide explains how to integrate backup automation into your REE AI Platform deployment.

## Quick Start

### Linux/Mac

```bash
# 1. Run interactive setup
cd scripts
./backup-setup.sh

# 2. Test the backup (dry-run)
./backup.sh --dry-run

# 3. Run actual backup
./backup.sh

# 4. List and restore backups
./restore.sh list
./restore.sh restore latest
```

### Windows

```powershell
# 1. Run interactive setup
cd scripts
.\backup-setup.ps1

# 2. Test the backup (dry-run)
.\backup.ps1 -DryRun

# 3. Run actual backup
.\backup.ps1

# 4. List backups
.\restore.sh list
```

## Setup Steps

### Step 1: Run Configuration Wizard

The setup scripts walk you through configuration:

```bash
# Linux/Mac
./scripts/backup-setup.sh

# Windows
.\scripts\backup-setup.ps1
```

You'll be prompted for:
- PostgreSQL credentials and connection details
- Backup directory location
- Retention policy (days)
- OpenSearch backup preference
- S3 upload credentials (optional)
- Email notification settings (optional)
- Automatic scheduling (optional)

### Step 2: Manual Configuration (Alternative)

If you prefer manual setup:

```bash
# Copy the example configuration
cp scripts/.backup.env.example scripts/.backup.env

# Edit with your values
# Required: POSTGRES_PASSWORD
# Optional: S3, Email, etc.

# Protect sensitive data
chmod 600 scripts/.backup.env
```

### Step 3: Verify Setup

```bash
# Test PostgreSQL connection
psql -h localhost -U ree_ai_user -d ree_ai -c "SELECT version();"

# Test OpenSearch connection
curl -X GET "localhost:9200/"

# Test backup permissions
./scripts/backup.sh --dry-run
```

## Integration Scenarios

### Docker Environment

When running services in Docker:

```bash
# Update .backup.env with container names
POSTGRES_HOST=postgres          # Docker service name
OPENSEARCH_HOST=opensearch       # Docker service name

# Backup from Docker container
docker-compose exec -T postgres pg_dump -U ree_ai_user ree_ai > backup.sql

# Or run backup script from host with correct container names
./scripts/backup.sh
```

### Kubernetes Environment

For Kubernetes deployments:

```bash
# Port-forward PostgreSQL
kubectl port-forward svc/postgres 5432:5432 &

# Port-forward OpenSearch
kubectl port-forward svc/opensearch 9200:9200 &

# Run backup with localhost
export POSTGRES_HOST=localhost
./scripts/backup.sh
```

### Remote Server

For remote PostgreSQL servers:

```bash
# Update .backup.env
POSTGRES_HOST=db.example.com
POSTGRES_PORT=5432

# Ensure network connectivity
ping db.example.com
psql -h db.example.com -U ree_ai_user -d ree_ai -c "SELECT 1;"

# Run backup
./scripts/backup.sh
```

## Scheduling

### Linux/Mac - Cron

```bash
# Edit crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * cd /path/to/ree-ai && \
  POSTGRES_PASSWORD=your_password \
  S3_ENABLED=true \
  S3_BUCKET=backups \
  ./scripts/backup.sh >> ./scripts/backup.log 2>&1

# Multiple times per day (every 6 hours)
0 0,6,12,18 * * * cd /path/to/ree-ai && ./scripts/backup.sh

# View scheduled jobs
crontab -l
```

### Windows - Task Scheduler

The setup script creates a task automatically:

```powershell
# View created task
Get-ScheduledTask -TaskName "REE-AI-Backup-Daily"

# Manually create task
$trigger = New-ScheduledTaskTrigger -Daily -At 02:00
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-NoProfile -File C:\path\to\backup-task.ps1"
Register-ScheduledTask -TaskName "REE-AI-Backup-Daily" `
  -Trigger $trigger -Action $action -RunLevel Highest

# Run task manually
Start-ScheduledTask -TaskName "REE-AI-Backup-Daily"

# View task history
Get-ScheduledTaskInfo -TaskName "REE-AI-Backup-Daily"
```

## S3 Integration

### AWS Setup

1. Create S3 bucket:
```bash
aws s3 mb s3://my-ree-ai-backups --region us-east-1
```

2. Create IAM user with S3 access:
```bash
aws iam create-user --user-name ree-ai-backup
aws iam put-user-policy --user-name ree-ai-backup --policy-name S3Access \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::my-ree-ai-backups",
        "arn:aws:s3:::my-ree-ai-backups/*"
      ]
    }]
  }'
```

3. Create access keys:
```bash
aws iam create-access-key --user-name ree-ai-backup
```

4. Update `.backup.env`:
```
S3_ENABLED=true
S3_BUCKET=my-ree-ai-backups
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=wJalr...
```

### Verify S3 Upload

```bash
# List backups in S3
aws s3 ls s3://my-ree-ai-backups/ree-ai-backups/

# Download backup from S3
aws s3 cp s3://my-ree-ai-backups/ree-ai-backups/backup.tar.gz .

# Calculate S3 storage usage
aws s3 ls s3://my-ree-ai-backups/ --recursive --human-readable --summarize
```

## Email Notifications

### Gmail Setup

```bash
# Create app-specific password
# 1. Enable 2-step verification
# 2. Go to: myaccount.google.com/apppasswords
# 3. Select Mail and Windows Computer
# 4. Copy the generated password

# Update .backup.env
ENABLE_EMAIL=true
EMAIL_RECIPIENT=your-email@company.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use app password, not regular password
```

### Custom SMTP Server

```bash
# Update .backup.env
ENABLE_EMAIL=true
EMAIL_RECIPIENT=ops@example.com
SMTP_SERVER=mail.example.com
SMTP_PORT=587
SMTP_USER=backup@example.com
SMTP_PASSWORD=your_password
```

## Monitoring

### Backup Health Checks

```bash
# Check latest backup status
ls -lh backups/ree-ai-backup_*.tar.gz | tail -5

# Verify backup integrity
./scripts/restore.sh verify ree-ai-backup_20241029_120000

# Check backup log
tail -50 scripts/backup.log

# Monitor backup size
du -sh backups/
du -sh backups/* | sort -h
```

### Log Analysis

```bash
# View all errors
grep ERROR scripts/backup.log

# View recent operations
tail -20 scripts/backup.log

# Count successful backups
grep -c SUCCESS scripts/backup.log

# Find slow backups
grep "Start time\|End time" scripts/backup.log | paste - -
```

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Test connection manually
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB

# Verify credentials
echo $POSTGRES_PASSWORD | psql -h localhost -U ree_ai_user ree_ai

# Check PostgreSQL is running
pg_isready -h localhost -p 5432
```

### Insufficient Disk Space

```bash
# Check disk usage
df -h

# Monitor backup size
du -sh backups/

# Reduce retention
RETENTION_DAYS=7 ./scripts/backup.sh

# Compress backups manually
gzip -9 backups/ree-ai-backup_*.sql 2>/dev/null || true
```

### S3 Upload Failures

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Test bucket access
aws s3 ls s3://my-bucket/

# Check bucket permissions
aws s3api get-bucket-policy --bucket my-bucket

# Check available disk space for upload
df -h
```

### Email Not Sending

```bash
# Test SMTP connection
telnet smtp.gmail.com 587

# Verify email credentials
echo "Test" | mail -s "Test" $EMAIL_RECIPIENT

# Check mail logs
tail -20 /var/log/mail.log  # Linux
Get-WinEvent -LogName Application | Select-Object -Last 10  # Windows
```

## Best Practices

### Security

1. **Protect Configuration File**
   ```bash
   chmod 600 scripts/.backup.env
   ```

2. **Use Strong Passwords**
   - PostgreSQL: Generate 20+ character random password
   - AWS: Use IAM roles instead of long-term keys
   - SMTP: Use app passwords instead of main account password

3. **Restrict Access**
   - Limit backup directory permissions
   - Use VPC endpoints for S3
   - Use private subnets for database access

4. **Encrypt Backups**
   - S3 default encryption enabled
   - Consider additional encryption for sensitive data
   - Use TLS for SMTP communication

### Operations

1. **Regular Testing**
   - Test restore procedure monthly
   - Verify backup integrity weekly
   - Test email notifications after changes

2. **Monitoring**
   - Set up alerts on backup failures
   - Monitor backup size trends
   - Track backup duration

3. **Documentation**
   - Document backup schedule
   - Maintain recovery procedures
   - Track retention policy changes

4. **Retention Policy**
   - Development: 7 days
   - Staging: 14 days
   - Production: 30+ days

## Advanced Configuration

### Multiple Backup Destinations

```bash
# Backup locally
BACKUP_DIR=./backups ./scripts/backup.sh

# Copy to external drive
cp -r ./backups/* /mnt/external-drive/backups/

# Backup also to S3
S3_ENABLED=true S3_BUCKET=my-bucket ./scripts/backup.sh
```

### Incremental Backups

```bash
# PostgreSQL WAL archiving (for point-in-time recovery)
# See PostgreSQL documentation for WAL setup

# Daily full backup + hourly WAL archives
0 2 * * * ./scripts/backup.sh
0 * * * * pg_basebackup -D backups/wal_backups/ -Ft -z
```

### Database Replication

```bash
# For replication setups, back up standby server
POSTGRES_HOST=standby.example.com ./scripts/backup.sh

# Verify replication status
psql -c "SELECT * FROM pg_stat_replication;"
```

## Reference

### File Locations

```
ree-ai/
├── scripts/
│   ├── backup.sh              # Main backup script (Linux/Mac)
│   ├── backup.ps1             # Backup script (Windows)
│   ├── restore.sh             # Restore script
│   ├── backup-setup.sh        # Setup wizard (Linux/Mac)
│   ├── backup-setup.ps1       # Setup wizard (Windows)
│   ├── .backup.env            # Configuration (secret!)
│   ├── .backup.env.example    # Configuration template
│   ├── BACKUP_README.md       # User guide
│   ├── BACKUP_INTEGRATION_GUIDE.md  # This file
│   ├── backup.log             # Backup logs
│   └── restore.log            # Restore logs
└── backups/                   # Backup storage
    └── ree-ai-backup_*.tar.gz # Compressed backups
```

### Common Commands

```bash
# Setup
./scripts/backup-setup.sh                  # Interactive setup

# Backup
./scripts/backup.sh                        # Run backup
./scripts/backup.sh --dry-run             # Preview
S3_ENABLED=true ./scripts/backup.sh       # Backup to S3

# Restore
./scripts/restore.sh list                  # List backups
./scripts/restore.sh restore latest        # Restore latest
./scripts/restore.sh verify <name>         # Verify backup

# Monitoring
tail -f scripts/backup.log                # Watch logs
ls -lh backups/                           # List backups
du -sh backups/                           # Total size
```

## Support Resources

- Main Guide: `BACKUP_README.md`
- PostgreSQL: https://www.postgresql.org/docs/current/backup.html
- OpenSearch: https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/
- AWS S3: https://docs.aws.amazon.com/s3/
- Docker Backups: https://docs.docker.com/storage/volumes/#backup-restore-or-migrate-data-volumes

---

**Last Updated:** October 29, 2024
**Version:** 1.0
