# binary-parser
Python parsers for ELF and PE formats

Required Tools:

Dependencies(Deps):
**Unity for Testing**
https://github.com/ThrowTheSwitch/Unity

**gcov for coverage Testing**
Part of Gcc

*GCC over MINGW*
https://www.mingw-w64.org/


How To build:

**Run Version**
make -f Windows.make FLAVOR=Run build

**Debug Version**
make -f Windows.make FLAVOR=Debug build

**Test Version**
make -f Windows.make FLAVOR=Test TEST_TARGET=<module-name> build test

e.g.
make -f Windows.make FLAVOR=Test TEST_TARGET=memory build test

