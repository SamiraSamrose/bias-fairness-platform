# API Documentation

## Base URL
```
http://localhost:5000/api
```

## Endpoints

### Health Check
**GET** `/health`

Check API status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-04T10:00:00Z",
  "version": "1.0.0"
}
```

---

### Load Datasets
**POST** `/datasets/load`

Load and preprocess all datasets.

**Response:**
```json
{
  "status": "success",
  "datasets": {
    "compas": {
      "raw_records": 7214,
      "processed_records": 6172
    },
    "loan": {
      "raw_records": 614,
      "processed_records": 614
    },
    "census": {
      "raw_records": 32561,
      "processed_records": 30162
    }
  }
}
```

---

### Train Models
**POST** `/models/train`

Train models on all datasets and compute fairness metrics.

**Response:**
```json
{
  "status": "success",
  "results": {
    "compas": {
      "Logistic Regression": {
        "accuracy": 0.67,
        "demographic_parity_diff": 0.15,
        ...
      }
    }
  },
  "semantic_metrics": {
    "compas": {
      "bias_delta": {...},
      "stability": {...}
    }
  }
}
```

---

### Get Fairness Metrics
**GET** `/fairness/metrics`

Retrieve all fairness metrics.

**Response:**
```json
{
  "status": "success",
  "fairness_metrics": {
    "compas": {
      "Logistic Regression": {
        "demographic_parity_diff": 0.15,
        "equal_opportunity_diff": 0.08,
        ...
      }
    }
  }
}
```

---

### Get Semantic Metrics
**GET** `/semantic/metrics`

Retrieve Bias Delta Score and Fairness Stability Index.

**Response:**
```json
{
  "status": "success",
  "semantic_metrics": {
    "compas": {
      "bias_delta": {
        "mean_bias_delta": 0.12,
        "fairness_stability_index": 0.85
      }
    }
  }
}
```

---

### Get Model Registry
**GET** `/governance/registry`

Retrieve complete model registry.

**Response:**
```json
{
  "status": "success",
  "registry": {
    "v1_1234567890": {
      "version_id": "v1_1234567890",
      "model_name": "Logistic Regression",
      "dataset": "compas",
      "compliance_status": {
        "compliant": false,
        "violations": ["DEMOGRAPHIC_PARITY_VIOLATION"]
      }
    }
  }
}
```

---

### Get Audit Log
**GET** `/governance/audit-log`

Retrieve immutable audit log.

**Response:**
```json
{
  "status": "success",
  "audit_log": [
    {
      "audit_id": "AUD_1_1234567890",
      "timestamp": "2024-01-04T10:00:00Z",
      "event_type": "MODEL_REGISTRATION",
      "entity_id": "v1_1234567890",
      "checksum": "abc123..."
    }
  ]
}
```

---

### Get Compliance Report
**GET** `/governance/compliance`

Retrieve compliance statistics.

**Response:**
```json
{
  "status": "success",
  "compliance_report": {
    "total_models_registered": 9,
    "compliant_models": 5,
    "compliance_rate": 0.556,
    "violation_summary": {
      "DEMOGRAPHIC_PARITY_VIOLATION": 3,
      "DISPARATE_IMPACT_VIOLATION": 1
    }
  }
}
```

---

### Get Alerts
**GET** `/alerts`

Retrieve all generated alerts.

**Response:**
```json
{
  "status": "success",
  "alerts": [
    {
      "timestamp": "2024-01-04T10:00:00Z",
      "severity": "HIGH",
      "alert_type": "DEMOGRAPHIC_PARITY_VIOLATION",
      "model": "Logistic Regression",
      "dataset": "compas",
      "metric_value": 0.15,
      "threshold": 0.1
    }
  ]
}
```

---

### Get Salesforce Registry
**GET** `/salesforce/registry`

Retrieve Salesforce AI Model Registry data.

**Response:**
```json
{
  "status": "success",
  "salesforce_registry": [
    {
      "salesforce_model_id": "SF_MODEL_1_1234567890",
      "model_name": "Logistic Regression",
      "compliance_status": {
        "compliant": true,
        "compliance_score": 100
      },
      "deployment_status": "REGISTERED"
    }
  ]
}
```

---

### Deploy Model
**POST** `/salesforce/deploy/<model_id>`

Deploy model to production.

**Response:**
```json
{
  "status": "success",
  "deployment": {
    "deployment_id": "DEP_1",
    "sf_model_id": "SF_MODEL_1_1234567890",
    "environment": "PRODUCTION",
    "status": "ACTIVE"
  }
}
```

---

### Export Tableau Data
**GET** `/tableau/export`

Get manifest of exported Tableau files.

**Response:**
```json
{
  "status": "success",
  "manifest": {
    "export_directory": "/app/exports/tableau",
    "total_files": 5,
    "files": [
      {
        "filename": "performance_fairness.csv",
        "filepath": "/app/exports/tableau/performance_fairness.csv",
        "size_bytes": 1024
      }
    ]
  }
}
```

## Error Responses

All endpoints return error responses in the following format:

```json
{
  "status": "error",
  "message": "Error description"
}
```

HTTP Status Codes:
- 200: Success
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error
