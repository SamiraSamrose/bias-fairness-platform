# Setup Guide

## Prerequisites

- Python 3.9 or higher
- pip 21.0 or higher
- 8GB RAM minimum
- Internet connection for dataset downloads

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/samirasamrose/bias-fairness-platform.git
cd bias-fairness-platform
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Unix/macOS
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file:

```env
FLASK_APP=backend/app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///fairness.db

# Salesforce Configuration
SALESFORCE_CLIENT_ID=your-client-id
SALESFORCE_CLIENT_SECRET=your-client-secret
SALESFORCE_USERNAME=your-username
SALESFORCE_PASSWORD=your-password
SALESFORCE_SECURITY_TOKEN=your-token

# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Tableau Configuration
TABLEAU_SERVER_URL=https://your-tableau-server.com
TABLEAU_SITE_ID=your-site-id
TABLEAU_USERNAME=your-username
TABLEAU_PASSWORD=your-password
```

### 5. Initialize Database

```bash
python backend/app.py init-db
```

### 6. Download Datasets

Datasets will be automatically downloaded on first run. Alternatively:

```bash
python backend/models/data_loader.py
```

### 7. Run Application

```bash
python backend/app.py
```

Application will start at `http://localhost:5000`

## Verification

### Test API Endpoints

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{"status": "healthy", "timestamp": "2024-01-03T10:00:00Z"}
```

### Access Web Interface

Navigate to `http://localhost:5000` in your browser.

## Troubleshooting

### Port Already in Use

```bash
# Change port in backend/config.py
PORT = 5001
```

### Missing Dependencies

```bash
pip install --upgrade -r backend/requirements.txt
```

### Dataset Download Failures

Manually download datasets:
- COMPAS: https://raw.githubusercontent.com/propublica/compas-analysis/master/compas-scores-two-years.csv
- Loan: https://raw.githubusercontent.com/dphi-official/Datasets/master/Loan_Data/loan_train.csv
- Census: https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data

Place in `data/raw/` directory.

## Production Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment instructions.
