def init_global_var():
    global protagonist_dict
    global entityheader_dict
    global mapping_dict
    global parent_link
    global mappingbeautified_dict
    global parent_api_link
    global job_metadata_dict
    protagonist_dict={}
    entityheader_dict={}
    mapping_dict={}
    mappingbeautified_dict={}
    # Job_metdata_dict [jobId:str -> {key:str -> value:str}]
    job_metadata_dict={}
    #Production
    parent_link="http://od2wd.id"
    parent_api_link="http://localhost:8080/"
    #Local
    # parent_link="http://localhost:5000"
    # parent_api_link="https://od2wd.id/api/"