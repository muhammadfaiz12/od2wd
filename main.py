from flask import Flask, request, render_template, flash, redirect, url_for, jsonify, send_from_directory, send_file
from flask_paginate import Pagination, get_page_args
from werkzeug import secure_filename
from src.main_convert import *
from src.utils import load_data
from src.main_utils import *
from var_settings import *
from migrate import migrate
from threading import Thread
import time



app = Flask(__name__)
app.secret_key="super secret key"
var_settings.init_global_var()

@app.route('/')
def index():
    query = request.args.get('query')
    sort = request.args.get('sort')
    catalogue, catalogue_time = get_catalogue(query)
    if sort=="DESC":
        catalogue, catalogue_time = sorted(catalogue, reverse=True), sorted(catalogue_time, reverse=True)
    page, per_page, offset = get_page_args()
    ori_catalogue_len = len(catalogue)
    catalogue = split_paginate(catalogue, offset=offset, per_page=per_page)
    catalogue_time = split_paginate(catalogue_time, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=ori_catalogue_len,
                            css_framework='bootstrap4')
    return render_template('hello.html', file_catalogue=zip(catalogue,catalogue_time), page=page, per_page=per_page, pagination=pagination, parent_link=var_settings.parent_link)

@app.route('/about')
def about():
    return render_template('about.html', parent_link=var_settings.parent_link)

@app.route('/form-metadata', methods=['POST'])
def submit_form_metadata():
    req = request.form
    if 'job_id' not in req.keys():
        print("job id not found")
        return jsonify(error_message="job id not found")
    var_settings.job_metadata_dict[req['job_id']]=req
    print(str(var_settings.job_metadata_dict))
    return jsonify(message="ok")

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
        url_redirect="{}/".format(var_settings.parent_link)
        return redirect(url_redirect, code=302)

@app.route('/url-upload', methods = ['GET', 'POST'])
def integrated_file():
    url = request.form['url']
    try:
        file_name = fetch_csv_from_link(url.lower())
    except Exception as e:
        print("ERROR in FETCH FILE \n"+str(e))
        flash("Error occured, please ensure you insert the correct URL and try again")
        return redirect(url_for('index'))
    res= load_data(file_name,'uncleaned')
    res = res.to_html(max_rows=15, justify='left',classes=['table','table-striped'])
    return background_run(file_name, url)

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

def create_qs(procId, sourceURL:str):
    print("[PROC-{}--[Phase 3]]-- Process Started Creating QS".format(procId))
    namaFile=procId
    df = load_data(namaFile,'processed')
    literal_columns_label = [x for x in df.columns if x not in var_settings.entityheader_dict[procId]]
    df_mapping = link_data(df,var_settings.protagonist_dict[procId],var_settings.entityheader_dict[procId],var_settings.mapping_dict[procId])
    save_linking_result(pd.DataFrame(df_mapping), procId)
    df_final = generate_qs(df_mapping,df,var_settings.protagonist_dict[procId],literal_columns_label,procId, sourceURL)
    res_address='data/results/{}'.format(namaFile)
    print("[PROC-{}--[Phase 3]]-- Saving to {}".format(procId, res_address))
    df_final.to_csv(res_address, index=False)
    migrate(procId)


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

@app.route('/download-paper', methods=['GET'])
def download_publication():
    filename='publication/od2wd_paper.pdf'
    return send_file(filename, attachment_filename='OD2WD_paper.pdf', mimetype='application/pdf',as_attachment=True)

@app.route('/job-detail/<procId>')
def job_detail(procId):
    publish_url = ''
    job_status = get_job_status(procId)
    mapping = {}
    #if procId in var_settings.mappingbeautified_dict:
    #    mapping = var_settings.mappingbeautified_dict[procId]
    if job_status[3] :
        mapping = get_label_from_map_file(procId)
    if job_status[5]:
        publish_url = get_publish_qs_url(procId)
    #preview are html string, unless phase 2(zero based), it will be just string
    previews = []
    idx = 0
    states = ['uncleaned', 'processed', 'metadataExtraction', 'mapped', 'linked', 'results']
    for status in job_status:
        if states[idx] == 'metadataExtraction':
            res = "protagonist: nama sd"
            continue
        res= load_data(procId,states[idx])
        res = res.to_html(max_rows=15, justify='left').replace("border=\"1\"","'border=\"0\"'").replace("\"","")
        idx+=1
        previews.append(res)

    return render_template('job-detail.html', procId=procId, job_status=job_status, publish_url=publish_url, mapping=mapping, dataPreviews=previews)

@app.route('/download-detail/<procId>/<phase>', methods=['GET', 'POST'])
def download_detail(procId, phase):
    directory='data/{}/'.format(phase)
    filename=procId
    return send_file(directory+filename, attachment_filename='{}-{}.csv'.format(procId, phase), mimetype='text/csv',as_attachment=True)

def background_run_thread(procId, sourceURL):
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
    create_qs(procId, sourceURL)

@app.route('/background-run/<procId>', methods = ['GET', 'POST'])
def background_run(procId, sourceURL=""):
    Thread(target=background_run_thread,args=(procId,sourceURL,)).start()
    print("[PROC-{}--[Phase 3]]--Thread Creation Success".format(procId))
    time.sleep(1)
    url_redirect="{}/job-detail/{}".format(var_settings.parent_link, procId)
    return redirect(url_redirect, code=302)

@app.route('/choose-column/<procId>', methods = ['POST'])
def choose_column_handler(procId):
    dropCol = request.form.getlist('dropCol')
    drop_export_column(procId, dropCol)
    url_redirect="{}/job-detail/{}".format(var_settings.parent_link, procId)
    return redirect(url_redirect, code=302)


if __name__ == '__main__':
    app.run(debug = True)
