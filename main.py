from flask import Flask, request, render_template, flash, redirect, url_for
from werkzeug import secure_filename
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
        f.save('data/'+secure_filename(f.filename))
        flash('file uploaded successfully')
        return redirect(request.url)
    else:
        return redirect(url_for('index'))
    

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug = True)