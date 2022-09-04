#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>

#include "types.h"
#include "misc/memory.h"
#include "misc/parsers.h"
#include "misc/helpers.h"
#include "misc/file.h"


#define LINE_MALLOC_MAX    (size_t)128

/*****************************************************************************
 * @param ppui8LineBuffer
 * @param xReadMax
 * @param pxFileHandle
 ******************************************************************************/
size_t xGetLine(uint8_t **ppui8LineBuffer, const size_t xReadMax, FILE *pxFileHandle)
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
 ******************************************************************************/
int32_t i32FileLoad(char *sFileFullPath, Memory_t *pxMemory)
{
   FILE *     pxFile;
   Filetype_e eFiletype;
   int32_t    i32Length;

   pxFile = fopen(sFileFullPath, "r");
   if (pxFile == NULL)
   {
      i32Log("Error: Could not open file %s\n", sFileFullPath);
      return(-1);
   }
   else
   {
      i32Length = strlen(sFileFullPath);
      if (i32Length >= 4)
      {
         if (0 == strcmp(&sFileFullPath[i32Length - 4], ".s19"))
         {
            eFiletype = S19;
         }
         else if (0 == strcmp(&sFileFullPath[i32Length - 4], ".hex"))
         {
            eFiletype = HEX;
         }
         else
         {
            eFiletype = UNKNOWN;
            i32Log("Warning: Unknown Format");
         }

         int32_t  i32LineCount = 0;
         size_t   xLineSize;
         uint8_t *pui8Buffer;

         // Init required memory
         pui8Buffer = malloc(LINE_MALLOC_MAX);

         // Loop through until we are done with the file
         do
         {
            /* Get the next line */
            xLineSize = xGetLine(&pui8Buffer, LINE_MALLOC_MAX, pxFile);
            i32LineCount++;

            /* Show the line details */
            //i32Log("line[%06d]: chars=%06zd, contents: %s", i32LineCount, xLineSize, pui8Buffer);
            if (xLineSize > 0)
            {
               // Switch load file
               switch (eFiletype)
               {
               case S19:
                  i32S19Parse((char *)pui8Buffer, xLineSize, pxMemory);
                  break;

               case HEX:
                  i32HexParse((char *)pui8Buffer, xLineSize, pxMemory);
                  break;

               case UNKNOWN:
               default:
                  break;
               }
            }
            else if (xLineSize == 0)
            {
               i32Log("End of file");
               break;
            }
            else
            {
               i32Log("Error: Could not load file");
               break;
            }
         } while (1);
         free(pui8Buffer);
      }
      else
      {
         i32Log("Error: Filename is too short %s", sFileFullPath);
         return(-2);
      }
   }

   return(0);
}
