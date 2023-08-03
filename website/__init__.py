from flask import Flask
from flask_cors import CORS


def create_app(debug=True):
   
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
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