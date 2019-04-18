from flask import Flask, request, render_template, flash, redirect, url_for, jsonify, send_from_directory, send_file
from werkzeug import secure_filename
from src.main_convert import *
from src.utils import load_data
from var_settings import *

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
        res = load_data(file_name,'uncleaned')
        res = res.to_html(max_rows=15)
        return render_template('preview.html', data=res, procId=file_name)
    else:
        return redirect(url_for('index'))

@app.route('/previewMap/<procId>', methods = ['GET', 'POST'])
def render_map(procId):
    df,dtMap, dt_type,protagonist,header_list = preprocess_data(procId)
    mapping = map_data(df,dt_type,protagonist,header_list)
    var_settings.protagonist_dict[procId]=protagonist
    var_settings.entityheader_dict[procId]=dtMap
    var_settings.mapping_dict[procId]=mapping
    return render_template('preview-map.html', mapping = mapping, procId=procId)

@app.route('/createQS/<procId>', methods = ['GET', 'POST'])
def render_qs(procId):
    namaFile=procId
    df = load_data(namaFile,'processed')
    literal_columns = [x for x in df.columns if x not in var_settings.entityheader_dict[procId]]
    df_mapping = link_data(df,var_settings.protagonist_dict[procId],var_settings.entityheader_dict[procId],var_settings.mapping_dict[procId])
    df_final = generate_qs(df_mapping,df,var_settings.protagonist_dict[procId],literal_columns)
    df_final.to_csv('data/results/{}'.format(namaFile))
    return render_template('check-result.html', data=df_final.to_html(max_rows=15), procId=procId)

@app.route('/check-result/<procId>', methods = ['GET'])
def check_result(procId):
    namaFile=procId
    result = check_result(namaFile)
    return jsonify(result)

@app.route('/download-result/<procId>', methods=['GET', 'POST'])
def download(procId):
    directory='data/results/'
    filename=procId
    return send_file(directory+filename, attachment_filename='qs_result.csv')

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug = True)