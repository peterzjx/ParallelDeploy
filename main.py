import datetime
import numpy as np
import itertools
import json
import os
import re
import sys

def timestamp():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def generate_param_space(vars):
    """
    :param vars: dict of {var: option}
    :return: a list of dicts, each is a combination of parameter set
    """
    values_list = []
    for var in vars:
        values = []
        value_option = vars[var]
        if type(value_option) is dict:
            if "linspace" in value_option:
                lspace = value_option["linspace"]
                assert(len(lspace) == 3)
                values = np.linspace(*lspace)
            elif "arange" in value_option:
                arange = value_option["arange"]
                values = np.arange(*arange)
            elif "Table" in value_option:
                arange = value_option["Table"]
                assert(len(arange) == 3)
                arange[1] += arange[2]
                values = np.arange(*arange)
        else:
            if type(value_option) is list:
                values = value_option
            else:
                values = [value_option]
        values_list.append(values)
    param_space = [dict(zip(vars, choice)) for choice in itertools.product(*values_list)]
    return param_space

def create_param_file(output_dir, unique_name, param):
    """
    Create the parameter json file from a single choice of param
    :param output_dir:
    :param unique_name:
    :param param: {var: val, var: val}
    :return:
    """
    directory = os.path.join(output_dir, unique_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    param_file = os.path.join(directory, "param.json")
    with open(param_file, 'w') as f:
        json.dump(param, f)
    return param_file

def submit(job_name, commands, work_dir, save_path, program, pbs, param_file):
    """
    Submit job to PBS system
    :param job_name: Task_name + id
    :param commands: Prerequisites before calling
    :param work_dir: path to the subprocess program file
    :param save_path: output file path, usually same as work_dir/task_name/unique_name
    :param program: command for the subprocess, e.g. "python run.py". Accepts parameters: params.json, output_path
    :param pbs: dict of PBS related params
    :param param_file: path to the param json
    :return:
    """
    queue_name = pbs["queue_name"]
    wall_time = pbs["wall_time"]
    command = """qsub - << EOJ
#!/bin/bash -l
#PBS -A {}
#PBS -N {}
#PBS -l nodes=1:ppn=1,mem=12gb
#PBS -l walltime={}
#PBS -j oe
#PBS -o stdout.o
{}
cd {}
{} {} {}
EOJ""".format(queue_name, job_name, wall_time, commands, work_dir, program, param_file, save_path)
    submit_message = os.popen(command).read()
    try:
        job_id = re.match('(\d+)\.torque', submit_message).group(1)
    except:
        job_id = ""
    return job_id

def main(config_path):
    with open(config_path) as config_file:
        config = json.load(config_file)
        assert ("param" in config)
        vars = config["param"]
        param_space = generate_param_space(vars)
        id_len = len(str(len(param_space)))
        task_name = config["task_name"]
        commands = "\n".join(config["commands"])
        program = config["program"]
        pbs = config["pbs"]
        work_dir = config["work_dir"]
        output_dir = os.path.join(work_dir, task_name)
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
        unique_name_prefix = timestamp()
        for i, param in enumerate(param_space):
            os.chdir("/")
            unique_name = unique_name_prefix + str(i).zfill(id_len)
            job_name = task_name + str(i).zfill(id_len)
            param_file = create_param_file(output_dir, unique_name, param)
            save_path = os.path.join(output_dir, unique_name)
            os.chdir(save_path)
            job_id = submit(job_name, commands, work_dir, save_path, program, pbs, param_file)
            print(job_id + " submitted")
            # delete param_file?

if __name__ == "__main__":
    # call("run.py", '{"var1":20, "var2":3}')
    main(config_path=sys.argv[1])
