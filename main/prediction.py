import joblib
import os
from processing import makeExcel
import numpy as np
from util import open_window

def load(path):
    loaded_models = {}
    def load_model(model_path):
        loaded_model = joblib.load(model_path)
        loaded_model_path = os.path.splitext(os.path.split(model_path)[1])[0]
        loaded_models[loaded_model_path] = loaded_model
    if path.endswith(".pkl"):
        load_model(path)
    elif path.endswith(".xlsx"):
        parentPath = os.path.join(os.path.splitext(path)[0], "models")
        for model_file in os.listdir(parentPath):
            path = os.path.join(parentPath, model_file)
            load_model(path)
    return loaded_models

def predict_value(x_val, loaded_models):
    predictions = {}
    label_text = ""
    for loaded_model_name, predict_model in loaded_models.items():
        predictions[predict_model]  = round(predict_model.model.predict(np.array([x_val]).reshape(-1,1))[0], 3)
        label_text += f"{predict_model.name} ({predict_model.category}) -> {predictions[predict_model]}\n"
        
    return predictions, label_text

def download_predictions(x_val, predictions, parentPath):
    print("checking")
    if parentPath.endswith(".xlsx"):
        print("ends with xlsx")
        parentPath = os.path.join(os.path.splitext(parentPath)[0], "predictions")
    elif parentPath.endswith(".pkl"):
        parentPath = os.path.join(os.path.split(os.path.split(parentPath)[0])[0], "predictions")
    print(parentPath)
    os.makedirs(parentPath) if not os.path.exists(parentPath) else None
    filename = f"prediction_({(len(os.listdir(parentPath)))}).xlsx"
    path = os.path.join(parentPath, filename)    
    print(path)
    preds = {
        "Model":["X-Val"],
        "Category":["-"],
        "Prediction":[x_val]
    }
    for model, prediction in predictions.items():
        preds["Model"].append(model.name)
        preds["Category"].append(model.category)
        preds["Prediction"].append(prediction)
    makeExcel(path, preds, sortby="Category")
    open_window(os.path.split(path)[0])
