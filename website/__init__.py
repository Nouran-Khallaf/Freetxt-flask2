from flask import Flask
from flask_cors import CORS
from flask import Flask, session
from flask_session import Session
import os
from datetime import timedelta




BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Get the current app directory

def create_app(debug=True):
   
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'Uploaded')

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SESSION_TYPE'] = 'filesystem'  
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'myapp_'
    app.config['SESSION_FILE_DIR'] = UPLOAD_FOLDER
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=120)  # set session to expire in 120 minutes
    Session(app)
    CORS(app)
    from .Home import Home
    app.register_blueprint(Home, url_prefix = '/')
    
    from .Home import ContactUs
    app.register_blueprint(ContactUs)
    

    from .Home import Userguide
    app.register_blueprint(Userguide)

    from .Text_analysis import TextAnalysis
    app.register_blueprint(TextAnalysis)

    from .File_analysis import FileAnalysis
    app.register_blueprint(FileAnalysis)
    return app