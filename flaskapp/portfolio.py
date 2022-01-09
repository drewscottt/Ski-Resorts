'''

'''

from main import *

@app.route('/portfolio', methods=['GET'])
def portfolio():
    return render_template('portfolio.html')
