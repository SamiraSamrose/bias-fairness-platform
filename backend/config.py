import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_ENV', 'production') == 'development'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///fairness.db')
    
    # Salesforce Configuration
    SALESFORCE_CLIENT_ID = os.getenv('SALESFORCE_CLIENT_ID')
    SALESFORCE_CLIENT_SECRET = os.getenv('SALESFORCE_CLIENT_SECRET')
    SALESFORCE_USERNAME = os.getenv('SALESFORCE_USERNAME')
    SALESFORCE_PASSWORD = os.getenv('SALESFORCE_PASSWORD')
    SALESFORCE_SECURITY_TOKEN = os.getenv('SALESFORCE_SECURITY_TOKEN')
    SALESFORCE_DOMAIN = os.getenv('SALESFORCE_DOMAIN', 'login')
    
    # Slack Configuration
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
    SLACK_CHANNEL = os.getenv('SLACK_CHANNEL', '#fairness-alerts')
    
    # Tableau Configuration
    TABLEAU_SERVER_URL = os.getenv('TABLEAU_SERVER_URL')
    TABLEAU_SITE_ID = os.getenv('TABLEAU_SITE_ID', '')
    TABLEAU_USERNAME = os.getenv('TABLEAU_USERNAME')
    TABLEAU_PASSWORD = os.getenv('TABLEAU_PASSWORD')
    TABLEAU_API_VERSION = os.getenv('TABLEAU_API_VERSION', '3.19')
    
    # Data Configuration
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
    EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
    TABLEAU_EXPORT_DIR = os.path.join(EXPORT_DIR, 'tableau')
    
    # Fairness Thresholds
    FAIRNESS_THRESHOLDS = {
        'demographic_parity_diff': 0.1,
        'equal_opportunity_diff': 0.1,
        'equalized_odds_diff': 0.1,
        'disparate_impact_ratio_min': 0.8,
        'disparate_impact_ratio_max': 1.25,
        'bias_delta_score': 0.15,
        'accuracy_drop': 0.05
    }
    
    # Model Configuration
    MODEL_REGISTRY_PATH = os.path.join(PROCESSED_DATA_DIR, 'model_registry.json')
    AUDIT_LOG_PATH = os.path.join(PROCESSED_DATA_DIR, 'audit_log.json')
    
    # Create directories if they don't exist
    @staticmethod
    def init_directories():
        """Initialize required directories"""
        directories = [
            Config.DATA_DIR,
            Config.RAW_DATA_DIR,
            Config.PROCESSED_DATA_DIR,
            Config.EXPORT_DIR,
            Config.TABLEAU_EXPORT_DIR
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)