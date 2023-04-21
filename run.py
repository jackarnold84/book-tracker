import read.reader as reader
import build.builder as builder
import sys

# read args
args = [a.lower() for a in sys.argv]
try:
    action = args[1]
    assert action in ['read', 'build']
    params = args[2:]
except:
    print('error: invalid arguments')
    print('  run.py read              # read and process new data')
    print('  run.py read <book1>      # read and process new data from book1 only')
    print('  run.py build             # rebuild html page')
    exit(1)


if action == 'read':
    reader.read(books=params)

if action == 'build':
    records = reader.get()
    builder.build(records)
