from flask import render_template
from flask import Blueprint

FileAnalysis = Blueprint('fileanalysis', __name__)


@FileAnalysis.route('/fileanalysis', methods=['GET', 'POST'])
def Textanalysis():
    return render_template('Fileanalysis.html')