import numpy as np
import json
import subprocess

def extend(param_space, new_var, new_choice):
    """
    :param param_space: list of dicts, the previous space of all parameters
    :param new_var:
    :param new_choice: list of values, the current parameter space for new_var
    :return: same format as param_space
    """
    new_space = []
    for item in param_space:
        for value in new_choice:
            new_item = dict(item)
            new_item[new_var] = value
            new_space.append(new_item)
    return new_space

def parse(config_path):
    """
    :param config_path: path to the configuration file
    :return: a list of dicts, each is a combination of parameter set
    """
    with open(config_path) as config_file:
        config = json.load(config_file)
        task_name = config["task_name"]
        command = config["command"]
        assert("param" in config)
        param_space = [dict()]
        for var in config["param"]:
            choice = []
            varlist = config["param"][var]
            if type(varlist) is dict:
                if "linspace" in varlist:
                    lspace = varlist["linspace"]
                    assert(len(lspace) == 3)
                    choice = np.linspace(*lspace)
                elif "arange" in varlist:
                    arange = varlist["arange"]
                    choice = np.arange(*arange)
            else:
                if type(varlist) is list:
                    choice = varlist
                else:
                    choice = [varlist]
            param_space = extend(param_space, var, choice)
    return task_name, command, param_space

def call(command, param):
    theproc = subprocess.Popen([command, param], shell=True)
    theproc.communicate()

def main(config_path):
    task_name, command, param_space = parse(config_path)
    for choice in param_space:
        param = str(choice).replace('\'', '\"')
        call(command, param)

if __name__ == "__main__":
    # call("run.py", '{"var1":20, "var2":3}')
    main(config_path="experiment.json")