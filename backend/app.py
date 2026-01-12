import os
import sys
import logging
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
from datetime import datetime
import numpy as np

from config import Config
from models import DataLoader, DataPreprocessor, ModelTrainer, FairnessMetrics
from services import GovernanceService, AlertService, SalesforceService, TableauService
from utils import SemanticMetrics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
           template_folder='../frontend/templates',
           static_folder='../frontend/static')
app.config.from_object(Config)
CORS(app)

Config.init_directories()

data_loader = DataLoader(Config.RAW_DATA_DIR)
preprocessor = DataPreprocessor()
trainer = ModelTrainer()
governance = GovernanceService(Config.MODEL_REGISTRY_PATH, Config.AUDIT_LOG_PATH)
alert_service = AlertService(Config.SLACK_WEBHOOK_URL, Config.FAIRNESS_THRESHOLDS)
salesforce_service = SalesforceService(
    Config.SALESFORCE_USERNAME,
    Config.SALESFORCE_PASSWORD,
    Config.SALESFORCE_SECURITY_TOKEN,
    Config.SALESFORCE_DOMAIN
)
tableau_service = TableauService(Config.TABLEAU_EXPORT_DIR)

all_model_results = {}
all_fairness_results = {}
all_semantic_results = {}

@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('index.html')

@app.route('/fairness')
def fairness_dashboard():
    """Render fairness metrics dashboard"""
    return render_template('fairness_dashboard.html')

@app.route('/temporal')
def temporal_monitoring():
    """Render temporal monitoring dashboard"""
    return render_template('temporal_monitoring.html')

@app.route('/governance')
def governance_dashboard():
    """Render governance dashboard"""
    return render_template('governance.html')

@app.route('/alerts')
def alerts_dashboard():
    """Render alerts dashboard"""
    return render_template('alerts.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/datasets/load', methods=['POST'])
def load_datasets():
    """
    Load and preprocess all datasets
    
    Returns:
        JSON with dataset statistics
    """
    try:
        logger.info("Loading datasets...")
        
        compas_raw = data_loader.load_compas()
        loan_raw = data_loader.load_loan()
        census_raw = data_loader.load_census()
        
        compas_processed = preprocessor.preprocess_compas(compas_raw)
        loan_processed = preprocessor.preprocess_loan(loan_raw)
        census_processed = preprocessor.preprocess_census(census_raw)
        
        return jsonify({
            'status': 'success',
            'datasets': {
                'compas': {
                    'raw_records': len(compas_raw) if compas_raw is not None else 0,
                    'processed_records': len(compas_processed) if compas_processed is not None else 0
                },
                'loan': {
                    'raw_records': len(loan_raw) if loan_raw is not None else 0,
                    'processed_records': len(loan_processed) if loan_processed is not None else 0
                },
                'census': {
                    'raw_records': len(census_raw) if census_raw is not None else 0,
                    'processed_records': len(census_processed) if census_processed is not None else 0
                }
            }
        })
    
    except Exception as e:
        logger.error(f"Error loading datasets: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/models/train', methods=['POST'])
def train_models():
    """
    Train models on all datasets
    
    Returns:
        JSON with training results and fairness metrics
    """
    try:
        logger.info("Training models...")
        
        compas_raw = data_loader.load_compas()
        loan_raw = data_loader.load_loan()
        census_raw = data_loader.load_census()
        
        compas_processed = preprocessor.preprocess_compas(compas_raw)
        loan_processed = preprocessor.preprocess_loan(loan_raw)
        census_processed = preprocessor.preprocess_census(census_raw)
        
        results = {}
        
        for dataset_name, df, dataset_type, protected_attr in [
            ('compas', compas_processed, 'compas', 'is_african_american'),
            ('loan', loan_processed, 'loan', 'Gender_encoded'),
            ('census', census_processed, 'census', 'sex_encoded')
        ]:
            if df is None:
                continue
            
            X, y = preprocessor.get_feature_target_split(df, dataset_type)
            model_results = trainer.train_models(X, y)
            
            dataset_metrics = {}
            
            for model_name, result in model_results.items():
                X_test_indices = result['X_test'].index
                protected_values = df.loc[X_test_indices, protected_attr].values
                
                fairness_metrics = FairnessMetrics.compute_all_metrics(
                    result['y_test'].values,
                    result['y_pred'],
                    protected_values
                )
                
                performance_metrics = trainer.calculate_performance_metrics(
                    result['y_test'],
                    result['y_pred'],
                    result['y_pred_proba']
                )
                
                combined_metrics = {**performance_metrics, **fairness_metrics}
                dataset_metrics[model_name] = combined_metrics
                
                model_hash = str(hash(str(result['model'])))
                version_id = governance.register_model(
                    model_name, dataset_name, combined_metrics, model_hash
                )
                
                alerts = alert_service.check_fairness_metrics(
                    model_name, dataset_name, combined_metrics, version_id
                )
                
                sf_model_id = salesforce_service.register_model(
                    model_name, dataset_name, combined_metrics, version_id,
                    {'training_date': datetime.now().isoformat()}
                )
            
            results[dataset_name] = dataset_metrics
            all_model_results[dataset_name] = model_results
            all_fairness_results[dataset_name] = dataset_metrics
            
            bias_delta = SemanticMetrics.compute_bias_delta_score(dataset_metrics)
            stability = SemanticMetrics.compute_fairness_stability_index(dataset_metrics)
            
            all_semantic_results[dataset_name] = {
                'bias_delta': bias_delta,
                'stability': stability
            }
        
        tableau_service.export_performance_fairness(results)
        tableau_service.export_semantic_metrics(all_semantic_results)
        tableau_service.export_audit_log(governance.get_audit_log())
        tableau_service.export_alerts(alert_service.get_all_alerts())
        tableau_service.export_salesforce_registry(salesforce_service.export_registry())
        
        return jsonify({
            'status': 'success',
            'results': results,
            'semantic_metrics': all_semantic_results
        })
    
    except Exception as e:
        logger.error(f"Error training models: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/fairness/metrics')
def get_fairness_metrics():
    """
    Get all fairness metrics
    
    Returns:
        JSON with fairness metrics for all datasets and models
    """
    if not all_fairness_results:
        return jsonify({'status': 'error', 'message': 'No models trained yet'}), 404
    
    return jsonify({
        'status': 'success',
        'fairness_metrics': all_fairness_results
    })

@app.route('/api/semantic/metrics')
def get_semantic_metrics():
    """
    Get semantic metrics (Bias Delta Score, Fairness Stability Index)
    
    Returns:
        JSON with semantic metrics for all datasets
    """
    if not all_semantic_results:
        return jsonify({'status': 'error', 'message': 'No semantic metrics available'}), 404
    
    return jsonify({
        'status': 'success',
        'semantic_metrics': all_semantic_results
    })

@app.route('/api/governance/registry')
def get_model_registry():
    """
    Get complete model registry
    
    Returns:
        JSON with all registered models
    """
    return jsonify({
        'status': 'success',
        'registry': governance.model_registry
    })

@app.route('/api/governance/audit-log')
def get_audit_log():
    """
    Get complete audit log
    
    Returns:
        JSON with all audit entries
    """
    return jsonify({
        'status': 'success',
        'audit_log': governance.get_audit_log()
    })

@app.route('/api/governance/compliance')
def get_compliance_report():
    """
    Get compliance report
    
    Returns:
        JSON with compliance statistics
    """
    report = governance.get_compliance_report()
    return jsonify({
        'status': 'success',
        'compliance_report': report
    })

@app.route('/api/alerts')
def get_alerts():
    """
    Get all generated alerts
    
    Returns:
        JSON with all alerts
    """
    return jsonify({
        'status': 'success',
        'alerts': alert_service.get_all_alerts()
    })

@app.route('/api/salesforce/registry')
def get_salesforce_registry():
    """
    Get Salesforce model registry
    
    Returns:
        JSON with Salesforce registry data
    """
    return jsonify({
        'status': 'success',
        'salesforce_registry': salesforce_service.export_registry()
    })

@app.route('/api/salesforce/deploy/<model_id>', methods=['POST'])
def deploy_model(model_id):
    """
    Deploy model to production
    
    Args:
        model_id: Salesforce model ID
        
    Returns:
        JSON with deployment result
    """
    result = salesforce_service.deploy_model(model_id)
    
    if 'error' in result:
        return jsonify({'status': 'error', **result}), 400
    
    return jsonify({'status': 'success', 'deployment': result})

@app.route('/api/tableau/export')
def export_tableau_data():
    """
    Export all data for Tableau Cloud
    
    Returns:
        JSON with export manifest
    """
    try:
        manifest = tableau_service.get_export_manifest()
        return jsonify({
            'status': 'success',
            'manifest': manifest
        })
    except Exception as e:
        logger.error(f"Error exporting Tableau data: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/visualizations/fairness-comparison')
def get_fairness_comparison():
    """
    Get data for fairness metrics comparison visualization
    
    Returns:
        JSON with formatted data for Plotly visualization
    """
    if not all_fairness_results:
        return jsonify({'status': 'error', 'message': 'No data available'}), 404
    
    data = []
    
    for dataset_name, models in all_fairness_results.items():
        for model_name, metrics in models.items():
            data.append({
                'dataset': dataset_name,
                'model': model_name,
                'demographic_parity_diff': metrics['demographic_parity_diff'],
                'equal_opportunity_diff': metrics['equal_opportunity_diff'],
                'equalized_odds_diff': metrics['equalized_odds_diff'],
                'disparate_impact_ratio': metrics['disparate_impact_ratio']
            })
    
    return jsonify({
        'status': 'success',
        'data': data
    })

@app.route('/api/visualizations/performance-metrics')
def get_performance_metrics():
    """
    Get data for performance metrics visualization
    
    Returns:
        JSON with formatted data for Plotly visualization
    """
    if not all_fairness_results:
        return jsonify({'status': 'error', 'message': 'No data available'}), 404
    
    data = []
    
    for dataset_name, models in all_fairness_results.items():
        for model_name, metrics in models.items():
            data.append({
                'dataset': dataset_name,
                'model': model_name,
                'accuracy': metrics['accuracy'],
                'precision': metrics['precision'],
                'recall': metrics['recall'],
                'f1_score': metrics['f1_score'],
                'roc_auc': metrics['roc_auc']
            })
    
    return jsonify({
        'status': 'success',
        'data': data
    })

@app.route('/api/visualizations/bias-delta')
def get_bias_delta_visualization():
    """
    Get data for Bias Delta Score visualization
    
    Returns:
        JSON with formatted data for visualization
    """
    if not all_semantic_results:
        return jsonify({'status': 'error', 'message': 'No data available'}), 404
    
    data = []
    
    for dataset_name, metrics in all_semantic_results.items():
        data.append({
            'dataset': dataset_name,
            'mean_bias_delta': metrics['bias_delta']['mean_bias_delta'],
            'max_bias_delta': metrics['bias_delta']['max_bias_delta'],
            'min_bias_delta': metrics['bias_delta']['min_bias_delta']
        })
    
    return jsonify({
        'status': 'success',
        'data': data
    })

@app.route('/api/visualizations/stability-index')
def get_stability_index_visualization():
    """
    Get data for Fairness Stability Index visualization
    
    Returns:
        JSON with formatted data for visualization
    """
    if not all_semantic_results:
        return jsonify({'status': 'error', 'message': 'No data available'}), 404
    
    data = []
    
    for dataset_name, metrics in all_semantic_results.items():
        data.append({
            'dataset': dataset_name,
            'fairness_stability_index': metrics['stability']['fairness_stability_index'],
            'stability_category': metrics['stability']['stability_category']
        })
    
    return jsonify({
        'status': 'success',
        'data': data
    })

if __name__ == '__main__':
    logger