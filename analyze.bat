python python/analyze.py -p -i  binaries/main32.exe  > main32exe.log
python python/analyze.py -p -i  binaries/main64.exe > main64exe.log
python python/analyze.py -p -i  binaries/main32 -o binaries/main32a > main32.log
python python/analyze.py -p -i  binaries/main64 -o binaries/main64a > main64.log

:: changed
python python/analyze.py -p -i  binaries/main32a > main32a.log
python python/analyze.py -p -i  binaries/main64a > main64a.log