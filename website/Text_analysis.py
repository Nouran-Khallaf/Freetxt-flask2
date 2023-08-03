from flask import render_template
from flask import Blueprint

TextAnalysis = Blueprint('textanalysis', __name__)


@TextAnalysis.route('/textanalysis', methods=['GET', 'POST'])
def Textanalysis():
    return render_template('Textanalysis.html')