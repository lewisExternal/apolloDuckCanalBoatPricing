from flask import Flask, render_template, request, jsonify
from api import get_price, get_lookup_values, validate_input

server = Flask(__name__)

@server.route("/")
@server.route("/help")
def help():
   return render_template('help.html', title='PRICE MY BOAT')

@server.route("/v1/api")
def api():
   
   # get look up values of categorical variables 
   lookup_dict = get_lookup_values()

   if 'length' in request.args:
      length = int(request.args['length'])
   else:
      return "Error, parameter 'length' is required."
   
   if 'berths' in request.args:
      berths = int(request.args['berths'])
   else:
      return "Error, parameter 'berths' is required."
   
   if 'age' in request.args:
      age = int(request.args['age'])
   else:
      return "Error, parameter 'age' is required."   
   
   if 'model' in request.args:
      model = request.args['model']
      if validate_input(lookup_dict,'Model',model):
         return 'Incorrect input, please try the following: ' + ', '.join(lookup_dict['Model'])
   else:
      return "Error, parameter 'model' is required."   

   if 'toilet' in request.args:
      Toilet = request.args['toilet']
      if validate_input(lookup_dict,'Toilet',Toilet):
         return 'Incorrect input, please try the following: ' + ', '.join(lookup_dict['Toilet'])
   else:
      return "Error, parameter 'Toilet' is required."   

   # set default values s
   dealer = 'Error' # no dealer
   project = False  # not a project boat 
   adLength = 1431 # sample median 
   location = 'London' # assume sold from london
   
   result_dict = {'dealer':dealer, 'length':length, 'berths':berths, 'Model':model, 'age': age, 'Project':project, 'Toilet':Toilet, 'adLength':adLength,'location':location}
   result_dict['price'] = get_price([dealer, length, berths, model, age, project, Toilet, adLength, location])

   return jsonify(result_dict)



if __name__ == "__main__":
   server.run(host='0.0.0.0',debug=True)
   #server.run()