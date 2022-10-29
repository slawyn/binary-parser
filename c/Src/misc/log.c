#include <stdio.h>
#include <stdlib.h>
#include <windows.h>

#include "types.h"
#include "misc/log.h"

/*****************************************************************************
 * @param format string with placeholders
 * @param ... variable arguments
 * @return        0: OK
 *                x: Error
 ******************************************************************************/
int32_t i32Log(const char *format, ...)
{
   va_list vl;
   va_start(vl, format);
   int32_t    i32Status;
   SYSTEMTIME xSystemTime;

   GetSystemTime(&xSystemTime);
   printf("%02hu:%02hu:%02hu:%03hu:: ", xSystemTime.wHour, xSystemTime.wMinute, xSystemTime.wSecond, xSystemTime.wMilliseconds);

   i32Status = vprintf(format, vl);
   printf("\n");
   va_end(vl);
   return(i32Status);
}
