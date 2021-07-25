import catboost as cb
import os 
import pickle 

def get_lookup_values():
    # load lookup_dict  
    infile = open('data.pkl','rb')
    lookup_dict = pickle.load(infile)
    infile.close()
    return lookup_dict

def load_model():
    # load cat boost model from file or throw an error 
    files = os.listdir("./")
    for file_name in files: 
        if "cat_boost_model" in file_name:
            model = cb.CatBoostRegressor(loss_function='RMSE')
            model.load_model(file_name, format='cbm')
            return model 
    exit(1)

def get_price(feature_vector):
    model = load_model()
    price  = model.predict(feature_vector)
    return price 

def validate_input(lookup_dict, input_name, input_val):
    incorrect_input = True 
    if input_val in lookup_dict[input_name]:
        incorrect_input = False 
    return incorrect_input

