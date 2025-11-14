# Master Data System - Production Readiness Checklist

## Overview

This checklist ensures that the Master Data Extraction System is production-ready before deployment. Review each item and check off when completed.

## Pre-Deployment Checklist

### 1. Infrastructure Setup

- [ ] **PostgreSQL Database**
  - [ ] Database server is running and accessible
  - [ ] Connection pool configured (min: 5, max: 20)
  - [ ] Backup strategy implemented (daily + hourly incremental)
  - [ ] Replication configured for high availability
  - [ ] Monitoring enabled (CPU, memory, disk I/O)

- [ ] **Redis Cache**
  - [ ] Redis server running with persistence (AOF + RDB)
  - [ ] Max memory policy configured (allkeys-lru)
  - [ ] Monitoring enabled

- [ ] **Docker Environment**
  - [ ] Docker Engine version >= 20.10
  - [ ] docker-compose version >= 1.29
  - [ ] Resource limits configured (CPU, memory)
  - [ ] Health checks configured for all services
  - [ ] Restart policies set to `unless-stopped`

### 2. Database Migrations

- [ ] **Schema Validation**
  - [ ] Run: `./scripts/migrate-master-data.sh status`
  - [ ] All migrations applied successfully
  - [ ] Migration history table exists
  - [ ] Backup created before migration

- [ ] **Master Data Tables**
  - [ ] All 11 master data tables exist
  - [ ] All translation tables exist
  - [ ] `pending_master_data` table created
  - [ ] Indexes created on foreign keys
  - [ ] Functions and views created

- [ ] **Seed Data**
  - [ ] Cities seeded (2 cities minimum)
  - [ ] Districts seeded (25 HCMC districts)
  - [ ] Property types seeded (12 types)
  - [ ] Amenities seeded (27 items)
  - [ ] Directions seeded (8 directions)
  - [ ] Furniture types seeded (4 types)
  - [ ] Legal statuses seeded (7 statuses)
  - [ ] View types seeded (9 types)
  - [ ] All translations present (vi, en minimum)

### 3. Service Configuration

- [ ] **Attribute Extraction Service**
  - [ ] Environment variables configured (`.env` file)
  - [ ] LLM API keys set (OpenAI or Ollama)
  - [ ] Database connection string correct
  - [ ] Redis connection string correct
  - [ ] Port 8084 accessible
  - [ ] Health endpoint responding: `http://localhost:8084/health`
  - [ ] API docs accessible: `http://localhost:8084/docs`

- [ ] **Crawler Service**
  - [ ] Chromium/Playwright installed
  - [ ] Rate limiting configured (1 req/sec)
  - [ ] User-agent set properly
  - [ ] Port 8095 accessible
  - [ ] Health endpoint responding: `http://localhost:8095/health`
  - [ ] Crawlers registered (batdongsan, mogi)

### 4. Security

- [ ] **Authentication**
  - [ ] JWT secret key changed from default
  - [ ] Token expiration configured (24h recommended)
  - [ ] Admin endpoints protected

- [ ] **API Security**
  - [ ] Rate limiting enabled
  - [ ] CORS configured properly
  - [ ] Request size limits set
  - [ ] SQL injection protection (parameterized queries)

- [ ] **Secrets Management**
  - [ ] No secrets in version control
  - [ ] `.env` file excluded from Git
  - [ ] Environment variables used for sensitive data
  - [ ] Secrets rotated regularly

- [ ] **Network Security**
  - [ ] Services communicate via internal network
  - [ ] PostgreSQL not exposed to public internet
  - [ ] Redis not exposed to public internet
  - [ ] Firewall rules configured

### 5. Testing

- [ ] **Unit Tests**
  - [ ] Language detection tests passing
  - [ ] Fuzzy matching tests passing
  - [ ] LLM translation tests passing

- [ ] **Integration Tests**
  - [ ] Run: `pytest tests/integration/test_extraction_pipeline.py -v`
  - [ ] All 6 test suites passing:
    - [ ] `test_extraction_with_master_data()`
    - [ ] `test_fuzzy_matching_accuracy()`
    - [ ] `test_admin_workflow()`
    - [ ] `test_orchestrator_integration()`
    - [ ] `test_crawler_integration()`
    - [ ] `test_performance_benchmarks()`

- [ ] **Health Checks**
  - [ ] Run: `./scripts/health-check.sh`
  - [ ] All checks passing
  - [ ] No critical warnings

- [ ] **Load Testing**
  - [ ] Extraction handles 10 concurrent requests
  - [ ] Response time < 2000ms under load
  - [ ] No memory leaks after 1000 requests
  - [ ] Database connections properly released

### 6. Monitoring & Logging

- [ ] **Application Logs**
  - [ ] Structured logging enabled
  - [ ] Log level configured (INFO for production)
  - [ ] Logs aggregated (ELK stack or CloudWatch)
  - [ ] Error tracking enabled (Sentry)

- [ ] **Metrics**
  - [ ] Prometheus metrics exposed
  - [ ] Grafana dashboards configured
  - [ ] Key metrics tracked:
    - [ ] Request rate
    - [ ] Error rate
    - [ ] Response time (p50, p95, p99)
    - [ ] Database query time
    - [ ] Cache hit rate

- [ ] **Alerts**
  - [ ] High error rate alert (> 5%)
  - [ ] Slow response time alert (> 3000ms)
  - [ ] Database connection pool exhausted
  - [ ] High pending master data count (> 100)

### 7. Performance

- [ ] **Benchmarks Met**
  - [ ] Extraction endpoint: < 2000ms (target)
  - [ ] Fuzzy matching: < 100ms per attribute
  - [ ] Database query: < 50ms
  - [ ] Cache hit rate: > 80%

- [ ] **Resource Optimization**
  - [ ] Connection pooling enabled
  - [ ] Redis caching enabled
  - [ ] Query indexes optimized
  - [ ] Batch processing for bulk operations

### 8. Documentation

- [ ] **Technical Documentation**
  - [ ] Architecture diagram updated
  - [ ] API documentation complete
  - [ ] Database schema documented
  - [ ] Deployment guide written

- [ ] **Operational Documentation**
  - [ ] Quick-start guide available
  - [ ] Troubleshooting guide created
  - [ ] Runbook for common issues
  - [ ] On-call procedures documented

- [ ] **User Documentation**
  - [ ] API usage examples
  - [ ] Admin workflow guide
  - [ ] Crawler usage guide

### 9. Data Quality

- [ ] **Master Data Validation**
  - [ ] No duplicate entries
  - [ ] All entries have English canonical names
  - [ ] All entries have Vietnamese translations
  - [ ] No orphaned translation records
  - [ ] Consistent naming conventions

- [ ] **Pending Data Management**
  - [ ] Admin review process documented
  - [ ] Approval workflow tested
  - [ ] Rejection workflow tested
  - [ ] Frequency tracking working

### 10. Disaster Recovery

- [ ] **Backup Strategy**
  - [ ] Automated daily backups
  - [ ] Backup retention policy (30 days)
  - [ ] Backup restoration tested
  - [ ] Offsite backup storage configured

- [ ] **Rollback Procedures**
  - [ ] Rollback scripts tested
  - [ ] Service rollback documented
  - [ ] Database rollback tested
  - [ ] Recovery time objective defined (< 1 hour)

- [ ] **High Availability**
  - [ ] Database replication configured
  - [ ] Service redundancy (multiple instances)
  - [ ] Load balancer configured
  - [ ] Failover tested

### 11. Compliance

- [ ] **Data Privacy**
  - [ ] GDPR compliance reviewed (if applicable)
  - [ ] Personal data handling documented
  - [ ] Data retention policies defined
  - [ ] User consent mechanisms in place

- [ ] **Crawling Ethics**
  - [ ] Robots.txt respected
  - [ ] Rate limiting prevents server overload
  - [ ] Only public data scraped
  - [ ] Source attribution in documentation

### 12. Deployment Process

- [ ] **Pre-Deployment**
  - [ ] Code review completed
  - [ ] All tests passing
  - [ ] Staging environment tested
  - [ ] Database backup created

- [ ] **Deployment**
  - [ ] Run: `./scripts/deploy-master-data-system.sh`
  - [ ] Services started successfully
  - [ ] Health checks passing
  - [ ] Smoke tests passing

- [ ] **Post-Deployment**
  - [ ] Verify all endpoints accessible
  - [ ] Monitor logs for errors
  - [ ] Run integration tests
  - [ ] Performance monitoring active

- [ ] **Rollback Plan**
  - [ ] Previous version tagged in Git
  - [ ] Database backup available
  - [ ] Rollback procedure documented
  - [ ] Rollback tested in staging

## Production Deployment Commands

### 1. Create Pre-Deployment Backup
```bash
./scripts/migrate-master-data.sh backup pre-deployment-$(date +%Y%m%d)
```

### 2. Run Migrations
```bash
./scripts/migrate-master-data.sh up
```

### 3. Deploy Services
```bash
./scripts/deploy-master-data-system.sh
```

### 4. Verify Health
```bash
./scripts/health-check.sh
```

### 5. Run Integration Tests
```bash
pytest tests/integration/test_extraction_pipeline.py -v
```

## Post-Deployment Monitoring

### First 24 Hours
- [ ] Monitor error rates every hour
- [ ] Check response times
- [ ] Review database performance
- [ ] Verify crawler functioning
- [ ] Check pending master data queue

### First Week
- [ ] Daily error log review
- [ ] Weekly performance report
- [ ] Admin review pending items
- [ ] User feedback collection

### First Month
- [ ] Monthly master data growth report
- [ ] Performance optimization review
- [ ] Capacity planning review
- [ ] Documentation updates

## Emergency Contacts

### On-Call Engineer
- Name: _______________
- Phone: _______________
- Email: _______________

### Database Administrator
- Name: _______________
- Phone: _______________
- Email: _______________

### DevOps Lead
- Name: _______________
- Phone: _______________
- Email: _______________

## Rollback Procedure

If critical issues occur:

1. **Stop new traffic**: Scale down to zero or redirect to maintenance page
2. **Restore database**: `./scripts/migrate-master-data.sh restore <backup-file>`
3. **Rollback services**: `docker-compose down && git checkout <previous-tag> && docker-compose up -d`
4. **Verify system**: `./scripts/health-check.sh`
5. **Resume traffic**: Scale up or remove maintenance page
6. **Post-mortem**: Document issues and lessons learned

## Sign-Off

- [ ] **Development Team Lead**: ______________ Date: __________
- [ ] **QA Lead**: ______________ Date: __________
- [ ] **DevOps Lead**: ______________ Date: __________
- [ ] **Product Owner**: ______________ Date: __________

---

**Version**: 1.0.0
**Last Updated**: 2025-01-13
**Next Review**: 2025-02-13
