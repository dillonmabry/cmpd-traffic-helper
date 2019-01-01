"""
Module for ML Model types and wrapper for operations
Included: XGBoost, RandomForest (ensemble)
"""
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import Imputer, OneHotEncoder
from xgboost.sklearn import XGBClassifier
from sklearn.model_selection import GridSearchCV

class XGModel(object):
    """
    XGBoost wrapper class 
    https://xgboost.readthedocs.io/en/latest/python/python_api.html
    """
    def __init__(self):
        """
        Setup default XGBClassifier
        """
        self.model = XGBClassifier()

    def train(self, X, y):
        """
        Args:
            X: features set of observations to train
            y: train labels
        """
        pipeline = Pipeline([
            ('scaler', StandardScaler()), # Standardization for continuous features
            ('clf', self.model) # Classifier
        ])
        pipeline.fit(X, y) 
        params = {
            'clf__max_depth': [1, 5, 10, 15],
            'clf__learning_rate': [0.001, 0.01, 0.1],
            'clf__n_estimators': [10, 100, 1000],
            'clf__min_child_weight': [1, 5, 10],
            'clf__colsample_bytree': [0.8],
            'clf__colsample_bylevel': [0.8]
        }
        gridsearch = GridSearchCV(
            estimator=pipeline, 
            param_grid=params, 
            scoring='neg_mean_squared_error', 
            cv=10
        )
        gridsearch.fit(X, y)
        return gridsearch

    def train_and_update(self, train_data, labels):
        """
        Args:
            train_data: train_data with appropriate features processed
            labels: train set labels
        """
        self.model = self.train(train_data, labels)

    def predict(self, observations):
        """
        Args:
            observations: list of observations with appropriate features processed
        Returns list of tuples -> observations tagged with prediction 0 vs. 1
        """
        predictions = self.model.predict(observations)
        return list(zip(observations, predictions))

class RFModel(object):
    """
    RandomForest wrapper class 
    https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
    """
    def __init__(self, model):
        """
        Setup default RandomForestClassifier
        """
        self.model = None