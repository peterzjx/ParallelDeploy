import json
import re
import os
import errno
import datetime
import itertools
from pydblite import Base
class Job_info:
    Job_Name='None'
    PBS_ID='0'
    Job_Dir='./'
    Output_Dir='./'
    Status='None'

def Db_load(db_dir, db_name, conf_extension):
    tz_db=Base(db_name)
    start_dir=os.getcwd()
    os.chdir(db_dir)
    if tz_db.exists():
        print('Previous database found.\n')
        tz_db.open()
    else:
        tz_db.create('Job_Name', 'PBS_Name','PBS_ID','Job_Dir','Output_Dir','Status', mode='open')
    ls=os.popen('ls *'+conf_extension+'*').read()
    ls=re.sub('_conf.json','',ls)    
    ls=ls.splitlines()    
    for jobname in ls:
        tz_db.insert(Job_Name=jobname, PBS_Name=jobname+'.pbs', Job_Dir=db_dir)
    
    os.chdir(start_dir)
    tz_db.commit()
    return tz_db

def Pbs_submit(job_dir, job_name):
    start_dir=os.getcwd()
    os.chdir(job_dir)
    submit_message=os.popen('qsub '+job_name).read()
    matchstring=re.search('[-+]?\d+.torque',submit_message)

    os.chdir(start_dir)
    if(matchstring):
        match_id=re.search('[-+]?\d+',matchstring.group(0))
        return match_id.group(0)
    else:
        return None

def Submit_from_Db(Job_Dir, PBS_Dir, DB_Name):
    db=Db_load(Job_Dir, DB_Name ,'_conf.json')
    db.open()
    for job in db:
        print('Submiting New Job: '+job['Job_Name']+'\n')
        tmpid=Pbs_submit(PBS_Dir,job['PBS_Name'])
        job['PBS_ID']=tmpid
        job['Status']='Submitted'
    db.commit()
    for job in db:
        print(job)

Submit_from_Db('/storage/home/t/tuz38/work/Jobmanager/test/','/storage/home/t/tuz38/work/Jobmanager/test/Storage/','Coulomb_Job_Db')
