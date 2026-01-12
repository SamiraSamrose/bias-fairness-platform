import json
import hashlib
from datetime import datetime
from typing import Dict, Optional
import logging

try:
    from simple_salesforce import Salesforce
    SALESFORCE_AVAILABLE = True
except ImportError:
    SALESFORCE_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("simple-salesforce not installed. Salesforce integration disabled.")

logger = logging.getLogger(__name__)

class SalesforceService:
    """Manages Salesforce AI Model Registry integration"""
    
    def __init__(self, username: str = None, password: str = None, 
                 security_token: str = None, domain: str = 'login'):
        self.username = username
        self.password = password
        self.security_token = security_token
        self.domain = domain
        self.sf_client = None
        self.registry = {}
        self.deployment_history = []
        
        if SALESFORCE_AVAILABLE and all([username, password, security_token]):
            try:
                self.sf_client = Salesforce(
                    username=username,
                    password=password,
                    security_token=security_token,
                    domain=domain
                )
                logger.info("Connected to Salesforce")
            except Exception as e:
                logger.error(f"Failed to connect to Salesforce: {e}")
                self.sf_client = None
    
    def register_model(self, model_name: str, dataset: str, metrics: Dict,
                      version_id: str, model_metadata: Dict) -> str:
        """
        Register model in Salesforce AI Model Registry
        
        Returns:
            salesforce_model_id: Unique Salesforce model identifier
        """
        sf_model_id = f"SF_MODEL_{len(self.registry) + 1}_{int(datetime.now().timestamp())}"
        
        registration_payload = {
            'salesforce_model_id': sf_model_id,
            'external_version_id': version_id,
            'model_name': model_name,
            'dataset': dataset,
            'registration_timestamp': datetime.now().isoformat(),
            'model_type': 'Binary Classifier',
            'framework': 'scikit-learn',
            'performance_metrics': {
                'accuracy': metrics.get('accuracy', 0),
                'precision': metrics.get('precision', 0),
                'recall': metrics.get('recall', 0),
                'f1_score': metrics.get('f1_score', 0),
                'roc_auc': metrics.get('roc_auc', 0)
            },
            'fairness_metrics': {
                'demographic_parity_difference': metrics.get('demographic_parity_diff', 0),
                'equal_opportunity_difference': metrics.get('equal_opportunity_diff', 0),
                'equalized_odds_difference': metrics.get('equalized_odds_diff', 0),
                'disparate_impact_ratio': metrics.get('disparate_impact_ratio', 1)
            },
            'compliance_status': self._determine_compliance(metrics),
            'deployment_status': 'REGISTERED',
            'metadata': model_metadata
        }
        
        self.registry[sf_model_id] = registration_payload
        
        if self.sf_client:
            try:
                self._sync_to_salesforce(registration_payload)
            except Exception as e:
                logger.error(f"Failed to sync to Salesforce: {e}")
        
        logger.info(f"Model registered in Salesforce: {sf_model_id}")
        return sf_model_id
    
    def _determine_compliance(self, metrics: Dict) -> Dict:
        """Determine compliance status based on fairness metrics"""
        violations = []
        
        if abs(metrics.get('demographic_parity_diff', 0)) > 0.1:
            violations.append('DEMOGRAPHIC_PARITY')
        if abs(metrics.get('equal_opportunity_diff', 0)) > 0.1:
            violations.append('EQUAL_OPPORTUNITY')
        if abs(metrics.get('equalized_odds_diff', 0)) > 0.1:
            violations.append('EQUALIZED_ODDS')
        
        dir_value = metrics.get('disparate_impact_ratio', 1)
        if dir_value < 0.8 or dir_value > 1.25:
            violations.append('DISPARATE_IMPACT')
        
        compliance_score = max(0, 100 - (len(violations) * 25))
        
        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'compliance_score': compliance_score
        }
    
    def _sync_to_salesforce(self, payload: Dict):
        """Sync model registration to Salesforce"""
        if not self.sf_client:
            return
        
        sf_record = {
            'Name': payload['model_name'],
            'Dataset__c': payload['dataset'],
            'Version_ID__c': payload['external_version_id'],
            'Accuracy__c': payload['performance_metrics']['accuracy'],
            'Compliance_Score__c': payload['compliance_status']['compliance_score'],
            'Registration_Date__c': payload['registration_timestamp']
        }
        
        try:
            result = self.sf_client.AI_Model__c.create(sf_record)
            logger.info(f"Synced to Salesforce: {result['id']}")
        except Exception as e:
            logger.error(f"Salesforce sync error: {e}")
    
    def deploy_model(self, sf_model_id: str, environment: str = 'PRODUCTION') -> Dict:
        """
        Deploy model to specified environment
        
        Returns:
            Deployment record or error dictionary
        """
        if sf_model_id not in self.registry:
            return {'error': 'Model not found in registry'}
        
        model_info = self.registry[sf_model_id]
        
        if not model_info['compliance_status']['compliant']:
            return {
                'error': 'Model cannot be deployed due to compliance violations',
                'violations': model_info['compliance_status']['violations']
            }
        
        deployment_record = {
            'deployment_id': f"DEP_{len(self.deployment_history) + 1}",
            'sf_model_id': sf_model_id,
            'model_name': model_info['model_name'],
            'environment': environment,
            'deployment_timestamp': datetime.now().isoformat(),
            'status': 'ACTIVE'
        }
        
        self.deployment_history.append(deployment_record)
        model_info['deployment_status'] = 'DEPLOYED'
        
        logger.info(f"Model deployed: {sf_model_id} to {environment}")
        return deployment_record
    
    def get_model_insights(self, sf_model_id: str) -> Dict:
        """Get comprehensive model insights for dashboard"""
        if sf_model_id not in self.registry:
            return {'error': 'Model not found'}
        
        model_info = self.registry[sf_model_id]
        
        insights = {
            'model_id': sf_model_id,
            'model_name': model_info['model_name'],
            'dataset': model_info['dataset'],
            'overall_score': self._calculate_overall_score(model_info),
            'performance_summary': {
                'accuracy': model_info['performance_metrics']['accuracy'],
                'f1_score': model_info['performance_metrics']['f1_score'],
                'roc_auc': model_info['performance_metrics']['roc_auc']
            },
            'fairness_summary': {
                'bias_detected': not model_info['compliance_status']['compliant'],
                'compliance_score': model_info['compliance_status']['compliance_score'],
                'primary_concerns': model_info['compliance_status']['violations']
            },
            'recommendations': self._generate_recommendations(model_info)
        }
        
        return insights
    
    def _calculate_overall_score(self, model_info: Dict) -> float:
        """Calculate overall model score (performance + fairness)"""
        perf_metrics = model_info['performance_metrics']
        perf_score = (perf_metrics['accuracy'] + perf_metrics['f1_score'] + 
                     perf_metrics['roc_auc']) / 3
        
        fairness_score = model_info['compliance_status']['compliance_score'] / 100
        
        overall = (perf_score * 0.6 + fairness_score * 0.4)
        return float(overall)
    
    def _generate_recommendations(self, model_info: Dict) -> list:
        """Generate actionable recommendations"""
        recommendations = []
        
        if not model_info['compliance_status']['compliant']:
            recommendations.append("Address fairness violations before deployment")
            
            for violation in model_info['compliance_status']['violations']:
                if violation == 'DEMOGRAPHIC_PARITY':
                    recommendations.append("Consider reweighting training data or using fairness constraints")
                elif violation == 'DISPARATE_IMPACT':
                    recommendations.append("Review feature selection and consider removing potentially biased features")
        
        if model_info['performance_metrics']['accuracy'] < 0.75:
            recommendations.append("Model accuracy below recommended threshold - consider retraining")
        
        if len(recommendations) == 0:
            recommendations.append("Model meets all compliance requirements and performance standards")
        
        return recommendations
    
    def export_registry(self) -> list:
        """Export registry for external systems"""
        return list(self.registry.values())