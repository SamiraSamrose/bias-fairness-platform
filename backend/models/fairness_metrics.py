import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class FairnessMetrics:
    """Computes fairness metrics for binary classification"""
    
    @staticmethod
    def demographic_parity_difference(y_pred, protected_attribute):
        """
        Calculate demographic parity difference
        Range: [-1, 1], 0 = perfect parity
        """
        protected = y_pred[protected_attribute == 1]
        unprotected = y_pred[protected_attribute == 0]
        
        if len(protected) == 0 or len(unprotected) == 0:
            return 0.0
        
        return float(protected.mean() - unprotected.mean())
    
    @staticmethod
    def equal_opportunity_difference(y_true, y_pred, protected_attribute):
        """
        Calculate equal opportunity difference (TPR difference)
        Range: [-1, 1], 0 = perfect equality
        """
        protected_mask = protected_attribute == 1
        unprotected_mask = protected_attribute == 0
        
        tpr_protected = (
            np.sum((y_true[protected_mask] == 1) & (y_pred[protected_mask] == 1)) /
            np.sum(y_true[protected_mask] == 1)
            if np.sum(y_true[protected_mask] == 1) > 0 else 0
        )
        
        tpr_unprotected = (
            np.sum((y_true[unprotected_mask] == 1) & (y_pred[unprotected_mask] == 1)) /
            np.sum(y_true[unprotected_mask] == 1)
            if np.sum(y_true[unprotected_mask] == 1) > 0 else 0
        )
        
        return float(tpr_protected - tpr_unprotected)
    
    @staticmethod
    def equalized_odds_difference(y_true, y_pred, protected_attribute):
        """
        Calculate equalized odds difference
        Average of TPR and FPR differences
        """
        protected_mask = protected_attribute == 1
        unprotected_mask = protected_attribute == 0
        
        tpr_protected = (
            np.sum((y_true[protected_mask] == 1) & (y_pred[protected_mask] == 1)) /
            np.sum(y_true[protected_mask] == 1)
            if np.sum(y_true[protected_mask] == 1) > 0 else 0
        )
        
        tpr_unprotected = (
            np.sum((y_true[unprotected_mask] == 1) & (y_pred[unprotected_mask] == 1)) /
            np.sum(y_true[unprotected_mask] == 1)
            if np.sum(y_true[unprotected_mask] == 1) > 0 else 0
        )
        
        fpr_protected = (
            np.sum((y_true[protected_mask] == 0) & (y_pred[protected_mask] == 1)) /
            np.sum(y_true[protected_mask] == 0)
            if np.sum(y_true[protected_mask] == 0) > 0 else 0
        )
        
        fpr_unprotected = (
            np.sum((y_true[unprotected_mask] == 0) & (y_pred[unprotected_mask] == 1)) /
            np.sum(y_true[unprotected_mask] == 0)
            if np.sum(y_true[unprotected_mask] == 0) > 0 else 0
        )
        
        return float((abs(tpr_protected - tpr_unprotected) + abs(fpr_protected - fpr_unprotected)) / 2)
    
    @staticmethod
    def disparate_impact_ratio(y_pred, protected_attribute):
        """
        Calculate disparate impact ratio
        Range: [0, inf], 1 = perfect parity, [0.8, 1.25] = acceptable
        """
        protected = y_pred[protected_attribute == 1]
        unprotected = y_pred[protected_attribute == 0]
        
        if len(protected) == 0 or len(unprotected) == 0:
            return 1.0
        
        positive_rate_protected = protected.mean()
        positive_rate_unprotected = unprotected.mean()
        
        if positive_rate_unprotected == 0:
            return 0.0
        
        return float(positive_rate_protected / positive_rate_unprotected)
    
    @staticmethod
    def statistical_parity_difference(y_pred, protected_attribute):
        """
        Statistical parity difference (same as demographic parity)
        """
        return FairnessMetrics.demographic_parity_difference(y_pred, protected_attribute)
    
    @staticmethod
    def compute_all_metrics(y_true, y_pred, protected_attribute) -> Dict:
        """Compute all fairness metrics"""
        return {
            'demographic_parity_diff': FairnessMetrics.demographic_parity_difference(
                y_pred, protected_attribute
            ),
            'equal_opportunity_diff': FairnessMetrics.equal_opportunity_difference(
                y_true, y_pred, protected_attribute
            ),
            'equalized_odds_diff': FairnessMetrics.equalized_odds_difference(
                y_true, y_pred, protected_attribute
            ),
            'disparate_impact_ratio': FairnessMetrics.disparate_impact_ratio(
                y_pred, protected_attribute
            ),
            'statistical_parity_diff': FairnessMetrics.statistical_parity_difference(
                y_pred, protected_attribute
            )
        }