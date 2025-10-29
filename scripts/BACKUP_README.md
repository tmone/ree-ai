# REE AI Platform - Backup and Restore Guide

This directory contains automated backup and restore scripts for the REE AI Platform.

## Overview

The backup suite provides:

- **Automated PostgreSQL database backups**
- **OpenSearch indices backup** (optional)
- **Configuration files backup**
- **Automatic compression and timestamping**
- **S3 or local storage upload** (optional)
- **Automatic cleanup of old backups** (30-day retention by default)
- **Email notifications** on failure
- **Restore functionality** with integrity verification
- **Dry-run mode** for testing

## Files

- `backup.sh` - Linux/Mac backup script
- `backup.ps1` - Windows PowerShell backup script
- `restore.sh` - Restore script (Linux/Mac)
- `.backup.env.example` - Configuration template
- `BACKUP_README.md` - This file

## Quick Start

### 1. Setup Configuration

```bash
# Copy the example configuration
cp scripts/.backup.env.example scripts/.backup.env

# Edit with your actual values
nano scripts/.backup.env
```

**Required settings:**
```
POSTGRES_PASSWORD=your_password
```

### 2. Run Backup (Linux/Mac)

```bash
# Standard backup
./scripts/backup.sh

# Dry-run (preview without backup)
./scripts/backup.sh --dry-run

# With specific configuration
export POSTGRES_PASSWORD=your_password
./scripts/backup.sh
```

### 3. Run Backup (Windows)

```powershell
# Set execution policy if needed
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Standard backup
.\scripts\backup.ps1

# Dry-run
.\scripts\backup.ps1 -DryRun

# With environment variables
$env:POSTGRES_PASSWORD = "your_password"
.\scripts\backup.ps1
```

### 4. Restore from Backup

```bash
# List available backups
./scripts/restore.sh list

# Restore from specific backup
./scripts/restore.sh restore ree-ai-backup_20241029_120000

# Restore latest backup (dry-run)
DRY_RUN=true ./scripts/restore.sh restore latest

# Verify backup integrity
./scripts/restore.sh verify ree-ai-backup_20241029_120000
```

## Configuration

### Environment Variables

#### Required
| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_PASSWORD` | PostgreSQL password | **REQUIRED** |

#### PostgreSQL
| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_HOST` | PostgreSQL host | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_DB` | Database name | `ree_ai` |
| `POSTGRES_USER` | PostgreSQL user | `ree_ai_user` |

#### OpenSearch (Optional)
| Variable | Description | Default |
|----------|-------------|---------|
| `OPENSEARCH_ENABLED` | Enable OpenSearch backup | `true` |
| `OPENSEARCH_HOST` | OpenSearch host | `localhost` |
| `OPENSEARCH_PORT` | OpenSearch port | `9200` |

#### S3 Upload (Optional)
| Variable | Description | Default |
|----------|-------------|---------|
| `S3_ENABLED` | Enable S3 upload | `false` |
| `S3_BUCKET` | S3 bucket name | (required if enabled) |
| `S3_REGION` | AWS region | `us-east-1` |
| `S3_PREFIX` | S3 path prefix | `ree-ai-backups` |
| `AWS_ACCESS_KEY_ID` | AWS access key | (required if S3 enabled) |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | (required if S3 enabled) |

#### Email Notifications (Optional)
| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_EMAIL` | Enable email notifications | `false` |
| `EMAIL_RECIPIENT` | Email recipient | (required if enabled) |
| `SMTP_SERVER` | SMTP server | (required if enabled) |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | SMTP username | (optional) |
| `SMTP_PASSWORD` | SMTP password | (optional) |

#### Other Options
| Variable | Description | Default |
|----------|-------------|---------|
| `BACKUP_DIR` | Backup directory | `./backups` |
| `RETENTION_DAYS` | Days to retain backups | `30` |
| `LOG_FILE` | Log file path | `./backup.log` |
| `DRY_RUN` | Dry-run mode | `false` |
| `DROP_DB_BEFORE_RESTORE` | Drop DB before restore | `false` |

### Configuration File

Create a `.backup.env` file in the scripts directory:

```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ree_ai
POSTGRES_USER=ree_ai_user
POSTGRES_PASSWORD=your_password_here

# Backup settings
BACKUP_DIR=./backups
RETENTION_DAYS=30

# S3 (optional)
S3_ENABLED=false
S3_BUCKET=my-bucket
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Email (optional)
ENABLE_EMAIL=false
EMAIL_RECIPIENT=ops@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## Usage Examples

### Basic Backup

```bash
# Linux/Mac
export POSTGRES_PASSWORD="my_password"
./scripts/backup.sh

# Windows
$env:POSTGRES_PASSWORD = "my_password"
.\scripts\backup.ps1
```

### Backup with Docker

```bash
# When PostgreSQL is in a Docker container
export POSTGRES_HOST=postgres  # container name
export POSTGRES_PASSWORD="password"
./scripts/backup.sh
```

### Backup to S3

```bash
export POSTGRES_PASSWORD="password"
export S3_ENABLED=true
export S3_BUCKET=my-backup-bucket
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
./scripts/backup.sh
```

### Scheduled Backup (Linux/Mac with Cron)

```bash
# Edit crontab
crontab -e

# Add backup job (daily at 2 AM)
0 2 * * * cd /path/to/ree-ai && \
  POSTGRES_PASSWORD=your_password \
  S3_ENABLED=true \
  S3_BUCKET=my-bucket \
  ./scripts/backup.sh >> ./scripts/backup.log 2>&1
```

### Scheduled Backup (Windows with Task Scheduler)

```powershell
# Create PowerShell script: backup-task.ps1
$env:POSTGRES_PASSWORD = "your_password"
$env:S3_ENABLED = "true"
$env:S3_BUCKET = "my-bucket"
Set-Location "C:\path\to\ree-ai"
.\scripts\backup.ps1

# Create scheduled task (run as administrator)
$trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\path\to\backup-task.ps1"
Register-ScheduledTask -TaskName "REE-AI-Backup" -Trigger $trigger -Action $action -RunLevel Highest
```

### Dry-Run (Preview Without Changes)

```bash
# Linux/Mac
./scripts/backup.sh --dry-run

# Windows
.\scripts\backup.ps1 -DryRun
```

### Restore Operations

```bash
# List available backups
./scripts/restore.sh list

# Restore specific backup
./scripts/restore.sh restore ree-ai-backup_20241029_120000

# Restore latest backup
./scripts/restore.sh restore latest

# Verify backup before restore
./scripts/restore.sh verify ree-ai-backup_20241029_120000

# Restore with database drop (caution!)
export DROP_DB_BEFORE_RESTORE=true
./scripts/restore.sh restore latest
```

## What Gets Backed Up

### PostgreSQL
- Complete database dump (SQL format)
- All tables, indexes, and data
- Database schema and objects

### OpenSearch (Optional)
- Cluster state
- Index metadata
- Index settings and mappings
- Does NOT include actual documents (use OpenSearch snapshots for that)

### Configuration Files
- `.env` - Environment configuration
- `docker-compose.yml` - Docker setup
- `Makefile` - Build configuration
- Additional files specified in `BACKUP_CONFIG_FILES`

## Backup File Structure

```
backups/
├── ree-ai-backup_20241029_120000.tar.gz
│   └── ree-ai-backup_20241029_120000/
│       ├── postgres_dump.sql          # PostgreSQL database dump
│       ├── opensearch_snapshot.json   # OpenSearch state
│       ├── opensearch_indices.json    # OpenSearch indices list
│       └── config/
│           ├── .env
│           ├── docker-compose.yml
│           └── Makefile
└── ree-ai-backup_20241028_120000.tar.gz
```

## Verification and Validation

### Check Backup Status

```bash
# Check backup log
tail -f ./scripts/backup.log

# List created backups
ls -lh ./backups/

# Check backup size
du -sh ./backups/ree-ai-backup_*.tar.gz

# Verify backup integrity
./scripts/restore.sh verify ree-ai-backup_20241029_120000
```

### Verify PostgreSQL Backup

```bash
# Extract and inspect SQL
tar -xzf backups/ree-ai-backup_*.tar.gz
grep "CREATE TABLE" ree-ai-backup_*/postgres_dump.sql | head

# Restore to test database
export POSTGRES_DB=ree_ai_test
./scripts/restore.sh restore latest
```

## Error Handling

### Common Issues

**PostgreSQL connection refused:**
```
Error: Could not connect to database
Solution:
- Verify POSTGRES_HOST and POSTGRES_PORT
- Check PostgreSQL is running
- Verify POSTGRES_PASSWORD is correct
```

**S3 upload failed:**
```
Error: AWS credentials not valid
Solution:
- Verify S3_BUCKET exists
- Check AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
- Ensure IAM user has s3:PutObject permission
```

**No compression utility found:**
```
Error: Could not compress backup
Solution (Windows): Install 7-Zip or use built-in Compress-Archive
Solution (Linux): Install gzip: apt-get install gzip
```

**Email notification failed:**
```
Error: Could not send email
Solution:
- Verify SMTP_SERVER is correct
- Check SMTP_USER and SMTP_PASSWORD
- For Gmail, use app password not regular password
- Ensure firewall allows SMTP traffic
```

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Backup/restore completed successfully |
| 1 | General error | Check logs for details |
| 2 | Configuration error | Missing or invalid configuration |
| 3 | Backup error | Backup operation failed |
| 4 | Upload error | S3 or other upload failed |
| 5 | Cleanup error | Failed to clean old backups |

## Performance Considerations

### Database Size Impact

- PostgreSQL dump size ≈ database size
- Compressed size typically 10-30% of original
- Large databases (>10GB) may need increased memory

### Backup Duration

- Small DB (<1GB): ~1-5 minutes
- Medium DB (1-10GB): ~5-30 minutes
- Large DB (>10GB): >30 minutes

### Network Impact

- S3 upload speed depends on connection
- Consider scheduling during low-traffic hours
- Monitor bandwidth for large databases

## Security Best Practices

1. **Protect Environment File**
   ```bash
   chmod 600 scripts/.backup.env
   ```

2. **Use Strong Passwords**
   - Generate strong PostgreSQL passwords
   - Use IAM roles for AWS credentials (avoid long-term keys)

3. **Encrypt Backups in Transit**
   - Use HTTPS for S3 uploads (default)
   - Use TLS for SMTP (port 587 or 465)

4. **Store Backups Securely**
   - Keep local backups in secure location
   - Use S3 bucket policies to restrict access
   - Consider encryption at rest for S3

5. **Rotate Credentials**
   - Rotate PostgreSQL passwords periodically
   - Rotate AWS IAM keys regularly
   - Update SMTP credentials as needed

6. **Monitor Backups**
   - Set up email alerts on failures
   - Regularly verify backup integrity
   - Test restore procedures

## Troubleshooting

### Enable Debug Logging

```bash
# View detailed logs
tail -100 ./scripts/backup.log

# Create log with increased verbosity
./scripts/backup.sh 2>&1 | tee backup_debug.log
```

### Test Database Connectivity

```bash
# Test PostgreSQL connection
psql -h localhost -U ree_ai_user -d ree_ai -c "SELECT version();"

# Test OpenSearch connection
curl -X GET "localhost:9200/"

# Test S3 access
aws s3 ls s3://my-bucket/
```

### Validate Configuration

```bash
# Print environment variables
./scripts/backup.sh --help

# Check prerequisites
which pg_dump
which tar
which gzip
```

## Restore Testing

It's critical to test restore procedures regularly:

```bash
# 1. List available backups
./scripts/restore.sh list

# 2. Create test database
createdb ree_ai_test

# 3. Verify backup integrity
./scripts/restore.sh verify ree-ai-backup_20241029_120000

# 4. Test restore (dry-run first)
DRY_RUN=true ./scripts/restore.sh restore ree-ai-backup_20241029_120000

# 5. Perform actual restore
POSTGRES_DB=ree_ai_test ./scripts/restore.sh restore ree-ai-backup_20241029_120000

# 6. Verify restored data
psql -d ree_ai_test -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';"

# 7. Clean up test database
dropdb ree_ai_test
```

## Additional Resources

- [PostgreSQL Backup Documentation](https://www.postgresql.org/docs/current/backup.html)
- [OpenSearch Backup and Restore](https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/)
- [AWS S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/BestPractices.html)
- [Docker Volume Backup](https://docs.docker.com/storage/volumes/#backup-restore-or-migrate-data-volumes)

## Support and Contributing

For issues, improvements, or questions:

1. Check logs: `./scripts/backup.log`
2. Verify configuration: `./scripts/.backup.env`
3. Test connectivity to services
4. Review error codes and exit status

## License

These scripts are part of the REE AI Platform and follow the same license.

---

**Last Updated:** October 29, 2024
**Version:** 1.0
