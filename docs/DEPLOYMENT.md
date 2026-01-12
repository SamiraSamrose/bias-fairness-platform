# Deployment Guide

## Prerequisites

- Python 3.9+
- 8GB RAM minimum
- 10GB disk space
- Internet connection

## Local Deployment

### 1. Clone Repository
```bash
git clone https://github.com/samirasamrose/bias-fairness-platform.git
cd bias-fairness-platform
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Unix/macOS
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 5. Run Application
```bash
python backend/app.py
```

Access at `http://localhost:5000`

---

## Docker Deployment

### 1. Build Image
```bash
docker-compose build
```

### 2. Start Services
```bash
docker-compose up -d
```

### 3. View Logs
```bash
docker-compose logs -f
```

### 4. Stop Services
```bash
docker-compose down
```

---

## Production Deployment

### AWS Elastic Beanstalk

1. Install EB CLI
```bash
pip install awsebcli
```

2. Initialize EB
```bash
eb init -p python-3.9 bias-fairness-platform
```

3. Create Environment
```bash
eb create production-env
```

4. Deploy
```bash
eb deploy
```

### Heroku

1. Install Heroku CLI

2. Create App
```bash
heroku create bias-fairness-platform
```

3. Set Environment Variables
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set SALESFORCE_CLIENT_ID=your-client-id
```

4. Deploy
```bash
git push heroku main
```

### Azure App Service

1. Install Azure CLI

2. Create Resource Group
```bash
az group create --name bias-fairness-rg --location eastus
```

3. Create App Service Plan
```bash
az appservice plan create --name bias-fairness-plan --resource-group bias-fairness-rg --sku B1 --is-linux
```

4. Create Web App
```bash
az webapp create --resource-group bias-fairness-rg --plan bias-fairness-plan --name bias-fairness-app --runtime "PYTHON|3.9"
```

5. Deploy Code
```bash
az webapp up --name bias-fairness-app
```

---

## Configuration

### Environment Variables

Required:
- `SECRET_KEY`: Flask secret key
- `SALESFORCE_CLIENT_ID`: Salesforce OAuth client ID
- `SALESFORCE_CLIENT_SECRET`: Salesforce OAuth client secret
- `SALESFORCE_USERNAME`: Salesforce username
- `SALESFORCE_PASSWORD`: Salesforce password
- `SALESFORCE_SECURITY_TOKEN`: Salesforce security token

Optional:
- `SLACK_WEBHOOK_URL`: Slack webhook for alerts
- `TABLEAU_SERVER_URL`: Tableau Server URL
- `TABLEAU_USERNAME`: Tableau username
- `TABLEAU_PASSWORD`: Tableau password

### Salesforce Setup

1. Create Connected App in Salesforce
2. Enable OAuth settings
3. Add callback URL
4. Copy Client ID and Secret
5. Generate Security Token

### Slack Setup

1. Create Slack App
2. Enable Incoming Webhooks
3. Add webhook to workspace
4. Copy Webhook URL

### Tableau Setup

1. Create Tableau Online/Server account
2. Generate Personal Access Token
3. Create project for data sources
4. Configure permissions

---

## Monitoring

### Health Checks
```bash
curl http://localhost:5000/api/health
```

### Logs
```bash
tail -f logs/app.log
```

### Metrics
Monitor:
- API response times
- Model training duration
- Alert generation rate
- Dataset download times

---

## Backup

### Database
```bash
cp data/processed/model_registry.json backups/
cp data/processed/audit_log.json backups/
```

### Exports
```bash
tar -czf tableau-exports.tar.gz exports/tableau/
```

---

## Troubleshooting

### Port Already in Use
```bash
# Change port in config.py
PORT = 5001
```

### Dataset Download Failures
- Check internet connection
- Verify dataset URLs
- Check firewall settings

### Salesforce Authentication Errors
- Verify credentials
- Check security token
- Confirm IP allowlist

### Slack Alerts Not Working
- Verify webhook URL
- Check webhook permissions
- Test webhook manually

---

## Performance Optimization

### Caching
- Datasets cached in `data/raw/`
- Preprocessed data cached in memory
- Model registry persisted to disk

### Scaling
- Use Gunicorn for production: `gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app`
- Enable Redis for session management
- Use PostgreSQL for persistent storage
- Deploy behind load balancer

---

## Security Best Practices

1. Never commit `.env` file
2. Use HTTPS in production
3. Enable CORS restrictions
4. Implement rate limiting
5. Regular security audits
6. Keep dependencies updated
7. Use secrets management service
