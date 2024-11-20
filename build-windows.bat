set PATH=C:\msys64\mingw32\bin\;%PATH%
gcc.exe tests\main.c tests\test.c -m32 -o binaries\main32.exe

set PATH=C:\msys64\ucrt64\bin;%PATH%
gcc.exe tests\main.c tests\test.c -o binaries\main64.exe