from flask import render_template
from flask import Blueprint

Home = Blueprint('home', __name__)
Userguide = Blueprint('userguide', __name__)
ContactUs = Blueprint('contactus', __name__)

@Home.route('/', methods=['GET', 'POST'])
def home():
    return render_template('Home.html')

@ContactUs.route('/contactus')
def contactus():
    return render_template('ContactUs.html')

@Userguide.route('/userguide')
def userguide():
    return render_template('User-Guide.html')