import json
import sys

def call(*args):
    """
    Simulate a subprocess with unnamed arguments
    :param args:
    :return: None
    """
    return sum(args)


def main(command_str):
    """
    Calls the subprocess with a json string
    :param command_str: json, with format "var": val
    :return: None
    """
    cmd = json.loads(command_str)
    print("Subprocess running with parameters ", cmd)
    args = [v for k, v in sorted(cmd.items())]
    print("Sum is", call(*args))

if __name__ == "__main__":
    command_str = sys.argv[1]
    main(command_str)