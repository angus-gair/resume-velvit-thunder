# Deployment Guide

This guide provides instructions for deploying Resume Velvit Thunder in different environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Deployment Options](#deployment-options)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Frontend Deployment](#frontend-deployment)
- [Backend Deployment](#backend-deployment)
- [Scaling](#scaling)
- [Monitoring](#monitoring)
- [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Docker and Docker Compose
- PostgreSQL 12+ (for production)
- Node.js 16.x+ (for building frontend)
- Python 3.9+ (for backend)
- Nginx or similar web server (for production)
- SSL certificate (for HTTPS)

## Deployment Options

### 1. Development (Docker Compose)

```bash
# Clone the repository
git clone https://github.com/yourusername/resume-velvit-thunder.git
cd resume-velvit-thunder

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your configuration

# Start services
docker-compose up -d
```

### 2. Production (Kubernetes)

See the `kubernetes/` directory for Kubernetes manifests.

### 3. Serverless (AWS Lambda + API Gateway)

See the `serverless/` directory for serverless configuration.

## Environment Configuration

### Required Environment Variables

```env
# Backend
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_GA_TRACKING_ID=UA-XXXXX-Y
```

### Optional Environment Variables

```env
# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=user@example.com
EMAIL_HOST_PASSWORD=your-email-password

# Storage (AWS S3 example)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
```

## Database Setup

### PostgreSQL

```bash
# Create database
createdb resume_velvit_thunder

# Create user
createuser --pwprompt resume_user

# Grant privileges
grant all privileges on database resume_velvit_thunder to resume_user;

# Run migrations
python manage.py migrate
```

### Database Backups

```bash
# Create backup
pg_dump -U username -d resume_velvit_thunder > backup_$(date +%Y%m%d).sql

# Restore from backup
psql -U username -d resume_velvit_thunder < backup_file.sql
```

## Frontend Deployment

### Production Build

```bash
cd apps/web
npm install
npm run build
```

### Static File Serving

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        root /path/to/resume-velvit-thunder/apps/web/out;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Backend Deployment

### Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 --threads 2 api.main:app
```

### Systemd Service

```ini
# /etc/systemd/system/resume-velvit-thunder.service
[Unit]
Description=Resume Velvit Thunder API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/resume-velvit-thunder
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 4 --threads 2 api.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## Scaling

### Horizontal Scaling

1. **Load Balancing**: Use Nginx or a cloud load balancer
2. **Database**: Consider read replicas for read-heavy workloads
3. **Caching**: Implement Redis for session storage and caching

### Vertical Scaling

1. **Database**: Increase CPU, RAM, and storage as needed
2. **Application Servers**: Scale up server resources
3. **Storage**: Use scalable storage solutions like S3

## Monitoring

### Application Monitoring

- **Prometheus + Grafana**: For metrics and dashboards
- **Sentry**: For error tracking
- **Logging**: Centralized logging with ELK Stack or similar

### Health Checks

```bash
# Health check endpoint
curl http://localhost:8000/health

# Metrics endpoint (if enabled)
curl http://localhost:8000/metrics
```

## Backup and Recovery

### Regular Backups

1. **Database**: Daily backups with retention policy
2. **Media Files**: Regular backups of uploaded files
3. **Configuration**: Version control for all configuration files

### Disaster Recovery

1. **Backup Verification**: Regularly test backup restoration
2. **Recovery Plan**: Documented recovery procedures
3. **Failover**: Set up failover systems if needed

## Troubleshooting

### Common Issues

**Application Not Starting**
- Check logs: `journalctl -u resume-velvit-thunder -f`
- Verify database connection
- Check port availability

**Database Connection Issues**
- Verify database server is running
- Check connection string in `.env`
- Verify user permissions

**Performance Issues**
- Check database queries with `EXPLAIN ANALYZE`
- Monitor system resources
- Review application logs for slow requests

**Updating the Application**

```bash
# Pull latest changes
git pull

# Install new dependencies
pip install -r requirements.txt
cd apps/web && npm install

# Run migrations
python manage.py migrate

# Rebuild frontend
cd apps/web && npm run build

# Restart services
sudo systemctl restart resume-velvit-thunder
```

## Security Considerations

- Keep all dependencies up to date
- Use strong, unique passwords
- Implement rate limiting
- Enable HTTPS
- Regular security audits
- Follow principle of least privilege

## Support

For deployment support, contact devops@resume-velvit-thunder.com or open an issue on GitHub.
