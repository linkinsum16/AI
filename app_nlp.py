import json
import os
import sys


from flasgger import Swagger
sys.path.append(str(os.getcwd()))
print(os.getcwd())
from flask import Flask, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from routes import  request_api9

app = Flask(__name__)
swagger = Swagger(app)
CORS(app)

app.config['TESTING'] = True
app.testing = True
### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swaggertest.yaml'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###

app.register_blueprint(request_api9.get_blueprint())

@app.route('/')
def index():

    return 'Flask is running!'

if __name__ == '__main__':
   host = os.environ.get('IP','0.0.0.0')
   port = int(os.environ.get('PORT', 5000))
   app.run(host=host,port=port)



