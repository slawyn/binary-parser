#include <stdio.h>
#include <stdlib.h>
#include <windows.h>

#include "config.h"
#include "types.h"
#include "misc/memory.h"
#include "misc/dump.h"
#include "misc/helpers.h"

/* Private Prototypes */
PROTOTYPE uint32_t ui32ConvertHexNibbleToUint(char cHex);

/* Private Functions */

/*****************************************************************************
 * @param cHex Hex character
 * @return Resulting Byte
 ******************************************************************************/
STATIC uint32_t ui32ConvertHexNibbleToUint(char cHex)
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
      LogNormal(__BASE_FILE__ "::ui32ConvertHexNibbleToUint:: Error: Unknown Hex %c", cHex);
      ui32Result = 0;
   }
   return(ui32Result);
}

/*****************************************************************************
 * @param sHexNibbles String of Nibbles
 * @return Resulting Byte
 ******************************************************************************/
uint32_t ui32ConvertHexStringToByte(char *sHexNibbles)
{
   uint32_t ui32Result = ((ui32ConvertHexNibbleToUint(sHexNibbles[0]) << 4) | ui32ConvertHexNibbleToUint(sHexNibbles[1]));
   return(ui32Result);
}

/*****************************************************************************
 * @param sHexNibbles String of Nibbles
 * @return Returing Word
 ******************************************************************************/
uint32_t ui32ConvertHexStringToWord(char *sHexNibbles)
{
   uint32_t ui32Result = (ui32ConvertHexStringToByte(&sHexNibbles[0]) << 8 | ui32ConvertHexStringToByte(&sHexNibbles[2]));
   return(ui32Result);
}

/*****************************************************************************
 * @param sHexNibbles String of Nibbles
 * @return Resulting Dword
 ******************************************************************************/
uint32_t ui32ConvertHexStringToDword(char *sHexNibbles)
{
   uint32_t ui32Result = (ui32ConvertHexStringToWord(&sHexNibbles[0]) << 16 | ui32ConvertHexStringToWord(&sHexNibbles[4]));
   return(ui32Result);
}

/*****************************************************************************
 * @param cHex Hex character
 * @return Resulting byte buffer
 ******************************************************************************/
void vConvertHexStringToByteBuffer(char *sHexNibbles, uint8_t *pui8Buffer, uint8_t ui8Size)
{
   for (uint8_t ui8Index = 0; ui8Index < ui8Size; ++ui8Index)
   {
      (pui8Buffer)[ui8Index] = (uint8_t)ui32ConvertHexStringToByte(&sHexNibbles[ui8Index * 2]);
   }
}

/***************************************************************
* @param pxMemory Pointer to Memory
* @param ui8FreeByte Fill Byte between the blocks
* @return Pointer to Dump struct
***************************************************************/
Dump_t * pxConvertMemoryToDump(Memory_t *pxMemory, uint8_t ui8FreeByte)
{
   Memoryblock_t *pxMemoryblock;
   uint32_t       ui32DumpSize = ui32MemoryGetTotalSize(pxMemory);


   Dump_t *pxDump = NULL;
   if (ui32DumpSize > 0)
   {
      pxDump = malloc(sizeof(Dump_t));

      // Update base if 0
      if (pxMemory->ui32BaseAddress == 0 && (pxMemory->pxMemoryblockHead != NULL))
      {
         pxDump->ui32BaseAddress = pxMemory->pxMemoryblockHead->ui32BlockAddress;
      }
      else
      {
         pxDump->ui32BaseAddress = pxMemory->ui32BaseAddress;
      }

      pxDump->ui32Size = ui32DumpSize;
      pxDump->pui8Data = malloc(ui32DumpSize);

      // Fill with ui8Freebyte
      memset(pxDump->pui8Data, ui8FreeByte, ui32DumpSize);

      // Copy into memory
      pxMemoryblock = pxMemory->pxMemoryblockHead;
      while (pxMemoryblock != NULL)
      {
         memcpy(pxDump->pui8Data + (pxMemoryblock->ui32BlockAddress - pxDump->ui32BaseAddress), pxMemoryblock->pui8Buffer, pxMemoryblock->ui32BlockSize);
         pxMemoryblock = pxMemoryblock->pxMemoryblockNext;
      }
   }

   return(pxDump);
}
