import json
import sys
import os
import errno
import datetime
import itertools

def tz_date():
    now=datetime.datetime.now()
    return now.strftime("%Y%m%d")
    
def pbs_parse(item_table, value_table, job_id, store_dir):
    j_config=dict(zip(item_table, value_table))
    file_name=j_config['System_Type']+'_Ne'+str(j_config['Ne'])+'_ran'+str(j_config['Random_Seed'])+"_"+tz_date()+"_LLM_"+str(j_config['LL_Mixing'])+"_id"+str(job_id)
    j_config['Job_Dependent_File']=store_dir+file_name+'.dpt'
    with open(store_dir+file_name+'_conf.json', 'w') as output:
        json.dump(j_config, output)
    return file_name

def write_single_PBS(pbs_info, jconf_filename, c_output_name):
    storage_dir=pbs_info['Storage_Dir']
    work_dir=pbs_info['Work_Dir']
    if not os.path.exists(os.path.dirname(work_dir)):
        try:
            os.makedirs(os.path.dirname(work_dir))
        except OSError as exc:
            if exc.errno!=errno.EEXIST:
                raise
    if not os.path.exists(os.path.dirname(storage_dir)):
        try:
            os.makedirs(os.path.dirname(storage_dir))
        except OSError as exc:
            if exc.errno!=errno.EEXIST:
                raise
    with open(pbs_info['Storage_Dir']+jconf_filename+'.pbs','w') as PBS_conf:
        PBS_conf.write('#PBS -A '+pbs_info['Queue_Name']+'\n')
        PBS_conf.write('#PBS -l walltime='+pbs_info['Wall_Time']+'\n')
        PBS_conf.write('#PBS -l nodes=1:ppn=1\n')
        PBS_conf.write('#PBS -j oe\n')
        PBS_conf.write('#PBS -me -M tuz38@psu.edu\n')
        PBS_conf.write('cd '+pbs_info['Work_Dir']+'\n')
        PBS_conf.write('./'+pbs_info['Program_Name']+' '+jconf_filename+'_conf.json '+c_output_name+'\n')

def cprogram_config_generator(json_conf_file_name):
    with open(json_conf_file_name) as json_PBS_config:
        PBS_config=json.load(json_PBS_config)
    
        mcinfo_table=[]
        mcinfo_title=[]
        for i in PBS_config['Monte_Carlo']:
            mcinfo_title.append(i)
            mcinfo_table.append(PBS_config['Monte_Carlo'][i])
        mcinfo_table=list(map(list,itertools.product(*mcinfo_table)))
        #print(mcinfo_title)
        #print(mcinfo_table)
        for subtable in mcinfo_table:
            jconfig_file_name=pbs_parse(mcinfo_title,subtable, mcinfo_table.index(subtable), PBS_config['PBS']['Work_Dir'])
            write_single_PBS(PBS_config['PBS'], jconfig_file_name, jconfig_file_name+'_outfile')

cprogram_config_generator(sys.argv[1])
