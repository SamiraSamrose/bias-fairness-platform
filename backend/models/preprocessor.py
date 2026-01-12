import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class DataPreprocessor:
    """Preprocesses datasets for model training"""
    
    @staticmethod
    def preprocess_compas(df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess COMPAS dataset"""
        if df is None:
            return None
        
        df_clean = df.copy()
        
        relevant_cols = ['age', 'sex', 'race', 'juv_fel_count', 'juv_misd_count',
                        'priors_count', 'c_charge_degree', 'is_recid', 'decile_score']
        df_clean = df_clean[relevant_cols].copy()
        df_clean = df_clean.dropna()
        
        df_clean['sex_encoded'] = (df_clean['sex'] == 'Male').astype(int)
        df_clean['race_encoded'] = LabelEncoder().fit_transform(df_clean['race'])
        df_clean['charge_encoded'] = (df_clean['c_charge_degree'] == 'F').astype(int)
        df_clean['is_african_american'] = (df_clean['race'] == 'African-American').astype(int)
        df_clean['is_caucasian'] = (df_clean['race'] == 'Caucasian').astype(int)
        
        logger.info(f"COMPAS preprocessed: {len(df_clean)} records")
        return df_clean
    
    @staticmethod
    def preprocess_loan(df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess loan dataset"""
        if df is None:
            return None
        
        df_clean = df.copy()
        
        df_clean['Gender'].fillna(df_clean['Gender'].mode()[0], inplace=True)
        df_clean['Married'].fillna(df_clean['Married'].mode()[0], inplace=True)
        df_clean['Dependents'].fillna(df_clean['Dependents'].mode()[0], inplace=True)
        df_clean['Self_Employed'].fillna(df_clean['Self_Employed'].mode()[0], inplace=True)
        df_clean['LoanAmount'].fillna(df_clean['LoanAmount'].median(), inplace=True)
        df_clean['Loan_Amount_Term'].fillna(df_clean['Loan_Amount_Term'].mode()[0], inplace=True)
        df_clean['Credit_History'].fillna(df_clean['Credit_History'].mode()[0], inplace=True)
        
        df_clean['Gender_encoded'] = (df_clean['Gender'] == 'Male').astype(int)
        df_clean['Married_encoded'] = (df_clean['Married'] == 'Yes').astype(int)
        df_clean['Education_encoded'] = (df_clean['Education'] == 'Graduate').astype(int)
        df_clean['Self_Employed_encoded'] = (df_clean['Self_Employed'] == 'Yes').astype(int)
        df_clean['Property_Area_encoded'] = LabelEncoder().fit_transform(df_clean['Property_Area'])
        df_clean['Loan_Status_encoded'] = (df_clean['Loan_Status'] == 'Y').astype(int)
        
        df_clean['Dependents'] = df_clean['Dependents'].replace('3+', '3')
        df_clean['Dependents_encoded'] = df_clean['Dependents'].astype(float)
        
        logger.info(f"Loan preprocessed: {len(df_clean)} records")
        return df_clean
    
    @staticmethod
    def preprocess_census(df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess census dataset"""
        if df is None:
            return None
        
        df_clean = df.copy()
        df_clean = df_clean.replace('?', np.nan).dropna()
        
        df_clean['income_encoded'] = (df_clean['income'] == '>50K').astype(int)
        df_clean['sex_encoded'] = (df_clean['sex'] == 'Male').astype(int)
        df_clean['race_encoded'] = LabelEncoder().fit_transform(df_clean['race'])
        df_clean['workclass_encoded'] = LabelEncoder().fit_transform(df_clean['workclass'])
        df_clean['education_encoded'] = LabelEncoder().fit_transform(df_clean['education'])
        df_clean['marital_encoded'] = LabelEncoder().fit_transform(df_clean['marital-status'])
        df_clean['occupation_encoded'] = LabelEncoder().fit_transform(df_clean['occupation'])
        df_clean['relationship_encoded'] = LabelEncoder().fit_transform(df_clean['relationship'])
        df_clean['is_white'] = (df_clean['race'] == 'White').astype(int)
        df_clean['is_black'] = (df_clean['race'] == 'Black').astype(int)
        
        logger.info(f"Census preprocessed: {len(df_clean)} records")
        return df_clean
    
    @staticmethod
    def get_feature_target_split(df: pd.DataFrame, dataset_type: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Extract features and target variable for each dataset"""
        if dataset_type == 'compas':
            feature_cols = ['age', 'sex_encoded', 'race_encoded', 'juv_fel_count',
                          'juv_misd_count', 'priors_count', 'charge_encoded']
            target_col = 'is_recid'
        elif dataset_type == 'loan':
            feature_cols = ['Gender_encoded', 'Married_encoded', 'Dependents_encoded',
                          'Education_encoded', 'Self_Employed_encoded', 'ApplicantIncome',
                          'CoapplicantIncome', 'LoanAmount', 'Loan_Amount_Term',
                          'Credit_History', 'Property_Area_encoded']
            target_col = 'Loan_Status_encoded'
        elif dataset_type == 'census':
            feature_cols = ['age', 'workclass_encoded', 'education-num', 'marital_encoded',
                          'occupation_encoded', 'relationship_encoded', 'race_encoded',
                          'sex_encoded', 'capital-gain', 'capital-loss', 'hours-per-week']
            target_col = 'income_encoded'
        else:
            raise ValueError(f"Unknown dataset type: {dataset_type}")
        
        return df[feature_cols], df[target_col]