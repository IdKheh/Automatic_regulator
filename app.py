from flask import Flask, render_template, abort
from controller import *

import plotly.express as px
import pandas as pd


app = Flask(__name__)

conn = ":)" # database connection

@app.route('/')
def index():
    params = {
        'kp': 0.5,
        'Ti': 2,
        'c_zadane': 40,
        'Tp': 0.1,
        't_sym': 1800
    }
    return render_template('index.html', params=params)


@app.route('/<FUNCTION>')
def execCommand(FUNCTION = None):
    fun = str(FUNCTION).lstrip('/').split('(')[0]
    
    if fun != 'start':
        abort(404)
    
    exec(FUNCTION.replace("<br>", "\n"))
    return ""


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def start(kp: float, Ti: float, c_zadane: int, Tp: float, t_sym: int):
    classic = ClassicPI(conn, kp, Ti, Tp, t_sym, c_zadane/100)
    classic.calculate()
    classic.savePlot()
    
    fuzzy = FuzzyPI(conn, Tp, t_sym, c_zadane/100)
    fuzzy.calculate()
    fuzzy.savePlot()
    return ""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)