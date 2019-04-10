from flask import Flask, request, render_template, flash, redirect, url_for
from werkzeug import secure_filename
from src.main_convert import *
from src.utils import load_data
import var_settings 

app = Flask(__name__)
init_global_var()

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
        filesave_name = 'data/uncleaned/'+secure_filename(f.filename)
        f.save(filesave_name)
        file_name = secure_filename(f.filename)
        print('file uploaded successfully {}'.format(filesave_name))
        res, column = load_data(file_name)
        res = res.to_html(max_rows=15)
        return render_template('preview.html', data=res, procId=file_name)
    else:
        return redirect(url_for('index'))

@app.route('/previewMap/<procId>', methods = ['GET', 'POST'])
def render_map(procId):
    df,dtMap, dt_type,protagonist,header_list = preprocess_data(procId)
    mapping = map_data(df,dt_type,protagonist,header_list)
    protagonist_dict[procId]=protagonist
    entityheader_dict[procId]=dtMap
    return render_template('preview-map.html', mapping = mapping, procId=procId)

@app.route('/createQS/<procId>', methods = ['GET', 'POST'])
def render_qs(procId):
    namaFile=procId
    df = load_data(namaFile,'processed')
    literal_columns = [x for x in df.columns if x not in entityheader_dict[procId]]
    df_mapping = link_data(df,protagonist_dict[procId],entityheader_dict[procId])
    df_final = generate_qs(df_mapping,df,protagonist_dict[procId],literal_columns)
    df_final.to_csv('data/results/{}'.format(namaFile))
    return render_template('preview-qs.html', mapping = mapping, procId=procId)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug = True)