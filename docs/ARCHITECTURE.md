# System Architecture

## Overview

The Algorithmic Bias & Fairness Observability Platform is built using a modular architecture with clear separation between data processing, model training, fairness analysis, and presentation layers.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  (HTML/CSS/JavaScript + Plotly.js)                         │
│  - Dashboard                                                │
│  - Fairness Metrics Visualization                          │
│  - Temporal Monitoring                                      │
│  - Governance Dashboard                                     │
│  - Alerts Dashboard                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ REST API
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Backend Layer (Flask)                     │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Models     │  │  Services    │  │   Utils      │    │
│  │              │  │              │  │              │    │
│  │ DataLoader   │  │ Governance   │  │ Semantic     │    │
│  │ Preprocessor │  │ Alert        │  │ Metrics      │    │
│  │ Trainer      │  │ Salesforce   │  └──────────────┘    │
│  │ Fairness     │  │ Tableau      │                       │
│  │ Metrics      │  └──────────────┘                       │
│  └──────────────┘                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  Integration Layer                          │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐│
│  │  Salesforce API  │  │   Slack Webhook  │  │  Tableau  ││
│  │  Model Registry  │  │   Alert System   │  │  Cloud    ││
│  └──────────────────┘  └──────────────────┘  └───────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Components

### Frontend Layer
- **Technology**: HTML5, CSS3, Vanilla JavaScript, Plotly.js
- **Purpose**: Interactive dashboards for visualizing fairness metrics
- **Key Features**:
  - Real-time data visualization
  - Interactive charts and graphs
  - Responsive design
  - REST API integration

### Backend Layer

#### Models Package
- **DataLoader**: Downloads and caches datasets
- **Preprocessor**: Cleans and transforms data
- **Trainer**: Trains ML models
- **FairnessMetrics**: Computes fairness metrics

#### Services Package
- **GovernanceService**: Model registry and audit logging
- **AlertService**: Slack alert generation
- **SalesforceService**: Salesforce AI Model Registry integration
- **TableauService**: Data export for Tableau Cloud

#### Utils Package
- **SemanticMetrics**: Bias Delta Score and Fairness Stability Index

### Integration Layer
- **Salesforce**: Model registration and deployment
- **Slack**: Real-time alert notifications
- **Tableau Cloud**: Data visualization and reporting

## Data Flow

1. **Data Ingestion**: Datasets downloaded from remote sources
2. **Preprocessing**: Data cleaned and encoded
3. **Model Training**: Multiple classifiers trained
4. **Fairness Computation**: Five fairness metrics calculated
5. **Semantic Analysis**: Bias Delta Score and Fairness Stability Index computed
6. **Governance**: Models registered with compliance status
7. **Alerting**: Violations trigger Slack notifications
8. **Export**: Data exported to Tableau Cloud
9. **Visualization**: Metrics displayed in interactive dashboards

## Security

- Environment variables for sensitive credentials
- No hardcoded secrets
- HTTPS for external API calls
- Immutable audit logs with checksums

## Scalability

- Modular architecture allows independent scaling
- Stateless API design
- File-based caching for datasets
- JSON-based persistence for registry and audit logs

## Deployment

Supports multiple deployment options:
- Local development (Python virtual environment)
- Docker containerization
- Cloud platforms (AWS, Azure, GCP)
