import pandas as pd
import sqlite3
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
import numpy as np

DB_FILE = "database/rank_predictor.db"

class RankPredictor:
    def __init__(self, degree=3):
        self.model = None
        self.degree = degree
        self._train_model()
    
    def _train_model(self):
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT Percentage, Rank FROM ranks", conn)
        conn.close()
        X = df["Percentage"].values.reshape(-1, 1)
        y = df["Rank"].values
        self.model = make_pipeline(PolynomialFeatures(self.degree), LinearRegression())
        self.model.fit(X, y)
    
    def predict_rank(self, percentage):
        pred = self.model.predict(np.array([[percentage]]))
        return max(1, int(round(pred[0])))

# Instantiate one global predictor to avoid retraining
predictor = RankPredictor()

def predict_rank(percentage):
    return predictor.predict_rank(percentage)
