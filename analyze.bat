@echo off
python python/analyze.py -p -i  binaries/main32.exe  > logs/main32exe.log
python python/analyze.py -p -i  binaries/main64.exe > logs/main64exe.log
python python/analyze.py -p -i  binaries/main32 -o binaries/main32a > logs/main32.log
python python/analyze.py -p -i  binaries/main64 -o binaries/main64a > logs/main64.log
python python/analyze.py -p -i  binaries/delayimport.exe> logs/Project.log
python python/analyze.py -p -i  binaries/twain_32.dll> logs/twain32.log

:: changed
python python/analyze.py -p -i  binaries/main32a > logs/main32a.log
python python/analyze.py -p -i  binaries/main64a > logs/main64a.log