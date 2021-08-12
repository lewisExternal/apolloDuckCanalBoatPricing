#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.chrome.options import Options
import os
import sys
import shutil
#from webdriver_manager.chrome import ChromeDriverManager
import numpy as np 
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import sqlite3
import re
import catboost as cb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.inspection import permutation_importance
import docker 
from datetime import datetime
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import shap 

# import scripts 
from docker_lib import create_and_run_docker

sys.path.append('../scraping/')
import db_lib
sys.path.append('../utils/')
from utils import get_time_stamp, get_file_name_time_stamp

# functions
def pre_cleanse(df):

    # remove errors 
    df_pre_cleansed = df[(df['status']!='Error') & (df['desc']!='Error') & (df['specs']!='Error')]
    print( get_time_stamp() + ' - INFO - pre cleanse records: '+ str(df_pre_cleansed.shape[0]))
    return df_pre_cleansed

def create_features(df_cleansed):

    # create features 
    df_cleansed['length'] = (df_cleansed['specs'].str.extract("[length]*([0-9][0-9])[']", expand=False).str.strip())
    df_cleansed['constructed'] = (df_cleansed['specs'].str.extract("[Constructed]*([0-9][0-9][0-9][0-9])", expand=False).str.strip())
    df_cleansed['berths'] = (df_cleansed['specs'].str.extract("[Berths: ]([0-9])[\n]", expand=False).str.strip())
    df_cleansed['val'] =   df_cleansed['price'].apply(lambda x: int(re.sub('\D', '', x)) if re.sub('\D', '', x) != '' else int(0))

    #df_cleansed['Model'] = (df_cleansed['specs'].str.extract("[Model]*[:]*([a-zA-Z].*[a-zA-Z])[ ]", expand=False).str.strip())

    df_cleansed['Model'] = df_cleansed.apply(calculate_model, axis=1)
    df_cleansed['Project'] = df_cleansed.apply(calculate_project, axis=1)
    df_cleansed['Toilet'] = df_cleansed.apply(calculate_toilet, axis=1)
    df_cleansed['adLength'] = df_cleansed.apply(calculate_advert_length, axis=1)

    return df_cleansed

def calculate_model(row):
    search = row['specs'].lower() + row['desc'].lower() + row['title'].lower()
    if 'semi' in search and 'trad'in search:
        model = 'semitrad'
    elif 'trad ' in search:
        model = 'trad'
    elif 'traditional' in search:
        model = 'trad'
    elif 'cruiser' in search:
        model = 'cruiser'
    elif 'wide' in search and 'beam' in search:
        model = 'widebeam'
    elif 'eurocruiser' in search:
        model = 'eurocruiser'
    elif 'dutch' in search and 'barge' in search:
        model = 'dutchbarge'
    elif 'tug ' in search:
        model = 'tug'
    else:
        model = 'none'
        
    return model 

def calculate_project(row):
    search = row['specs'].lower() + row['desc'].lower() + row['title'].lower()
    if ' project ' in search:
        project = True
    else:
        project = False
    return project 

def calculate_toilet(row):
    search = row['specs'].lower() + row['desc'].lower() + row['title'].lower()    
    if 'macerator' in search:
        toilet = 'macerator'
    elif 'pump out' in search or 'pump-out' in search:
        toilet = 'pumpout'
    elif 'compost' in search:
        toilet = 'compost'
    elif 'cassette' in search:
        toilet = 'cassette'
    elif 'sealand' in search:
        toilet = 'sealand'
    else:
        toilet = 'none'
    return toilet
   
def calculate_advert_length(row):
    search = row['specs'].lower() + row['desc'].lower() + row['title'].lower()
    # remove whitespace 
    search = search.replace(' ','')
    length = len(search)
    return int(length) 

def construct_final_dataset(df_cleansed):

    # drop null values 
    df_final = df_cleansed.dropna()

    # remove zero price values 
    df_final = df_final[df_final['val']!=0]
    
    # calculate year diff remove outliers 
    now = datetime.now()
    year  = int(now.year)
    df_final['year_diff'] = df_final['constructed'].apply(lambda x: year-int(x))
    df_final = df_final[(df_final['year_diff']<200)]
    df_final = df_final[(df_final['year_diff']>=0)]
    print( get_time_stamp() + ' - INFO - df final records: '+ str(df_final.shape[0]))

    return df_final

def fit_cat_boost_model(df_final):
    # split target and features 
    cols = ['dealer', 'length', 'berths', 'Model', 'year_diff', 'Project', 'Toilet', 'adLength','location']
    X = df_final[cols]
    y = df_final['val']
    
    # train test split 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=42)
    
    # assign dataset 
    categorical_features_indices = [0,3,5,6,8]
    train_dataset = cb.Pool(X_train, y_train, cat_features=categorical_features_indices) 
    test_dataset = cb.Pool(X_test, y_test, cat_features=categorical_features_indices)
    
    # define model 
    model = cb.CatBoostRegressor(loss_function='RMSE')
    
    # train model 
    print( get_time_stamp() + ' - INFO - model training')
    grid = {'iterations': [100, 150, 200],
        'learning_rate': [0.03, 0.1],
        'depth': [2, 4, 6, 8],
        'l2_leaf_reg': [0.2, 0.5, 1, 3]}
    model.grid_search(grid, train_dataset)
    print( get_time_stamp() + ' - INFO - model has been trained')

    # calculate error 
    pred = model.predict(X_test)
    rmse = (np.sqrt(mean_squared_error(y_test, pred)))
    r2 = r2_score(y_test, pred)
    
    print("Testing model performance")
    print(get_time_stamp() + ' RMSE: {:.2f}'.format(rmse))
    print(get_time_stamp() + ' R2: {:.2f}'.format(r2))

    # shap analysis 
    shap_values = shap.TreeExplainer(model).shap_values(X_train)
    f1 = shap.summary_plot(shap_values, X_train, plot_type="bar",show=False)
    plt.savefig("summary_plot.png")
    plt.clf()
    explainer = shap.TreeExplainer(model)
    shap_obj = explainer(X_train)
    shap.plots.beeswarm(shap_obj,show=False)
    plt.savefig("beeswarm.png")
    plt.clf()
    
    #for col in cols:
    #    shap.dependence_plot(col, shap_values, X_train)

    # save the model to file 
    save_model(model,train_dataset)

    return model 

def save_model(model,train_dataset):
    
    # archive old models 
    archive_model()
    
    # save model to flask app 
    fname = "./flask/" + get_file_name_time_stamp() + "cat_boost_model"
    model.save_model(fname,
           format="cbm",
           export_parameters=None,
           pool=train_dataset)


def archive_model():

    # archive old model if it exists 
    # os.chdir('./flask')
    #old_models = glob.glob("./flask/*cat_boost_model", recursive = True)
    files = os.listdir("./flask/")
    
    # move file 
    for file_name in files:
        if "cat_boost_model" in file_name:
            shutil.move("./flask/"+ file_name, './'+file_name)
            print( get_time_stamp() + ' - INFO - file has been moved: ' + file_name)

def visualise_data(df,df_pre_cleansed,df_cleansed,df_final): 
    #  data loss due to cleansing 
    print( get_time_stamp() +  ' - df # of records - '+ str(df.shape[0]))
    print( get_time_stamp() + ' - df_pre_cleansed # of records - '+ str(df_pre_cleansed.shape[0]))
    print( get_time_stamp() + ' - df_cleansed # of records - '+ str(df_cleansed.shape[0]))
    print( get_time_stamp() + ' - df_final # of records - '+ str(df_final.shape[0]))

    # categorical data 
    cat_col = ['dealer',  'berths', 'Model',  'Project', 'Toilet', 'location']

    # numerical data 
    num_col = ['length','year_diff','adLength']

    # for categorical data 
    lookup_dict = {}

    print("Processing categorical variables. ")
    for col in cat_col:
        lookup_dict = plot_cat_feature(col,df_final,lookup_dict)

    # save categorical data 
    save_lookup(lookup_dict)
    
    print("Processing numerical variables. ")
    for col in num_col:
        plot_num_feature(col,df_final)

def plot_cat_feature(col_name,df_final,lookup_dict):
    print('#################################################')
    print(get_time_stamp() + ' - INFO - processing ' + col_name)
    agg_df = df_final.groupby(col_name).count()
    dff = agg_df['id'].sort_values(ascending=False)
    print(dff)
    print('#################################################')
    lookup_dict = add_lookup_value(dff,col_name,lookup_dict)
    return lookup_dict

def plot_num_feature(col_name,df_final):
    print('#################################################')
    print(get_time_stamp() + ' - INFO - processing ' + col_name)
    print(get_time_stamp() + ' - INFO - max value is: ' + str(df_final[col_name].max()))
    print(get_time_stamp() + ' - INFO - min value is: ' + str(df_final[col_name].min()))  
    print(get_time_stamp() + ' - INFO - mean value is: ' + str(df_final[col_name].mean()))
    print(get_time_stamp() + ' - INFO - median value is: ' + str(df_final[col_name].median()))
    sns.scatterplot(data=df_final.sort_values(by=col_name), x=col_name, y="val")
    plt.savefig(col_name+".png")
    plt.clf()
    print('#################################################')

def add_lookup_value(dff,col_name,lookup_dict):
    vals = set(dff.index.values)
    lookup_dict[col_name] = vals
    return lookup_dict

def save_lookup(lookup_dict):
    lookup_file = open("./flask/data.pkl", "wb")
    pickle.dump(lookup_dict, lookup_file)
    lookup_file.close()

def main():

    # start of model script 
    print( get_time_stamp() + ' - INFO - createModel script has started')
   
    # get boat data from the DB
    database = r"../pythonsqlite.db"

    # get connection to db 
    conn = db_lib.create_connection(database)
    print("Connection to the DB established.")

    # create df of boat data 
    df = pd.read_sql_query("SELECT * from boats", conn)
    print( get_time_stamp() + ' - INFO - raw boat records: '+ str(df.shape[0]))

    # remove errors 
    df_pre_cleansed = pre_cleanse(df)
    
    # create features 
    df_cleansed = create_features(df_pre_cleansed)

    # construct final data set for training 
    df_final = construct_final_dataset(df_cleansed)
    
    #sns.scatterplot(data=df_final, x="year_diff", y="val", hue="Model")
    #plt.show()  

    # fit the model 
    model = fit_cat_boost_model(df_final)

    # visualise
    visualise_data(df,df_pre_cleansed,df_cleansed,df_final)  

    # create docker image 
    create_and_run_docker()

    # end of model script 
    print( get_time_stamp() + ' - INFO - createModel script has finished')

if __name__ == "__main__":
    main()
