import os
import pandas as pd
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

class TableauService:
    """Manages Tableau Cloud data exports and API integration"""
    
    def __init__(self, export_dir: str):
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
    
    def export_performance_fairness(self, all_results: Dict) -> str:
        """
        Export model performance and fairness metrics
        
        Args:
            all_results: Dictionary with dataset -> model -> metrics
            
        Returns:
            Path to exported CSV file
        """
        records = []
        
        for dataset_name, model_results in all_results.items():
            for model_name, metrics in model_results.items():
                record = {
                    'dataset': dataset_name,
                    'model': model_name,
                    'accuracy': metrics.get('accuracy', 0),
                    'precision': metrics.get('precision', 0),
                    'recall': metrics.get('recall', 0),
                    'f1_score': metrics.get('f1_score', 0),
                    'roc_auc': metrics.get('roc_auc', 0),
                    'demographic_parity_diff': metrics.get('demographic_parity_diff', 0),
                    'equal_opportunity_diff': metrics.get('equal_opportunity_diff', 0),
                    'equalized_odds_diff': metrics.get('equalized_odds_diff', 0),
                    'disparate_impact_ratio': metrics.get('disparate_impact_ratio', 1),
                    'statistical_parity_diff': metrics.get('statistical_parity_diff', 0)
                }
                records.append(record)
        
        df = pd.DataFrame(records)
        filepath = os.path.join(self.export_dir, 'performance_fairness.csv')
        df.to_csv(filepath, index=False)
        
        logger.info(f"Exported performance_fairness: {len(df)} records")
        return filepath
    
    def export_semantic_metrics(self, semantic_results: Dict) -> str:
        """
        Export Bias Delta Score and Fairness Stability Index
        
        Args:
            semantic_results: Dictionary with dataset -> semantic metrics
            
        Returns:
            Path to exported CSV file
        """
        records = []
        
        for dataset_name, metrics in semantic_results.items():
            record = {
                'dataset': dataset_name,
                'mean_bias_delta': metrics['bias_delta']['mean_bias_delta'],
                'max_bias_delta': metrics['bias_delta']['max_bias_delta'],
                'min_bias_delta': metrics['bias_delta']['min_bias_delta'],
                'fairness_stability_index': metrics['stability']['fairness_stability_index'],
                'stability_category': metrics['stability']['stability_category']
            }
            records.append(record)
        
        df = pd.DataFrame(records)
        filepath = os.path.join(self.export_dir, 'semantic_metrics.csv')
        df.to_csv(filepath, index=False)
        
        logger.info(f"Exported semantic_metrics: {len(df)} records")
        return filepath
    
    def export_audit_log(self, audit_log: List[Dict]) -> str:
        """
        Export governance audit log
        
        Args:
            audit_log: List of audit entries
            
        Returns:
            Path to exported CSV file
        """
        df = pd.DataFrame(audit_log)
        filepath = os.path.join(self.export_dir, 'audit_log.csv')
        df.to_csv(filepath, index=False)
        
        logger.info(f"Exported audit_log: {len(df)} records")
        return filepath
    
    def export_alerts(self, alerts: List[Dict]) -> str:
        """
        Export fairness alerts
        
        Args:
            alerts: List of alert records
            
        Returns:
            Path to exported CSV file
        """
        if not alerts:
            logger.warning("No alerts to export")
            return None
        
        df = pd.DataFrame(alerts)
        filepath = os.path.join(self.export_dir, 'alerts.csv')
        df.to_csv(filepath, index=False)
        
        logger.info(f"Exported alerts: {len(df)} records")
        return filepath
    
    def export_salesforce_registry(self, registry_data: List[Dict]) -> str:
        """
        Export Salesforce model registry
        
        Args:
            registry_data: List of model registration records
            
        Returns:
            Path to exported CSV file
        """
        records = []
        
        for model_data in registry_data:
            record = {
                'salesforce_model_id': model_data['salesforce_model_id'],
                'model_name': model_data['model_name'],
                'dataset': model_data['dataset'],
                'accuracy': model_data['performance_metrics']['accuracy'],
                'precision': model_data['performance_metrics']['precision'],
                'recall': model_data['performance_metrics']['recall'],
                'f1_score': model_data['performance_metrics']['f1_score'],
                'roc_auc': model_data['performance_metrics']['roc_auc'],
                'demographic_parity_diff': model_data['fairness_metrics']['demographic_parity_difference'],
                'equal_opportunity_diff': model_data['fairness_metrics']['equal_opportunity_difference'],
                'equalized_odds_diff': model_data['fairness_metrics']['equalized_odds_difference'],
                'disparate_impact_ratio': model_data['fairness_metrics']['disparate_impact_ratio'],
                'compliance_score': model_data['compliance_status']['compliance_score'],
                'compliant': model_data['compliance_status']['compliant'],
                'deployment_status': model_data['deployment_status'],
                'registration_date': model_data['registration_timestamp']
            }
            records.append(record)
        
        df = pd.DataFrame(records)
        filepath = os.path.join(self.export_dir, 'salesforce_registry.csv')
        df.to_csv(filepath, index=False)
        
        logger.info(f"Exported salesforce_registry: {len(df)} records")
        return filepath
    
    def get_export_manifest(self) -> Dict:
        """Get manifest of all exported files"""
        files = os.listdir(self.export_dir)
        manifest = {
            'export_directory': self.export_dir,
            'files': [],
            'total_files': len(files)
        }
        
        for filename in files:
            filepath = os.path.join(self.export_dir, filename)
            file_info = {
                'filename': filename,
                'filepath': filepath,
                'size_bytes': os.path.getsize(filepath)
            }
            manifest['files'].append(file_info)
        
        return manifest