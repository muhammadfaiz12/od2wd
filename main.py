from flask import Flask, request, render_template, flash, redirect, url_for, jsonify, send_from_directory, send_file
from werkzeug import secure_filename
from src.main_convert import *
from src.utils import load_data
from src.main_utils import *
from var_settings import *
from threading import Thread


app = Flask(__name__)
var_settings.init_global_var()

@app.route('/')
def index():
    catalogue, catalogue_time = get_catalogue()
    print(catalogue)
    return render_template('hello.html', file_catalogue=zip(catalogue,catalogue_time))

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        if f.filename == '':
           flash('No selected file')
           return redirect(request.url)
        fix_name = check_file_name(f.filename)
        fix_name = secure_filename(fix_name)
        filesave_name = 'data/uncleaned/'+ fix_name
        f.save(filesave_name)
        file_name = fix_name
        print('[PHASE-1] file uploaded successfully {}'.format(filesave_name))
        res= load_data(file_name,'uncleaned')
        res = res.to_html(max_rows=15, justify='left',classes=['table','table-striped'])
        return render_template('preview.html', data=res, procId=file_name,parent_link=var_settings.parent_link)
    else:
        return redirect(url_for('index'))

@app.route('/previewMap/<procId>', methods = ['GET', 'POST'])
def render_map(procId):
    print("[PROC-{}--[Phase 2]]-- Rendering mapping".format(procId))
    df,dtMap, dt_type,protagonist,header_list = preprocess_data(procId)
    mapping, label = map_data(df,dt_type,protagonist,header_list)
    var_settings.protagonist_dict[procId]=protagonist
    var_settings.entityheader_dict[procId]=dtMap
    var_settings.mapping_dict[procId]=mapping
    print("[PROC-{}--[Phase 2]]-- Mapping Info , Protagonist : {} , mapping_dict : {}".format(procId, protagonist, str(mapping)))

    #beautify mapping dict to be sent to FE 
    mapping_beautified = dict(mapping)
    for key,value in mapping_beautified.items():
        if len(value) < 1:
            mapping_beautified[key]="Padanan Tidak Ditemukan"
        else :
            if key == protagonist:
                mapping_beautified[key]="[Protagonist]-{}-{}".format(mapping_beautified[key], label[key])
            elif key in label:
                mapping_beautified[key]="{}-{}".format(mapping_beautified[key], label[key])
    sample_info = []
    for x in mapping:
        sample_info.append(str(df[x].iloc[0]))
    var_settings.mappingbeautified_dict[procId]=mapping_beautified
    save_mapping_result(df, procId, mapping_beautified)
    return render_template('preview-map.html', mapping = mapping_beautified, sample_info = sample_info, procId=procId,parent_link=var_settings.parent_link)

@app.route('/createQS/<procId>', methods = ['GET', 'POST'])
def render_qs(procId):
    namaFile=procId
    Thread(target=create_qs,args=(procId,)).start()
    print("[PROC-{}--[Phase 3]]--Thread Creation Success".format(procId))
    return redirect(url_for('check_result',procId = procId))

def create_qs(procId):
    print("[PROC-{}--[Phase 3]]-- Process Started Creating QS".format(procId))
    namaFile=procId
    df = load_data(namaFile,'processed')
    literal_columns_label = [x for x in df.columns if x not in var_settings.entityheader_dict[procId]]
    df_mapping = link_data(df,var_settings.protagonist_dict[procId],var_settings.entityheader_dict[procId],var_settings.mapping_dict[procId])
    save_linking_result(pd.DataFrame(df_mapping), procId)
    df_final = generate_qs(df_mapping,df,var_settings.protagonist_dict[procId],literal_columns_label,procId)
    res_address='data/results/{}'.format(namaFile)
    print("[PROC-{}--[Phase 3]]-- Saving to {}".format(procId, res_address))
    df_final.to_csv(res_address, index=False)

@app.route('/check-result/<procId>', methods = ['GET'])
def check_result(procId):
    data=""
    namaFile=procId
    res_address='data/results/{}'.format(namaFile)
    namaFile=procId
    result_finished, data_df = check_result_finished(namaFile)
    print("[PROC-{}--[Phase 4]]-- Checking Result {}".format(procId, res_address))
    if result_finished:
        publish_url = get_publish_qs_url(procId)
        data = data_df.to_html(max_rows=15,classes=['table','table-striped'])
        return render_template('check-result.html', data=data, procId=procId, publish_url=publish_url, address=res_address,result_finished=True,parent_link=var_settings.parent_link)
    else:
        return render_template('check-result.html', data=data, procId=procId, address=res_address,result_finished=False,parent_link=var_settings.parent_link)

@app.route('/download-result/<procId>', methods=['GET', 'POST'])
def download(procId):
    directory='data/results/'
    filename=procId
    return send_file(directory+filename, attachment_filename='qs_result.csv', mimetype='text/csv',as_attachment=True)

@app.route('/job-detail/<procId>')
def job_detail(procId):
    publish_url = ''
    job_status = get_job_status(procId)
    mapping = {}
    if procId in var_settings.mappingbeautified_dict:
        mapping = var_settings.mappingbeautified_dict[procId]
    elif job_status[2] :
        mapping = get_label_from_map_file(procId)
    if job_status[4]:
        publish_url = get_publish_qs_url(procId)
    return render_template('job-detail.html', procId=procId, job_status=job_status, publish_url=publish_url, mapping=mapping)

@app.route('/download-detail/<procId>/<phase>', methods=['GET', 'POST'])
def download_detail(procId, phase):
    directory='data/{}/'.format(phase)
    filename=procId
    return send_file(directory+filename, attachment_filename='qs_result.csv', mimetype='text/csv',as_attachment=True)

@app.route('/background-run/<procId>', methods = ['GET', 'POST'])
def background_run(procId):
    print("[PROC-{}--[Phase 2]]-- Rendering mapping".format(procId))
    df,dtMap, dt_type,protagonist,header_list = preprocess_data(procId)
    mapping, label = map_data(df,dt_type,protagonist,header_list)
    var_settings.protagonist_dict[procId]=protagonist
    var_settings.entityheader_dict[procId]=dtMap
    var_settings.mapping_dict[procId]=mapping
    print("[PROC-{}--[Phase 2]]-- Mapping Info , Protagonist : {} , mapping_dict : {}".format(procId, protagonist, str(mapping)))

    #beautify mapping dict to be sent to FE 
    mapping_beautified = dict(mapping)
    for key,value in mapping_beautified.items():
        if len(value) < 1:
            mapping_beautified[key]="Padanan Tidak Ditemukan"
        else :
            if key == protagonist:
                mapping_beautified[key]="[Protagonist]-{}-{}".format(mapping_beautified[key], label[key])
            elif key in label:
                mapping_beautified[key]="{}-{}".format(mapping_beautified[key], label[key])
    sample_info = []
    for x in mapping:
        sample_info.append(str(df[x].iloc[0]))
    var_settings.mappingbeautified_dict[procId]=mapping_beautified
    save_mapping_result(df, procId, mapping_beautified)
    return render_qs(procId)

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug = True)
