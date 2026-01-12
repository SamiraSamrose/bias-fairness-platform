import requests
import json
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AlertService:
    """Manages fairness alerts and Slack notifications"""
    
    def __init__(self, webhook_url: str, thresholds: Dict):
        self.webhook_url = webhook_url
        self.thresholds = thresholds
        self.alerts = []
    
    def check_fairness_metrics(self, model_name: str, dataset_name: str,
                               metrics: Dict, version_id: str) -> List[Dict]:
        """Check metrics against thresholds and generate alerts"""
        alerts_triggered = []
        
        if abs(metrics.get('demographic_parity_diff', 0)) > self.thresholds['demographic_parity_diff']:
            alert = self._create_alert(
                'HIGH', 'DEMOGRAPHIC_PARITY_VIOLATION',
                model_name, dataset_name, version_id,
                metrics['demographic_parity_diff'],
                self.thresholds['demographic_parity_diff'],
                f"Demographic parity violation detected for {model_name} on {dataset_name}"
            )
            alerts_triggered.append(alert)
        
        if abs(metrics.get('equal_opportunity_diff', 0)) > self.thresholds['equal_opportunity_diff']:
            alert = self._create_alert(
                'HIGH', 'EQUAL_OPPORTUNITY_VIOLATION',
                model_name, dataset_name, version_id,
                metrics['equal_opportunity_diff'],
                self.thresholds['equal_opportunity_diff'],
                f"Equal opportunity violation detected for {model_name} on {dataset_name}"
            )
            alerts_triggered.append(alert)
        
        dir_value = metrics.get('disparate_impact_ratio', 1)
        if dir_value < self.thresholds['disparate_impact_ratio_min'] or \
           dir_value > self.thresholds['disparate_impact_ratio_max']:
            alert = self._create_alert(
                'CRITICAL', 'DISPARATE_IMPACT_VIOLATION',
                model_name, dataset_name, version_id,
                dir_value,
                f"{self.thresholds['disparate_impact_ratio_min']}-{self.thresholds['disparate_impact_ratio_max']}",
                f"Disparate impact violation detected for {model_name} on {dataset_name}"
            )
            alerts_triggered.append(alert)
        
        self.alerts.extend(alerts_triggered)
        
        for alert in alerts_triggered:
            self.send_slack_alert(alert)
        
        return alerts_triggered
    
    def _create_alert(self, severity: str, alert_type: str, model: str,
                     dataset: str, version_id: str, metric_value: float,
                     threshold, message: str) -> Dict:
        """Create alert dictionary"""
        return {
            'timestamp': datetime.now().isoformat(),
            'severity': severity,
            'alert_type': alert_type,
            'model': model,
            'dataset': dataset,
            'version_id': version_id,
            'metric_value': metric_value,
            'threshold': threshold,
            'message': message
        }
    
    def send_slack_alert(self, alert: Dict) -> bool:
        """Send alert to Slack webhook"""
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False
        
        slack_message = self._format_slack_message(alert)
        
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(slack_message),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            logger.info(f"Slack alert sent: {alert['alert_type']}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False
    
    def _format_slack_message(self, alert: Dict) -> Dict:
        """Format alert as Slack Block Kit message"""
        severity_emoji = {
            'LOW': ':information_source:',
            'MEDIUM': ':warning:',
            'HIGH': ':red_circle:',
            'CRITICAL': ':rotating_light:'
        }
        
        return {
            'text': f"{severity_emoji.get(alert['severity'], ':bell:')} Fairness Alert",
            'blocks': [
                {
                    'type': 'header',
                    'text': {
                        'type': 'plain_text',
                        'text': f"{alert['alert_type']} - {alert['severity']}"
                    }
                },
                {
                    'type': 'section',
                    'fields': [
                        {'type': 'mrkdwn', 'text': f"*Model:*\n{alert['model']}"},
                        {'type': 'mrkdwn', 'text': f"*Dataset:*\n{alert['dataset']}"},
                        {'type': 'mrkdwn', 'text': f"*Version:*\n{alert['version_id']}"},
                        {'type': 'mrkdwn', 'text': f"*Timestamp:*\n{alert['timestamp']}"}
                    ]
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': alert['message']
                    }
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f"*Metric Value:* {alert['metric_value']:.4f}\n*Threshold:* {alert['threshold']}"
                    }
                }
            ]
        }
    
    def get_all_alerts(self) -> List[Dict]:
        """Get all generated alerts"""
        return self.alerts