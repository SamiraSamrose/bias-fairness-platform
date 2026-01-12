import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class SemanticMetrics:
    """Computes semantic metrics for bias observability"""
    
    @staticmethod
    def compute_bias_delta_score(fairness_metrics_dict: Dict) -> Dict:
        """
        Bias Delta Score: Aggregate bias measurement
        Range: [0, 1], 0 = no bias
        
        Weighting:
        - DPD: 25%
        - EOD: 25%
        - EODD: 25%
        - DIR: 15%
        - SPD: 10%
        """
        scores = []
        
        for model, metrics in fairness_metrics_dict.items():
            dpd = abs(metrics['demographic_parity_diff'])
            eod = abs(metrics['equal_opportunity_diff'])
            eodd = abs(metrics['equalized_odds_diff'])
            dir_score = abs(1 - metrics['disparate_impact_ratio'])
            spd = abs(metrics['statistical_parity_diff'])
            
            bias_score = (dpd * 0.25 + eod * 0.25 + eodd * 0.25 + dir_score * 0.15 + spd * 0.10)
            scores.append(bias_score)
        
        return {
            'mean_bias_delta': float(np.mean(scores)),
            'max_bias_delta': float(np.max(scores)),
            'min_bias_delta': float(np.min(scores)),
            'std_bias_delta': float(np.std(scores)),
            'per_model_scores': {k: float(v) for k, v in zip(fairness_metrics_dict.keys(), scores)}
        }
    
    @staticmethod
    def compute_fairness_stability_index(fairness_metrics_dict: Dict) -> Dict:
        """
        Fairness Stability Index: Consistency measure
        Range: [0, 1], higher = more stable
        
        Uses coefficient of variation across models
        """
        all_metrics = []
        
        for model, metrics in fairness_metrics_dict.items():
            metric_vector = [
                abs(metrics['demographic_parity_diff']),
                abs(metrics['equal_opportunity_diff']),
                abs(metrics['equalized_odds_diff']),
                abs(1 - metrics['disparate_impact_ratio']),
                abs(metrics['statistical_parity_diff'])
            ]
            all_metrics.append(metric_vector)
        
        all_metrics = np.array(all_metrics)
        cv_scores = []
        
        for i in range(all_metrics.shape[1]):
            mean_val = np.mean(all_metrics[:, i])
            std_val = np.std(all_metrics[:, i])
            cv = std_val / mean_val if mean_val != 0 else 0
            cv_scores.append(cv)
        
        avg_cv = np.mean(cv_scores)
        stability_index = 1 / (1 + avg_cv)
        
        stability_category = 'High' if stability_index > 0.7 else 'Medium' if stability_index > 0.5 else 'Low'
        
        return {
            'fairness_stability_index': float(stability_index),
            'coefficient_of_variation': float(avg_cv),
            'per_metric_cv': [float(x) for x in cv_scores],
            'stability_category': stability_category
        }
    
    @staticmethod
    def compute_prediction_drift_score(predictions_dict: Dict, reference_model: str = 'Random Forest') -> Dict:
        """
        Prediction Drift Score: Inter-model prediction divergence
        """
        if reference_model not in predictions_dict:
            reference_model = list(predictions_dict.keys())[0]
        
        reference_preds = predictions_dict[reference_model]['y_pred']
        drift_scores = []
        
        for model_name, pred_data in predictions_dict.items():
            if model_name != reference_model:
                drift = float(np.mean(reference_preds != pred_data['y_pred']))
                drift_scores.append(drift)
        
        return {
            'mean_prediction_drift': float(np.mean(drift_scores)) if drift_scores else 0.0,
            'max_prediction_drift': float(np.max(drift_scores)) if drift_scores else 0.0,
            'reference_model': reference_model
        }