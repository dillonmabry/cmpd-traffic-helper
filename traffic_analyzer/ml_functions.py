"""
Util module for custom ML pipeline functions for feature extraction
"""
import numpy as np


class ColumnExtractor(object):
    """
    Class to extract columns based on selected and transform
    """

    def __init__(self, cols):
        """
        Args:
            cols: the columns to select for extraction in pipeline
        """
        self.cols = cols

    def transform(self, X):
        """
        Args:
            X: the featureset to concatenate to
        """
        col_list = []
        for c in self.cols:
            col_list.append(X[:, c:c+1])
        return np.concatenate(col_list, axis=1)

    def fit(self, X, y=None):
        return self
