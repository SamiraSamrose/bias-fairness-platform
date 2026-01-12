import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class GovernanceService:
    """Manages model governance, registry, and audit logging"""
    
    def __init__(self, registry_path: str, audit_log_path: str):
        self.registry_path = registry_path
        self.audit_log_path = audit_log_path
        self.model_registry = self._load_registry()
        self.audit_log = self._load_audit_log()
        self.version_counter = len(self.model_registry)
    
    def _load_registry(self) -> Dict:
        """Load model registry from file"""
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_audit_log(self) -> List:
        """Load audit log from file"""
        if os.path.exists(self.audit_log_path):
            with open(self.audit_log_path, 'r') as f:
                return json.load(f)
        return []
    
    def _save_registry(self):
        """Save model registry to file"""
        with open(self.registry_path, 'w') as f:
            json.dump(self.model_registry, f, indent=2)
    
    def _save_audit_log(self):
        """Save audit log to file"""
        with open(self.audit_log_path, 'w') as f:
            json.dump(self.audit_log, f, indent=2)
    
    def register_model(self, model_name: str, dataset: str, metrics: Dict, model_hash: str) -> str:
        """
        Register a model with full metadata
        
        Returns:
            version_id: Unique version identifier
        """
        self.version_counter += 1
        version_id = f"v{self.version_counter}_{int(datetime.now().timestamp())}"
        
        registration_record = {
            'version_id': version_id,
            'model_name': model_name,
            'dataset': dataset,
            'registration_timestamp': datetime.now().isoformat(),
            'performance_metrics': {
                'accuracy': metrics.get('accuracy', 0),
                'precision': metrics.get('precision', 0),
                'recall': metrics.get('recall', 0),
                'f1_score': metrics.get('f1_score', 0),
                'roc_auc': metrics.get('roc_auc', 0)
            },
            'fairness_metrics': {
                'demographic_parity_diff': metrics.get('demographic_parity_diff', 0),
                'equal_opportunity_diff': metrics.get('equal_opportunity_diff', 0),
                'equalized_odds_diff': metrics.get('equalized_odds_diff', 0),
                'disparate_impact_ratio': metrics.get('disparate_impact_ratio', 1),
                'statistical_parity_diff': metrics.get('statistical_parity_diff', 0)
            },
            'compliance_status': self._check_compliance(metrics),
            'model_hash': model_hash
        }
        
        self.model_registry[version_id] = registration_record
        self._save_registry()
        self._log_audit_event('MODEL_REGISTRATION', version_id, registration_record)
        
        logger.info(f"Model registered: {version_id}")
        return version_id
    
    def _check_compliance(self, metrics: Dict) -> Dict:
        """Check if model meets fairness compliance thresholds"""
        thresholds = {
            'demographic_parity_diff': 0.1,
            'equal_opportunity_diff': 0.1,
            'equalized_odds_diff': 0.1,
            'disparate_impact_ratio_min': 0.8,
            'disparate_impact_ratio_max': 1.25
        }
        
        violations = []
        
        if abs(metrics.get('demographic_parity_diff', 0)) > thresholds['demographic_parity_diff']:
            violations.append('DEMOGRAPHIC_PARITY_VIOLATION')
        
        if abs(metrics.get('equal_opportunity_diff', 0)) > thresholds['equal_opportunity_diff']:
            violations.append('EQUAL_OPPORTUNITY_VIOLATION')
        
        if abs(metrics.get('equalized_odds_diff', 0)) > thresholds['equalized_odds_diff']:
            violations.append('EQUALIZED_ODDS_VIOLATION')
        
        dir_value = metrics.get('disparate_impact_ratio', 1)
        if dir_value < thresholds['disparate_impact_ratio_min'] or dir_value > thresholds['disparate_impact_ratio_max']:
            violations.append('DISPARATE_IMPACT_VIOLATION')
        
        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'checked_at': datetime.now().isoformat()
        }
    
    def _log_audit_event(self, event_type: str, entity_id: str, details: Dict):
        """Log immutable audit event"""
        audit_entry = {
            'audit_id': f"AUD_{len(self.audit_log) + 1}_{int(datetime.now().timestamp())}",
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'entity_id': entity_id,
            'details': details,
            'checksum': hashlib.sha256(json.dumps(details, sort_keys=True).encode()).hexdigest()
        }
        
        self.audit_log.append(audit_entry)
        self._save_audit_log()
    
    def get_model_history(self, model_name: str) -> List[Dict]:
        """Get version history for a model"""
        history = []
        for version_id, record in self.model_registry.items():
            if record['model_name'] == model_name:
                history.append(record)
        return sorted(history, key=lambda x: x['registration_timestamp'], reverse=True)
    
    def get_compliance_report(self) -> Dict:
        """Generate comprehensive compliance report"""
        total_models = len(self.model_registry)
        compliant_models = sum(1 for r in self.model_registry.values()
                              if r['compliance_status']['compliant'])
        
        violation_summary = {}
        for record in self.model_registry.values():
            for violation in record['compliance_status']['violations']:
                violation_summary[violation] = violation_summary.get(violation, 0) + 1
        
        return {
            'total_models_registered': total_models,
            'compliant_models': compliant_models,
            'non_compliant_models': total_models - compliant_models,
            'compliance_rate': compliant_models / total_models if total_models > 0 else 0,
            'violation_summary': violation_summary,
            'report_generated_at': datetime.now().isoformat()
        }
    
    def get_audit_log(self) -> List[Dict]:
        """Get complete audit log"""
        return self.audit_log