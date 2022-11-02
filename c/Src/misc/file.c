#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>

#include "config.h"
#include "types.h"
#include "misc/memory.h"
#include "misc/parsers.h"
#include "misc/file.h"

/* Private defines*/
#define LINE_MALLOC_MAX    (size_t)128

/* Private prototypes*/
PROTOTYPE size_t xGetLine(uint8_t **ppui8LineBuffer, const size_t xReadMax, FILE *pxFileHandle);


/*****************************************************************************
 * @param ppui8LineBuffer Pointer to String
 * @param xReadMax Max characters that can be read
 * @param pxFileHandle File Handle
 * @return     -1: Error file handle
 *             -2: Error line too long
 *              0: End of file
 *       positive: Line length
 ******************************************************************************/
STATIC size_t xGetLine(uint8_t **ppui8LineBuffer, const size_t xReadMax, FILE *pxFileHandle)
{
   size_t  xReadCount = 0;
   int32_t i32Char;

   /* First check that none of our input pointers are NULL. */
   if (NULL == pxFileHandle)
   {
      return(-1);
   }

   /* Step through the file, pulling characters until either a newline or EOF. */
   while (EOF != (i32Char = getc(pxFileHandle)))
   {
      /* Note we read a character. */
      xReadCount++;

      /* Reallocate the buffer if we need more room */
      if (xReadCount >= xReadMax)
      {
         return(-2);
      }

      /* Break from the loop if we hit the ending character. */
      if (i32Char == '\n')
      {
         (*ppui8LineBuffer)[xReadCount - 1] = '\0';
         break;
      }
      else
      {
         /* Add the character to the buffer. */
         (*ppui8LineBuffer)[xReadCount - 1] = (char)i32Char;
      }
   }

   /* Note if we hit EOF. */
   if (EOF == i32Char)
   {
      return(0);
   }

   /* Terminate the string by suffixing NUL. */
   (*ppui8LineBuffer)[xReadCount] = '\0';
   return((size_t)xReadCount);
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
   FILE *  pxFile;
   int32_t i32Length;
   int32_t i32Error = 0;

   pxFile = fopen(sFileFullPath, "r");
   if (pxFile == NULL)
   {
      i32Error = -1;
      LogError(__BASE_FILE__ "::i32FileLoad:: Error: Could not open file %s\n", sFileFullPath);
   }
   else
   {
      i32Length = strlen(sFileFullPath);
      i32Length = i32Length < 4? 4:i32Length;

      Parser_j jParser = NULL;
      if (0 == strcmp(&sFileFullPath[i32Length - 4], ".s19"))
      {
         jParser = i32S19Parse;
      }
      else if (0 == strcmp(&sFileFullPath[i32Length - 4], ".hex"))
      {
         jParser = i32HexParse;
      }

      // Parser
      if (jParser == NULL)
      {
         LogError(__BASE_FILE__ "::i32FileLoad:: Warning: Unknown Format");
         i32Error = -2;
      }
      else
      {
         // Loop through until we are done with the file
         size_t   xLineSize;
         int32_t  i32LineCount = 0;
         uint8_t *pui8Buffer   = malloc(LINE_MALLOC_MAX);
         do
         {
            /* Get the next line */
            xLineSize = xGetLine(&pui8Buffer, LINE_MALLOC_MAX, pxFile);
            i32LineCount++;

            /* Show the line details */
            if (xLineSize > 0)
            {
               jParser((char *)pui8Buffer, xLineSize, pxMemory);
            }
            else if (xLineSize == 0)
            {
               LogNormal(__BASE_FILE__ "::i32FileLoad:: End of file");
               break;
            }
            else
            {
               LogError(__BASE_FILE__ "::i32FileLoad:: Error: Could not load file");
               i32Error = -3;
            }
         } while (!i32Error);
         free(pui8Buffer);
      }
   }

   return(i32Error);
}
