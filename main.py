from flask import Flask, request, render_template, flash, redirect, url_for
from werkzeug import secure_filename
from src.main_convert import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('hello.html')

@app.route('/hello/<user>')
def hello_name(user):
    return render_template('hello.html', name = user)

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        if f.filename == '':
           flash('No selected file')
           return redirect(request.url)
        filesave_name = 'data/'+secure_filename(f.filename)
        f.save(filesave_name)
        flash('file uploaded successfully')
        res, column = load_data(filesave_name)
        res = res.to_html(max_rows=15)
        return render_template('preview.html', data=res)
    else:
        return redirect(url_for('index'))

@app.route('/previewqs', methods = ['GET', 'POST'])
def render_map():
    pass

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug = True)