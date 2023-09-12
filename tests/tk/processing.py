import pandas as pd
import os
import matplotlib.pyplot as plt
import openpyxl
import numpy as np
from model_def import *
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def process_main(x,y,df, test_size, parentPath, models):
    y.original = df[y.label]
    if x.label in df.columns:
        x.original = df.drop([col for col in df.columns if col != x.label], axis=1)
    x.train, x.test, y.train, y.test = train_test_split(x.original.values,y.original.values, test_size=test_size, random_state=10)
    for model in models:
        try:
            model.model.fit(x.train, y.train)
        except Exception as e:
            print("Error at model.fit ", e)
        model.ypred = model.model.predict(x.test)
        model.r2 = r2_score(y.test, model.ypred)
        model.mse = mean_squared_error(y.test, model.ypred)
        model.mae = mean_absolute_error(y.test, model.ypred)
        model.rmse = np.sqrt(model.mse)
        modelsPath= os.path.join(parentPath, "models")
        if not os.path.exists(modelsPath):
            os.makedirs(modelsPath)
        modelPath = os.path.join(modelsPath, f"{model.name}.pkl")
        joblib.dump(model, modelPath)
    
    def errorMetricsSheet(parentPath):
        path = os.path.join(parentPath, 'error-metrics.xlsx')
        error_metrics = ML_Model.get_error_metrics(models)
        makeExcel(path, error_metrics)
        '''# Write the DataFrame to an Excel file
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
            worksheet = writer.sheets["Sheet 1"]
            for column_cells in worksheet.columns:
                length = max(len(str(cell.value)) for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2
            for row in worksheet.iter_rows():
                for cell in row:
                    cell.alignment = openpyxl.styles.Alignment(wrap_text=True)'''
    
    def putDataInCSV(parentPath):
        path = os.path.join(parentPath, 'xy-data.xlsx')
        y_preds = {
            f'{x.label}': x.test.flatten(),
            f'Original {y.label}': y.test.flatten()
        }
        for model in models:
            y_preds[model.name] = model.ypred.flatten()
    
        makeExcel(path, y_preds, f"Original {y.label}")

    def one_has_all(parentPath):
        models_num = len(models)
        plt.figure(figsize=((models_num*1.5)//1, (models_num*1.75)//1))
        for i, model in enumerate(models):
            if models_num % 3 ==0:
                row_div, cols, add = 3, 3, 0
            elif models_num%2 == 0:
                row_div, cols,add = 2,2, 0
            elif models_num%5 == 0:
                row_div, cols,add = 5,5, 0 
            else:
                row_div,cols,add = 3, 3, 1
            plt.subplot((models_num//row_div)+add, cols, i+1)
            plotSingleModel(model, parentPath)
        plt.savefig(os.path.join(parentPath, f'models.jpg'))
    
    def singlePlots(parentPath):
        for model in models:
            plotSingleModel(model, parentPath,save=True)
    
    def plotSingleModel(model,parentPath,save=False):
        if save:
            plt.figure(figsize=(10,10))
        plt.scatter(x.original,y.original, color="blue")
        plt.scatter(x.test, model.ypred, color="red")
        plt.legend(["Orginial", model.name])
        plt.title(f"{model.name} Technique")
        plt.xlabel(x.label)
        plt.ylabel(y.label)
        if save:
            save_name = model.name.strip().replace(" ", "_").strip().lower()
            save_path = os.path.join(parentPath, f"{save_name}.jpg")
            plt.savefig(save_path)
            plt.close()
    
    def all_in_one(parentPath):
        plt.figure(figsize=(10,10))
        plt.scatter(x.original,y.original, color="blue", label="Original")
        for color, model in zip(('red', 'green', 'black', 'magenta', 'orange', 'violet', 'brown', 'cyan', 'gray', 'khaki'),models):
            plt.scatter(x.test, model.ypred, color=color, label=model.name)
        plt.legend()
        plt.xlabel(x.label)
        plt.ylabel(y.label)
        plt.title(f"{x.label} vs {y.label}")
        plt.savefig(os.path.join(parentPath, f"total.jpg"))
    
    errorMetricsSheet(parentPath)
    putDataInCSV(parentPath)
    singlePlots(parentPath)
    plt.close()
    one_has_all(parentPath)
    plt.close()
    all_in_one(parentPath)
    plt.close()


def makeExcel(path, data, sortby = None):
    df = data if type(data) is pd.DataFrame else pd.DataFrame(data)

    # Sort the DataFrame in ascending order
    if sortby:
        df.sort_values(by=[sortby], inplace=True)

    # Write the DataFrame to an Excel file with auto-adjusted column widths and AutoFit text
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        worksheet = writer.sheets['Sheet1']
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2
        for row in worksheet.iter_rows():
            for cell in row:
                cell.alignment = openpyxl.styles.Alignment(wrap_text=True)