import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class ModelTrainer:
    """Trains and manages ML models"""
    
    def __init__(self):
        self.models = {
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
        }
    
    def train_models(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        Train all models and return predictions
        
        Returns:
            Dictionary with model predictions and test data
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        results = {}
        
        for name, model in self.models.items():
            logger.info(f"Training {name}")
            model.fit(X_train_scaled, y_train)
            
            y_pred = model.predict(X_test_scaled)
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
            
            results[name] = {
                'model': model,
                'scaler': scaler,
                'y_test': y_test,
                'y_pred': y_pred,
                'y_pred_proba': y_pred_proba,
                'X_test': X_test,
                'X_test_scaled': X_test_scaled
            }
        
        logger.info(f"Trained {len(results)} models")
        return results
    
    @staticmethod
    def calculate_performance_metrics(y_true, y_pred, y_pred_proba) -> Dict:
        """Calculate classification performance metrics"""
        return {
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision': float(precision_score(y_true, y_pred, zero_division=0)),
            'recall': float(recall_score(y_true, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y_true, y_pred, zero_division=0)),
            'roc_auc': float(roc_auc_score(y_true, y_pred_proba))
        }