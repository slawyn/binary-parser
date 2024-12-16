#include <stdio.h>
#include <stdint.h>
#include "test.h"

typedef struct
{
   uint8_t inner_member;
} structure_t;

structure_t public_str;


// DELAYED_IMPORT
// cl t.cpp user32.lib delayimp.lib  /link /DELAYLOAD:user32.dll
// #include <windows.h>
// // uncomment these lines to remove .libs from command line
//  #pragma comment(lib, "delayimp")
//  #pragma comment(lib, "user32")


void main()
{
   structure_t str;
   printf("Hello");
   test_function();

    #ifdef DELAYED_IMPORT
   // user32.dll will load at this point
   MessageBox(NULL, L"Hello", L"Hello", MB_OK);
    #endif
}
