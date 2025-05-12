# OKR Tracker - Production Deployment Guide

This document outlines how to deploy the OKR Tracker application in a production environment using Docker.

## Docker Deployment

### 1. Create a Dockerfile

Create a file named `Dockerfile` in the project root:

```dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy project
COPY . .

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Run gunicorn
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "run:app"]
```

### 2. Add Production Requirements

Update your `requirements.txt` or create a `requirements-prod.txt` with production dependencies:

```
# Add to requirements.txt or create new requirements-prod.txt
gunicorn==21.2.0
psycopg2-binary==2.9.9  # For PostgreSQL
```

### 3. Create Docker Compose Configuration

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  web:
    build: .
    restart: always
    depends_on:
      - db
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_DB=${POSTGRES_DB}
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/nginx/ssl
      - ./app/static:/app/static
    depends_on:
      - web
    networks:
      - app-network

networks:
  app-network:

volumes:
  postgres_data:
```

### 4. Configure Nginx as Reverse Proxy

Create a directory `nginx/conf.d` and add a configuration file:

```nginx
# nginx/conf.d/app.conf
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";
    
    # Serve static files directly
    location /static/ {
        alias /app/static/;
        expires 30d;
    }
    
    # Proxy requests to the Flask application
    location / {
        proxy_pass http://web:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. Update Application Configuration for Production

Modify `app/config.py` to include production settings:

```python
# Add to config.py
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # Additional production settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
```

### 6. Create an Environment File

Create a `.env` file for your Docker Compose environment variables:

```
SECRET_KEY=your-very-secure-secret-key
DATABASE_URL=postgresql://postgres:password@db:5432/okr
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=okr
```

### 7. WSGI Server Configuration

Gunicorn is used as the WSGI server. The configuration is included in the Dockerfile CMD. For more complex requirements, create a `gunicorn.conf.py`:

```python
# gunicorn.conf.py
workers = 4
bind = "0.0.0.0:5000"
timeout = 120
keepalive = 5
worker_class = "gevent"
accesslog = "-"
errorlog = "-"
```

### 8. Database Migration for Production

Before deploying, prepare your database migrations:

```bash
# Generate migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

Update `run.py` to handle migrations in production:

```python
# Add to run.py before app.run()
with app.app_context():
    if os.environ.get('FLASK_ENV') == 'production':
        from flask_migrate import upgrade
        upgrade()
```

## Deployment Steps

1. **Build and start the containers**:
   ```bash
   docker-compose up -d --build
   ```

2. **Initialize the database** (first time only):
   ```bash
   docker-compose exec web flask db upgrade
   ```

3. **Monitor the application**:
   ```bash
   docker-compose logs -f
   ```

## Security Considerations

1. **Secret Management**:
   - Never commit `.env` files or secrets to version control
   - Consider using Docker secrets or a vault solution for production

2. **Database Security**:
   - Use strong passwords
   - Restrict network access to the database
   - Regularly backup the database

3. **SSL/TLS**:
   - Always use HTTPS in production
   - Keep certificates up to date
   - Configure proper SSL security headers

4. **Regular Updates**:
   - Keep all dependencies updated
   - Regularly apply security patches

## Scaling Options

1. **Horizontal Scaling**:
   - Deploy multiple instances of the web container
   - Configure nginx for load balancing

2. **Database Scaling**:
   - Consider read replicas for database scaling
   - Implement connection pooling

3. **Container Orchestration**:
   - For more complex deployments, consider Kubernetes
   - Use Docker Swarm for simple multi-host orchestration

## Monitoring and Logging

1. **Application Monitoring**:
   - Implement health checks
   - Set up monitoring with Prometheus/Grafana

2. **Logging**:
   - Configure centralized logging with ELK stack or similar
   - Implement structured logging in the application

## Backup Strategy

1. **Database Backups**:
   - Schedule regular database dumps
   - Store backups securely off-site

2. **Application State**:
   - Back up configuration files
   - Version control all code changes