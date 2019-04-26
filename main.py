from flask import Flask, request, render_template, flash, redirect, url_for, jsonify, send_from_directory, send_file
from werkzeug import secure_filename
from src.main_convert import *
from src.utils import load_data
from var_settings import *
from threading import Thread


app = Flask(__name__)
var_settings.init_global_var()

@app.route('/')
def index():
    return render_template('hello.html')

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
        print('[PHASE-1] file uploaded successfully {}'.format(filesave_name))
        res= load_data(file_name,'uncleaned')
        res = res.to_html(max_rows=15, justify='left',classes=['table','table-striped'])
        return render_template('preview.html', data=res, procId=file_name,parent_link=var_settings.parent_link)
    else:
        return redirect(url_for('index'))

@app.route('/previewMap/<procId>', methods = ['GET', 'POST'])
def render_map(procId):
    df,dtMap, dt_type,protagonist,header_list = preprocess_data(procId)
    mapping = map_data(df,dt_type,protagonist,header_list)
    #protagonist = "nama sekolah"
    #dtMap = ['nama sekolah', 'kelurahan', 'kecamatan', 'kondisi lingkungan', 'nama sekolah', 'kelurahan', 'kecamatan', 'kondisi lingkungan', 'nama sekolah', 'kelurahan', 'kecamatan', 'kondisi lingkungan']
    #mapping = {'alamat': 'P6375', 'kelurahan': 'P131', 'kecamatan': 'P131', 'jumlah siswa': 'P2196', 'jumlah guru': 'P1128', 'telp sekolah': '', 'kondisi lingkungan': 'P1196', 'lokasi geografis': 'P625', 'nama sekolah': 'nama sekolah'}
    var_settings.protagonist_dict[procId]=protagonist
    var_settings.entityheader_dict[procId]=dtMap
    var_settings.mapping_dict[procId]=mapping
    
    #beautify mapping dict
    mapping_beautified = dict(mapping)
    mapping_beautified[protagonist]="Kolom Protagonis"
    for key,value in mapping_beautified.items():
        if len(value) < 1:
            mapping_beautified[key]="Padanan Tidak Ditemukan"
    sample_info = []
    for x in mapping:
        sample_info.append(str(df[x].iloc[0]))

    return render_template('preview-map.html', mapping = mapping_beautified, sample_info = sample_info, procId=procId,parent_link=var_settings.parent_link)

@app.route('/createQS/<procId>', methods = ['GET', 'POST'])
def render_qs(procId):
    namaFile=procId
    print(namaFile)
    Thread(target=create_qs,args=(procId,)).start()
    print("Thread Creation Succes")
    # df = load_data(namaFile,'processed')
    # literal_columns_label = [x for x in df.columns if x not in var_settings.entityheader_dict[procId]]
    # df_mapping = link_data(df,var_settings.protagonist_dict[procId],var_settings.entityheader_dict[procId],var_settings.mapping_dict[procId])
    # df_final = generate_qs(df_mapping,df,var_settings.protagonist_dict[procId],literal_columns_label,procId)
    # res_address='data/results/{}'.format(namaFile)
    # df_final.to_csv(res_address, index=False)
    # return render_template('check-result.html', data=df_final.to_html(max_rows=15,classes=['table','table-striped']), procId=procId, address=res_address,result_finished=True,parent_link=var_settings.parent_link)
    return redirect(url_for('check_result',procId = procId))

def create_qs(procId):
    print("anda di create_qs {}".format(procId))
    namaFile=procId
    df = load_data(namaFile,'processed')
    print("Process started for {}".format(procId))
    literal_columns_label = [x for x in df.columns if x not in var_settings.entityheader_dict[procId]]
    df_mapping = link_data(df,var_settings.protagonist_dict[procId],var_settings.entityheader_dict[procId],var_settings.mapping_dict[procId])
    df_final = generate_qs(df_mapping,df,var_settings.protagonist_dict[procId],literal_columns_label,procId)
    res_address='data/results/{}'.format(namaFile)
    df_final.to_csv(res_address, index=False)

@app.route('/check-result/<procId>', methods = ['GET'])
def check_result(procId):
    data=""
    namaFile=procId
    res_address='data/results/{}'.format(namaFile)
    namaFile=procId
    result_finished, data_df = check_result_finished(namaFile)
    if result_finished:
        data = data_df.to_html(max_rows=15,classes=['table','table-striped'])
        return render_template('check-result.html', data=data, procId=procId, address=res_address,result_finished=True,parent_link=var_settings.parent_link)
    else:
        return render_template('check-result.html', data=data, procId=procId, address=res_address,result_finished=False,parent_link=var_settings.parent_link)

@app.route('/download-result/<procId>', methods=['GET', 'POST'])
def download(procId):
    directory='data/results/'
    filename=procId
    return send_file(directory+filename, attachment_filename='qs_result.csv', mimetype='text/csv',as_attachment=True)

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug = True)
