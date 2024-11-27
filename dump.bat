@echo off
readelf -x .init binaries/main32 > logs/main32.dump
readelf -x .text binaries/main32 >> logs/main32.dump
readelf -x .init binaries/main32 >> logs/main32.dump
readelf -x .plt binaries/main32 >> logs/main32.dump
readelf -x .rodata binaries/main32 >> logs/main32.dump
readelf -x .data binaries/main32 >> logs/main32.dump
readelf -x .bss binaries/main32 >> logs/main32.dump
readelf -x .init_array binaries/main32 >> logs/main32.dump
readelf -x .strtab binaries/main32 >> logs/main32.dump
readelf -x .shstrtab binaries/main32 >> logs/main32.dump



readelf -x .init binaries/main32a > logs/main32a.dump
readelf -x .text binaries/main32a >> logs/main32a.dump
readelf -x .init binaries/main32a >> logs/main32a.dump
readelf -x .plt binaries/main32a >> logs/main32a.dump
readelf -x .rodata binaries/main32a >> logs/main32a.dump
readelf -x .data binaries/main32a >> logs/main32a.dump
readelf -x .bss binaries/main32a >> logs/main32a.dump
readelf -x .init_array binaries/main32a >> logs/main32a.dump
readelf -x .strtab binaries/main32a >> logs/main32a.dump
readelf -x .shstrtab binaries/main32a >> logs/main32a.dump