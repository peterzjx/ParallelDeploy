import datetime
import itertools
import json
import os
import re
import sys
from pydblite import Base

def init_work_dir(pbs_id):
    command = """
#!/bin/bash
if [ -z {}  ]
then
  echo "ID number missing"
else
  qstat -f {}|awk '
/^[ 	]*$/ {{ next }}
NR > 1 && /=/ {{ print last; sub(/[ 	]*$/,"");  last = $0 }}
NR > 1 && !/=/ {{ sub(/[ 	]*/,""); last = last $0}}
END {{ print last }}
' |grep -e 'init_work_dir'|sed 's/init_work_dir = //g'|tr -d '[:space:]'
fi
""".format(pbs_id,pbs_id)
    return str(os.popen(command).read())
def list_queue():
    command = """
qstat -u tuz38|sed '1,/^--/d'
"""
    return str(os.popen(command).read()).splitlines()

def new_repo(db_path):
    all_items=list_queue()
    pbs_id=[]
    for line in all_items:
        pbs_id.append(str(re.search(r'\d+',line).group()))

    job_db=Base(os.path.join(db_path,'PBS_job_database.pdl'))
    job_db.create('PBS_id', 'uniq_id', 'work_dir')

    for ele in pbs_id:
        ele_dir=init_work_dir(ele)
        ele_id=re.findall(r'\d+', ele_dir)[-1]
        job_db.insert(PBS_id=ele, work_dir=ele_dir, uniq_id=ele_id)
    job_db.commit()
    return job_db

def load_repo(db_path):
    job_db=Base(os.path.join(db_path,'PBS_job_database.pdl'))
    if job_db.exists():
        job_db.open()
        print("PBS_database found. Loading...\n")
        
        all_items=list_queue()
        pbs_id=[]
        for line in all_items:
            pbs_id.append(str(re.search(r'\d+',line).group()))
        for ele in pbs_id:
            ele_dir=init_work_dir(ele)
            ele_id=re.findall(r'\d+', ele_dir)[-1]
            if len(job_db(PBS_id=ele))==0:
                job_db.insert(PBS_id=ele, work_dir=ele_dir, uniq_id=ele_id)
    else:
        job_db=new_repo(db_path)
    job_db.commit()

#new_repo('./')
load_repo('./')
