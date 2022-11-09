#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>

#include "config.h"
#include "types.h"
#include "assert.h"
#include "misc/memory.h"
#include "misc/parsers.h"
#include "misc/file.h"

/* Private defines*/
#define LINE_MALLOC_MAX    (size_t)128

/* Private prototypes*/
PROTOTYPE size_t xGetLine(uint8_t *ppui8LineBuffer, const size_t xReadMax, FILE *pxFileHandle);


/* Private variables*/
STATIC uint8_t rui8Buffer[LINE_MALLOC_MAX];

/*****************************************************************************
 * @param ppui8LineBuffer Pointer to String
 * @param xReadMax Max characters that can be read
 * @param pxFileHandle File Handle
 * @return     -1: Error file handle
 *             -2: Error line too long
 *              0: End of file
 *       positive: Line length
 ******************************************************************************/
STATIC size_t xGetLine(uint8_t *ppui8LineBuffer, const size_t xReadMax, FILE *pxFileHandle)
{
   REQUIRE(ppui8LineBuffer && ppui8LineBuffer);
   REQUIRE(xReadMax > 0);
   REQUIRE(pxFileHandle);

   size_t  xReadCount = 0;
   int32_t i32Char;

   /* First check that none of our input pointers are NULL. */
   if (NULL == pxFileHandle || NULL == ppui8LineBuffer || NULL == ppui8LineBuffer || xReadMax == 0)
   {
      xReadCount = 0;
   }
   else
   {
      /* Step through the file, pulling characters until either a newline or EOF. */
      while (EOF != (i32Char = getc(pxFileHandle)))
      {
         /* Note we read a character. */
         xReadCount++;

         /* Reallocate the buffer if we need more room */
         if (xReadCount >= xReadMax)
         {
            xReadCount = 0;
            break;
         }
         /* Break from the loop if we hit the ending character. */
         else if (i32Char == '\n')
         {
            (ppui8LineBuffer)[xReadCount - 1] = '\0';
            break;
         }
         /* Add the character to the buffer. */
         else
         {
            (ppui8LineBuffer)[xReadCount - 1] = (char)i32Char;
         }
      }

      /* Terminate the string by suffixing NUL. */
      (ppui8LineBuffer)[xReadCount] = '\0';

      /* Note if we hit EOF. */
      if (EOF == i32Char)
      {
         xReadCount = 0;
      }
   }

   return(xReadCount);
}

/*****************************************************************************
 * @param sFileFullPath filename with full path
 * @param pxMemory Memory Pointer
 * @return       -1: Error opening file
 *               -2: Error filename short
 *                0: OK
 ******************************************************************************/
int32_t i32FileLoad(char *sFileFullPath, Memory_t *pxMemory)
{
   REQUIRE(sFileFullPath);
   REQUIRE(pxMemory);

   FILE *   pxFile;
   int32_t  i32Length;
   int32_t  i32Error = 0;
   Parser_j jParser;

   if (pxMemory == NULL || sFileFullPath == NULL)
   {
      i32Error = -1;
      LogError(__BASE_FILE__ "::i32FileLoad:: Error: NULL");
   }
   else if ((pxFile = fopen(sFileFullPath, "r")))
   {
      i32Length = strlen(sFileFullPath);
      i32Length = i32Length < 4? 4:i32Length;

      if (0 == strcmp(&sFileFullPath[i32Length - 4], ".s19"))
      {
         jParser = i32S19Parse;
      }
      else if (0 == strcmp(&sFileFullPath[i32Length - 4], ".hex"))
      {
         jParser = i32HexParse;
      }
      else
      {
         i32Error = -3;
         LogError(__BASE_FILE__ "::i32FileLoad:: Warning: Unknown Format");
      }

      // Loop through until we are done with the file
      int32_t i32LineCount = 0;
      size_t  xLineSize;
      while (!i32Error && (xLineSize = xGetLine((uint8_t *)&rui8Buffer, LINE_MALLOC_MAX, pxFile)))
      {
         i32LineCount++;
         i32Error = jParser((char *)rui8Buffer, xLineSize, pxMemory);
      }

      LogNormal(__BASE_FILE__ "::i32FileLoad:: Line End at %d", i32LineCount);
      fclose(pxFile);
   }
   else
   {
      i32Error = -2;
      LogError(__BASE_FILE__ "::i32FileLoad:: Error: Could not open file %s\n", sFileFullPath);
   }

   return(i32Error);
}
