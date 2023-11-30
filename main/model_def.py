from sklearn.linear_model import LinearRegression,RANSACRegressor, HuberRegressor, TheilSenRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.neighbors import KNeighborsRegressor
#from xgboost import XGBRegressor
from sklearn.svm import SVR

class DataAxis:
    axes = []
    def __init__(self, label, original, test, train):
        self.label = label
        self.original = original
        self.test = test
        self.train = train
        DataAxis.axes.append(self)

global x
x = DataAxis("",[],[],[])
global y
y = DataAxis("",[],[],[])

class ML_Model:
    models = []
    def __init__(self, name, model, category, r2=0, mse=0, rmse=0, mae=0, ypred=[]):
        self.name = name
        self.model = model
        self.category = category
        self.rmse = rmse
        self.mae = mae
        self.r2 = r2
        self.mse = mse
        self.ypred = ypred
        ML_Model.models.append(self)

    def get_results(self):
        return {
            "R2 Score": self.r2,
            "MAE": self.mae,
            "MSE":self.mse,
            "RMSE": self.rmse,
            "Y-Pred": self.ypred
        }
    
    def get_error_metrics(models):
        error_metrics = {
            'Model': [],
            'R2 Score': [],
            'MAE': [],
            'MSE': [],
            'RMSE': []
        }
    
        for model in models:
            model_result = model.get_results()
            error_metrics['Model'].append(model.name)
            error_metrics['R2 Score'].append(model_result["R2 Score"])
            error_metrics['MAE'].append(model_result["MAE"])
            error_metrics['MSE'].append(model_result["MSE"])
            error_metrics['RMSE'].append(model_result["RMSE"])
        
        return error_metrics

    def get_model_names():
        return [model.name for model in ML_Model.models]

lr = ML_Model("Linear Regression", LinearRegression(), "Linear")
ransac = ML_Model("RANSAC Regression", RANSACRegressor(), "Linear")
huber = ML_Model("Huber Regression", HuberRegressor(), "Linear")
tsr = ML_Model("Theil-Sen Regression", TheilSenRegressor(), "Linear")
dtr = ML_Model("Decision Tree", DecisionTreeRegressor(), "Tree")
rfr = ML_Model("Random Forest", RandomForestRegressor(), "Ensemble")
ada = ML_Model("AdaBoost", AdaBoostRegressor(), "Ensemble")
gdboost = ML_Model("Gradient Boost", GradientBoostingRegressor(), "Ensemble")
#xgboost = ML_Model("XGBoost", XGBRegressor(), "Ensemble")
knn = ML_Model("KNeighbors", KNeighborsRegressor(), "Neighbor")
svm = ML_Model("Support Vector Machine", SVR(), "SVM")

class Reagent:
    reagents = []
    def __init__(self, name, min_hue, max_hue):
        self.name = name
        self.min_hue = min_hue
        self.max_hue = max_hue
        Reagent.reagents.append(self)
    def get_reagent(name:str):
        for reagent in Reagent.reagents:
            if reagent.name.lower().strip() == name.lower():
                return reagent
            
luminol = Reagent("Luminol", 110, 130)
ruthenium = Reagent("Ruthenium", 0,20)