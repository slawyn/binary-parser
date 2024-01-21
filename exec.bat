set OUT=Bootloader.out
set ELF=Bootloader.out
set MOD=Bootloader.mod
set HEX=Bootloader.hex

::python elf.py %OUT% %MOD% %HEX%
@REM python python/analyze.py %OUT% >out.txt
@REM python python/analyze.py %ELF% >elf.txt
@REM python python/analyze.py %MOD% >mod.txt
python python/analyze.py python/binaries/main >a.txt