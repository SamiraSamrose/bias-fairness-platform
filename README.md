# Algorithmic Bias & Fairness Observability Platform

Enterprise-grade platform for monitoring algorithmic fairness in production AI systems. Provides real-time bias detection, governance compliance, and integration with Salesforce AI Model Registry and Tableau Cloud.

Organizations deploying machine learning models face regulatory requirements for fairness and compliance. Models trained on historical data often perpetuate existing societal biases, leading to discriminatory outcomes in credit lending, criminal justice, employment and healthcare decisions.

The project addresses the critical gap between rapid AI deployment and responsible governance. Organizations deploy models affecting millions of lives without continuous fairness monitoring, leading to discriminatory outcomes in lending, hiring, criminal justice and healthcare. Regulatory frameworks increasingly mandate algorithmic fairness, but existing tools lack integrated monitoring, governance and alerting capabilities.

## Links
-**Source Code**: https://github.com/SamiraSamrose/bias-fairness-platform/tree/main

-**Video Demo**: https://youtu.be/gzsOBDAoutE

-**Notebook**: https://github.com/SamiraSamrose/bias-fairness-platform/blob/main/Algorithmic_Bias_%26_Fairness_Observability_Platform.ipynb

## Features and Usages

**Features:**

1. Automated dataset acquisition from remote sources with local caching
2. Data preprocessing with missing value imputation and categorical encoding
3. Multi-model training with three algorithms per dataset
4. Five fairness metric calculations with configurable thresholds
5. Bias Delta Score computation as weighted aggregate measure
6. Fairness Stability Index calculation for cross-model consistency
7. Immutable audit logging with cryptographic checksums
8. Model version tracking with timestamp-based identifiers
9. Compliance status determination against regulatory thresholds
10. Slack webhook integration for real-time alerts
11. Salesforce AI Model Registry synchronization
12. Tableau Cloud data export in CSV format
13. Interactive web dashboards with Plotly visualizations
14. Temporal drift monitoring with time-series analysis
15. RESTful API for programmatic access
16. Performance vs fairness trade-off visualization
17. Demographic disparity analysis across protected groups
18. Model deployment approval workflow based on compliance
19. Comprehensive metric comparison across datasets
20. Alert severity classification and filtering

**Usages:**

1. Monitor production ML models for fairness violations
2. Compare bias across multiple model architectures
3. Track fairness metrics over time to detect drift
4. Generate compliance reports for regulatory audits
5. Alert teams when models exceed fairness thresholds
6. Analyze trade-offs between accuracy and fairness
7. Document model governance with immutable logs
8. Export metrics to business intelligence tools
9. Evaluate models before production deployment
10. Identify which demographic groups are disadvantaged
11. Benchmark fairness across organizational models
12. Investigate historical bias patterns
13. Verify compliance with anti-discrimination laws
14. Support model retraining decisions with drift data
15. Integrate fairness monitoring into CI/CD pipelines

## Tech Stack

**Languages:** Python, JavaScript, HTML, CSS

**Frameworks:** Flask, Plotly.js

**Libraries:** pandas, numpy, scikit-learn, scipy, matplotlib, seaborn, aif360, requests, python-dotenv, gunicorn, simple-salesforce

**Tools:** Git, Docker, pip, virtualenv

**Services:** Salesforce AI Model Registry, Slack Webhooks, Tableau Cloud

**APIs:** Salesforce REST API, Slack Webhook API, Tableau REST API

**Models:** Logistic Regression, Random Forest, Gradient Boosting

**Data Integrations:** HTTP data fetching, CSV file processing, JSON persistence

**Datasets:** COMPAS Recidivism Dataset (ProPublica), Loan Approval Dataset (dphi-official), Census Income Dataset (UCI Machine Learning Repository)

**Databases:** JSON file storage (model_registry.json, audit_log.json), CSV file caching


## Quick Start

See [SETUP.md](SETUP.md) for detailed installation instructions.

```bash
# Clone repository
git clone https://github.com/samirasamrose/bias-fairness-platform.git
cd bias-fairness-platform

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run application
python backend/app.py
```

Access the platform at `http://localhost:5000`

## Functionality

**Data Processing:**
- Automated dataset loading from remote sources
- Missing value imputation using mode and median strategies
- Label encoding for categorical variables
- Feature scaling using standardization

**Model Training:**
- Three classifier algorithms per dataset
- Train-test split with stratification
- Probability score generation for ROC analysis

**Fairness Metrics:**
- Demographic Parity Difference calculation
- Equal Opportunity Difference measurement
- Equalized Odds Difference computation
- Disparate Impact Ratio calculation
- Statistical Parity Difference tracking

**Semantic Modeling:**
- Bias Delta Score aggregation across metrics
- Fairness Stability Index measuring consistency
- Prediction Drift Score for model divergence

**Governance:**
- Immutable audit logging with SHA-256 checksums
- Model version tracking with timestamps
- Compliance status determination against thresholds
- Model registration with metadata storage

**Alerting:**
- Threshold-based violation detection
- Slack webhook integration for notifications
- Severity classification (Critical, High, Medium, Low)
- Alert metadata storage

**Integration:**
- Salesforce AI Model Registry synchronization
- Tableau Cloud data export in CSV format
- RESTful API endpoints for all operations

**Visualization:**
- Interactive Plotly charts for metrics comparison
- Temporal drift monitoring graphs
- Performance vs fairness trade-off plots
- Compliance distribution pie charts


## Documentation

- [Setup Guide](SETUP.md) - Installation and configuration
- [API Documentation](docs/API.md) - REST API endpoints
- [Architecture](docs/ARCHITECTURE.md) - System design
- [Deployment](docs/DEPLOYMENT.md) - Production deployment

## License

MIT License
