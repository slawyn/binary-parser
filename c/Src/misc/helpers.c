#include <stdio.h>
#include <stdlib.h>
#include <windows.h>

#include "config.h"
#include "types.h"
#include "misc/memory.h"
#include "misc/helpers.h"
#include "misc/parsers.h"


/*****************************************************************************
 * @param format string with placeholders
 * @param ... variable arguments
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

/*****************************************************************************
 * @param cHex Hex character
 ******************************************************************************/
uint32_t ui32ConvertHexNibbleToUint(char cHex)
{
   uint32_t ui32Result;
   if (cHex >= '0' && cHex <= '9')
   {
      ui32Result = (cHex - 0x30);
   }
   else if (cHex >= 'A' && cHex <= 'F')
   {
      ui32Result = (cHex - 0x41) + 0x0A;
   }
   else
   {
      LogNormal("helpers::ui32ConvertHexNibbleToUint: Error: Unknown Hex %c", cHex);
      ui32Result = 0;
   }
   return(ui32Result);
}

/*****************************************************************************
 * @param sHexNibbles String of Nibbles
 ******************************************************************************/
uint8_t ui32ConvertHexStringToByte(char *sHexNibbles)
{
   uint8_t ui8Result = ((ui32ConvertHexNibbleToUint(sHexNibbles[0]) << 4) | ui32ConvertHexNibbleToUint(sHexNibbles[1]));
   return(ui8Result);
}

/*****************************************************************************
 * @param sHexNibbles String of Nibbles
 ******************************************************************************/
uint16_t ui32ConvertHexStringToWord(char *sHexNibbles)
{
   uint16_t ui16Result = (ui32ConvertHexStringToByte(&sHexNibbles[0]) << 8 | ui32ConvertHexStringToByte(&sHexNibbles[2]));
   return(ui16Result);
}

/*****************************************************************************
 * @param sHexNibbles String of Nibbles
 ******************************************************************************/
uint32_t ui32ConvertHexStringToDword(char *sHexNibbles)
{
   uint32_t ui32Result = (ui32ConvertHexStringToWord(&sHexNibbles[0]) << 16 | ui32ConvertHexStringToWord(&sHexNibbles[4]));
   return(ui32Result);
}

/*****************************************************************************
 * @param cHex Hex character
 ******************************************************************************/
void vConvertHexStringToByteBuffer(char *sHexNibbles, uint8_t *pui8Buffer, uint8_t ui8Size)
{
   for (uint8_t ui8Index = 0; ui8Index < ui8Size; ++ui8Index)
   {
      (pui8Buffer)[ui8Index] = (uint8_t)ui32ConvertHexStringToByte(&sHexNibbles[ui8Index * 2]);
   }
}
