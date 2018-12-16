import gzip
import os
import json
import sys

if len(sys.argv) > 1 is not None:
    log_file = sys.argv[1]
else:
    log_file = sorted(list(filter(lambda r: r.endswith('gz') and r.startswith('2018'), os.listdir())))[-1]

with gzip.open(log_file, 'rb') as f:
    print(log_file)
    json_data = json.loads(f.read().decode("utf-8"))
    for i in json_data:
        print(i)