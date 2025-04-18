
from flask import render_template
from app import app




@app.route('/')
@app.route('/publicshare')
def index():
    return render_template("publicshare.html")
