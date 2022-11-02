#include <stdlib.h>
#include <string.h>

#include "config.h"
#include "types.h"
#include "assert.h"
#include "misc/dump.h"
#include "misc/helpers.h"

/***************************************************************
 * @param pxOriginalDump Pointer to Original Dump Comparee
 * @param ui32Size Size of Data
 * @param pui8Data Pointer to Data
 * @return -1: different addresses
 *         -2: different sizes
 *         -3: different data
 *          0: dumps are equal
 **************************************************************/
int32_t i32DumpAddBuffer(Dump_t *pxDump, uint32_t ui32Size, const uint8_t *pui8Data)
{
   REQUIRE(pxDump);
   REQUIRE(pui8Data);

   memcpy(pxDump->pui8Data + pxDump->ui32Offset, pui8Data, ui32Size);
   pxDump->ui32Offset += ui32Size;
   return(0);
}

/***************************************************************
* @param ui32BaseAddress Base of the dump
* @param ui32Size Size of Data
***************************************************************/
Dump_t *pxDumpCreate(uint32_t ui32BaseAddress, uint32_t ui32Size)
{
   // Create Dump with Size
   Dump_t *pxDump = malloc(sizeof(Dump_t));
   if (NULL != pxDump)
   {
      // No Dump without buffer
      pxDump->pui8Data = malloc(ui32Size);
      if ((0 == ui32Size) || NULL == pxDump->pui8Data)
      {
         free(pxDump);
         pxDump = NULL;
      }
      else
      {
         pxDump->ui32BaseAddress = ui32BaseAddress;
         pxDump->ui32Size        = ui32Size;
         pxDump->ui32Offset      = 0;
      }
   }

   return(pxDump);
}

/***************************************************************
* @param ui32BaseAddress Base of the dump
* @param ui32Size Size of Data
***************************************************************/
int32_t i32DumpDestroy(Dump_t *pxDump)
{
   REQUIRE(pxDump);

   int32_t i32Error = (-1);
   if (pxDump != NULL)
   {
      // Double check
      if ((pxDump->ui32Size > 0) && (pxDump->pui8Data != NULL))
      {
         pxDump->pui8Data = NULL;
         pxDump->ui32Size = 0;
         i32Error         = 0;
      }

      // At last Release Memory
      free(pxDump);
   }

   return(i32Error);
}

/***************************************************************
 * @param pxOriginalDump Pointer to Original Dump Comparee
 * @param pxSecondaryDump Pointer to Second Dump Comparee
 * @return -1: different addresses
 *         -2: different sizes
 *         -3: different data
 *          0: dumps are equal
 **************************************************************/
int32_t i32DumpCompare(Dump_t *pxOriginalDump, Dump_t *pxSecondaryDump)
{
   REQUIRE(pxOriginalDump);
   REQUIRE(pxSecondaryDump);

   uint8_t  i8Comparison;
   uint32_t ui32Size;
   if ((pxOriginalDump == NULL) || (pxSecondaryDump == NULL))
   {
      LogError(__BASE_FILE__ "::i32DumpCompare:: Error! NULL Pointer");
      i8Comparison = -1;
   }
   else
   {
      i8Comparison = 0;
      ui32Size     = pxOriginalDump->ui32Size;
      if (pxOriginalDump->ui32Size != pxSecondaryDump->ui32Size)
      {
         LogDebug(__BASE_FILE__ "::i32DumpCompare:: Warning! Dump different sizes %d %d", (pxOriginalDump->ui32Size), pxSecondaryDump->ui32Size);
         i8Comparison = -3;
      }
   }

   // Continue of there is no error
   if (!i8Comparison)
   {
      for (uint32_t ui32ArrayIndex = 0; ui32ArrayIndex < ui32Size; ++ui32ArrayIndex)
      {
         if (pxOriginalDump->pui8Data[ui32ArrayIndex] != pxSecondaryDump->pui8Data[ui32ArrayIndex])
         {
            i8Comparison = -4;
            break;
         }
      }
   }

   return(i8Comparison);
}
