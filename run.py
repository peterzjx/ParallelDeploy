import json
import sys
import os

with open(sys.argv[1]) as f:
    param = json.load(f)
    args = [v for k, v in sorted(param.items())]
    print(sum(args))
    
with open(os.path.join(sys.argv[2], "output.txt"), 'w') as f:
    f.write("Output = " + str(sum(args)))
