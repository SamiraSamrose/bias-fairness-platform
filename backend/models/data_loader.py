import os
import pandas as pd
import requests
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    """Handles loading of datasets from various sources"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def load_compas(self) -> Optional[pd.DataFrame]:
        """
        Load COMPAS recidivism dataset
        Source: ProPublica
        """
        filename = os.path.join(self.data_dir, 'compas.csv')
        
        if os.path.exists(filename):
            logger.info(f"Loading COMPAS from cache: {filename}")
            return pd.read_csv(filename)
        
        try:
            url = "https://raw.githubusercontent.com/propublica/compas-analysis/master/compas-scores-two-years.csv"
            logger.info(f"Downloading COMPAS from {url}")
            df = pd.read_csv(url)
            df.to_csv(filename, index=False)
            logger.info(f"COMPAS dataset cached: {len(df)} records")
            return df
        except Exception as e:
            logger.error(f"Failed to load COMPAS: {e}")
            return None
    
    def load_loan(self) -> Optional[pd.DataFrame]:
        """
        Load loan approval dataset
        Source: dphi-official
        """
        filename = os.path.join(self.data_dir, 'loan.csv')
        
        if os.path.exists(filename):
            logger.info(f"Loading Loan from cache: {filename}")
            return pd.read_csv(filename)
        
        try:
            url = "https://raw.githubusercontent.com/dphi-official/Datasets/master/Loan_Data/loan_train.csv"
            logger.info(f"Downloading Loan from {url}")
            df = pd.read_csv(url)
            df.to_csv(filename, index=False)
            logger.info(f"Loan dataset cached: {len(df)} records")
            return df
        except Exception as e:
            logger.error(f"Failed to load Loan: {e}")
            return None
    
    def load_census(self) -> Optional[pd.DataFrame]:
        """
        Load census income dataset
        Source: UCI Machine Learning Repository
        """
        filename = os.path.join(self.data_dir, 'census.csv')
        
        if os.path.exists(filename):
            logger.info(f"Loading Census from cache: {filename}")
            return pd.read_csv(filename)
        
        try:
            url = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"
            logger.info(f"Downloading Census from {url}")
            
            column_names = ['age', 'workclass', 'fnlwgt', 'education', 'education-num',
                          'marital-status', 'occupation', 'relationship', 'race', 'sex',
                          'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'income']
            
            df = pd.read_csv(url, names=column_names, skipinitialspace=True)
            df.to_csv(filename, index=False)
            logger.info(f"Census dataset cached: {len(df)} records")
            return df
        except Exception as e:
            logger.error(f"Failed to load Census: {e}")
            return None
    
    def load_all(self) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """Load all three datasets"""
        return self.load_compas(), self.load_loan(), self.load_census()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loader = DataLoader('../data/raw')
    compas, loan, census = loader.load_all()
    print(f"COMPAS: {len(compas) if compas is not None else 0} records")
    print(f"Loan: {len(loan) if loan is not None else 0} records")
    print(f"Census: {len(census) if census is not None else 0} records")