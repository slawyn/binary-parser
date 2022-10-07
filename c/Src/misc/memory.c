#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "config.h"
#include "types.h"
#include "misc/helpers.h"
#include "misc/memory.h"



static int32_t i32MemoryDestroyBlock(Memory_t *pxMemory, Memoryblock_t *pxMemoryblock);
static Memoryblock_t * pxMemoryCreateBlock(Memory_t *pxMemory, uint32_t ui32BlockAddress, uint32_t ui32BufferSize, uint8_t rui8Buffer[]);

/***************************************************************
 * @param pxMemory Pointer to Memory
 **************************************************************/
void vMemoryInit(Memory_t *pxMemory)
{
   pxMemory->ui32BlockCount    = 0;
   pxMemory->ui32BaseAddress   = 0;
   pxMemory->pxMemoryblockTail = NULL;
   pxMemory->pxMemoryblockHead = NULL;
}

/***************************************************************
 * @param pxMemory Pointer to Memory
 * @param ui32DestinationAddress Destination Address
 * @param ui32Size Size of Data
 * @param pui8Data Poiinter to Data
 **************************************************************/
int32_t i32MemoryCompare(Memory_t *pxMemory, uint32_t ui32DestinationAddress, uint32_t ui32Size, uint8_t *pui8Data)
{
   uint8_t        ui8Error      = 1;
   Memoryblock_t *pxMemoryblock = pxMemory->pxMemoryblockHead;

   while (pxMemoryblock != NULL)
   {
      if ((ui32DestinationAddress >= pxMemoryblock->ui32BlockAddress) &&
          (ui32DestinationAddress <= pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize))
      {
         break;
      }
      else
      {
         pxMemoryblock = pxMemoryblock->pxMemoryblockNext;
      }
   }

   uint32_t ui32ArrayIndex = 0;
   for (; ui32ArrayIndex < ui32Size; ++ui32ArrayIndex)
   {
      if (pxMemoryblock == NULL)
      {
         break;
      }

      // All bytes from the region have been read, switch to next block
      uint32_t ui32IndexEnd = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32DestinationAddress;
      if (ui32IndexEnd == 0)
      {
         pxMemoryblock = pxMemoryblock->pxMemoryblockNext;
      }

      if (pxMemoryblock == NULL)
      {
         break;
      }

      uint32_t ui32IndexStart = (ui32DestinationAddress - pxMemoryblock->ui32BlockAddress);

      // Compare memory
      uint8_t ui8MemoryData = pxMemoryblock->pui8Buffer[ui32IndexStart];
      if (pui8Data[ui32ArrayIndex] != ui8MemoryData)
      {
         break;
      }

      // Go to next byte
      ++ui32DestinationAddress;
   }

   if (ui32ArrayIndex == ui32Size)
   {
      ui8Error = 0;
   }


   return(ui8Error);
}

/***************************************************************
* @param pxMemory Pointer to Memory
***************************************************************/
void vMemoryPrint(Memory_t *pxMemory)
{
   uint32_t       ui32BlockIndex;
   uint32_t       ui32InnerBufferIndex;
   Memoryblock_t *pxMemoryblock;

   // Print total count
   printf("Memory:[%-d]", pxMemory->ui32BlockCount);

   // Print contents
   pxMemoryblock = pxMemory->pxMemoryblockHead;
   for (ui32BlockIndex = 0; ui32BlockIndex < pxMemory->ui32BlockCount; ++ui32BlockIndex)
   {
      printf("\n%010x[%3d]", pxMemoryblock->ui32BlockAddress, pxMemoryblock->ui32BlockSize);
      for (ui32InnerBufferIndex = 0; ui32InnerBufferIndex < pxMemoryblock->ui32BlockSize; ++ui32InnerBufferIndex)
      {
         printf(" %02x", pxMemoryblock->pui8Buffer[ui32InnerBufferIndex]);
      }
      pxMemoryblock = pxMemoryblock->pxMemoryblockNext;
   }
   printf("\n");
}

/***************************************************************
* @param pxMemory Pointer to Memory
* @param ui32SourceStartAddress Source Address
* @param ui32DestinationStartAddress Destination Address
* @param ui32SizeToCopy Size to Copy
***************************************************************/
int32_t i32MemoryCopy(Memory_t *pxMemory, uint32_t ui32SourceStartAddress, uint32_t ui32DestinationStartAddress, int32_t i32SizeToCopy)
{
   Memoryblock_t *pxMemoryblock;
   Memoryblock_t *pxMemorySourceblock;
   Memoryblock_t *pxMemoryTempblock;

   uint32_t ui32SourceEndAddress      = ui32SourceStartAddress + i32SizeToCopy;
   uint32_t ui32DestinationEndAddress = ui32DestinationStartAddress + i32SizeToCopy;
   int32_t  i32MemoryOverlap;
   uint8_t  ui8Done = 0;

   // Invalid Pointers
   if (pxMemory->pxMemoryblockHead == NULL || pxMemory->pxMemoryblockTail == NULL)
   {
      LogTest("memory::i32MemoryCopy: Error:Head or Tail NULL");
      return(-1);
   }

   // Size is overlapping
   if (((ui32DestinationStartAddress > ui32SourceStartAddress) &&
        ((ui32DestinationStartAddress - ui32SourceStartAddress) < i32SizeToCopy)) ||
       ((ui32DestinationStartAddress <= ui32SourceStartAddress) &&
        (ui32SourceStartAddress - ui32DestinationStartAddress) < i32SizeToCopy))
   {
      LogTest("memory::i32MemoryCopy: Error:Regions overlap");
      return(-2);
   }

   // Free Destination blocks
   pxMemoryblock = pxMemory->pxMemoryblockHead;
   while (!ui8Done)
   {
      // Split the first intersecting block in the destination region
      LogTest("memory::i32MemoryCopy: Block at %x", pxMemoryblock->ui32BlockAddress);
      if (pxMemoryblock->ui32BlockAddress <= ui32DestinationStartAddress)
      {
         LogTest("memory::i32MemoryCopy: Traversing Before Destination Region");
         i32MemoryOverlap  = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32DestinationStartAddress;
         pxMemoryTempblock = pxMemoryblock->pxMemoryblockNext;
         if (i32MemoryOverlap > 0)
         {
            // Remove whole block
            if (i32MemoryOverlap == pxMemoryblock->ui32BlockSize)
            {
               i32MemoryDestroyBlock(pxMemory, pxMemoryblock);
            }
            // Split the block
            else
            {
               pxMemoryblock->ui32BlockSize -= i32MemoryOverlap;

               // Partial copy, free old and assign new
               LogTest("memory::i32MemoryCopy: Partial OP1 at %x of %d", pxMemoryblock->ui32BlockAddress, i32MemoryOverlap);
               uint8_t *pui8SplitBuffer = malloc(pxMemoryblock->ui32BlockSize);
               memcpy(pui8SplitBuffer, pxMemoryblock->pui8Buffer, pxMemoryblock->ui32BlockSize);
               free(pxMemoryblock->pui8Buffer);
               pxMemoryblock->pui8Buffer = pui8SplitBuffer;
            }
         }
         else if (i32MemoryOverlap == 0)
         {
            LogTest("memory::i32MemoryCopy: Full OP1 %x", pxMemoryblock->ui32BlockAddress);
            i32MemoryDestroyBlock(pxMemory, pxMemoryblock);
         }
         pxMemoryblock = pxMemoryTempblock;
      }

      else if (pxMemoryblock->ui32BlockAddress < ui32DestinationEndAddress)
      {
         LogTest("memory::i32MemoryCopy: Traversing Inside Destination Region");
         i32MemoryOverlap  = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32DestinationEndAddress;
         pxMemoryTempblock = pxMemoryblock->pxMemoryblockNext;

         if (i32MemoryOverlap <= 0)
         {
            LogTest("memory::i32MemoryCopy: Full OP2 %x", pxMemoryblock->ui32BlockAddress);
            i32MemoryDestroyBlock(pxMemory, pxMemoryblock);
         }
         else if (i32MemoryOverlap > 0)
         {
            // Partial copy, free old and assign new
            LogTest("memory::i32MemoryCopy: Partial OP2 at %x of %d", pxMemoryblock->ui32BlockAddress, i32MemoryOverlap);
            uint8_t *pui8SplitBuffer = malloc(i32MemoryOverlap);
            uint32_t ui32Offset      = pxMemoryblock->ui32BlockSize - i32MemoryOverlap;
            memcpy(pui8SplitBuffer, (pxMemoryblock->pui8Buffer + ui32Offset), i32MemoryOverlap);
            free(pxMemoryblock->pui8Buffer);
            pxMemoryblock->ui32BlockAddress += ui32Offset;
            pxMemoryblock->ui32BlockSize     = i32MemoryOverlap;
            pxMemoryblock->pui8Buffer        = pui8SplitBuffer;
         }
         pxMemoryblock = pxMemoryTempblock;
      }
      else
      {
         LogTest("memory::i32MemoryCopy: Traversing Done-1 at %x", pxMemoryblock->ui32BlockAddress);
         ui8Done = TRUE;
      }

      if (pxMemoryblock == NULL)
      {
         LogTest("memory::i32MemoryCopy: Traversing Done-2");
         ui8Done = TRUE;
      }
   }


   return(0);
}

/*************************************************************
 * @param pxMemory Pointer to Memory
 * @param ui32BlockAddress Block base address
 * @param ui32BufferSize Byte Count
 * @param rui8Buffer Buffer Pointer
 **************************************************************/
static Memoryblock_t * pxMemoryCreateBlock(Memory_t *pxMemory, uint32_t ui32BlockAddress, uint32_t ui32BufferSize, uint8_t rui8Buffer[])
{
   Memoryblock_t *pxMemoryblock;
   pxMemoryblock = (Memoryblock_t *)malloc(sizeof(Memoryblock_t));
   if (pxMemoryblock == NULL)
   {
      return(NULL);
   }

   uint8_t *pui8Buffer = malloc(ui32BufferSize);
   if (pui8Buffer == NULL)
   {
      free(pxMemoryblock);
      return(NULL);
   }
   else
   {
      memcpy(pui8Buffer, rui8Buffer, ui32BufferSize);
   }


   // Init block
   pxMemoryblock->ui32BlockAddress  = ui32BlockAddress;
   pxMemoryblock->ui32BlockSize     = ui32BufferSize;
   pxMemoryblock->pui8Buffer        = pui8Buffer;
   pxMemoryblock->pxMemoryblockNext = NULL;

   ++pxMemory->ui32BlockCount;
   return(pxMemoryblock);
}

/***************************************************************
* @param pxMemory Pointer to Memory
* @param ui32BlockAddress Block base address
* @param ui32BufferSize Byte Count
* @param rui8Buffer Buffer Pointer
***************************************************************/
static int32_t i32MemoryDestroyBlock(Memory_t *pxMemory, Memoryblock_t *pxMemoryblock)
{
   if (pxMemoryblock == NULL)
   {
      return(-1);
   }

   if (pxMemoryblock->pui8Buffer != NULL)
   {
      free(pxMemoryblock->pui8Buffer);
   }
   --pxMemory->ui32BlockCount;
   free(pxMemoryblock);
   return(0);
}

/**************************************************************
* @param pxMemory Pointer to Memory
* @param ui32BlockAddress Block base address
* @param ui32BufferSize Byte Count
* @param rui8Buffer Buffer Pointer
**************************************************************/
int32_t i32MemoryAdd(Memory_t *pxMemory, uint32_t ui32BlockAddress, uint32_t ui32BufferSize, uint8_t rui8Buffer[])
{
   Memoryblock_t *pxMemoryblock;
   Memoryblock_t *pxMemoryblockForward;
   Memoryblock_t *pxMemoryblockBackward;
   uint8_t        ui8Found             = 0;
   uint32_t       ui32FullBlockAddress = (ui32BlockAddress + pxMemory->ui32BaseAddress);
   int32_t        i32MemoryOverlap     = 0;
   int32_t        i32FreeSpace         = 0;
   int32_t        i32Error             = 0;

   if (0 == ui32BufferSize)
   {
      return(-1);
   }

   if (pxMemory->pxMemoryblockHead == NULL)
   {
      pxMemoryblock = pxMemoryCreateBlock(pxMemory, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
      pxMemory->pxMemoryblockHead = pxMemoryblock;
      pxMemory->pxMemoryblockTail = pxMemoryblock;
      LogTest("memory::i32MemoryAdd: Creating Head of %x at %x", ui32FullBlockAddress, pxMemoryblock->ui32BlockAddress);
   }
   else
   {
      // Prepend to Head
      //---------------------------------------------------------------------
      if (ui32FullBlockAddress < pxMemory->pxMemoryblockHead->ui32BlockAddress)
      {
         i32MemoryOverlap = (ui32FullBlockAddress + ui32BufferSize) - pxMemory->pxMemoryblockHead->ui32BlockAddress;
         if (i32MemoryOverlap > 0)
         {
            ui32BufferSize -= i32MemoryOverlap;
         }

         // Prepend Block
         pxMemoryblock = pxMemoryCreateBlock(pxMemory, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
         pxMemoryblock->pxMemoryblockNext = pxMemory->pxMemoryblockHead;
         pxMemory->pxMemoryblockHead      = pxMemoryblock;

         // Prepare for traversing
         if (i32MemoryOverlap > 0)
         {
            LogTest("memory::i32MemoryAdd: OP-Head-0 at [%x] of %d", pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize - i32MemoryOverlap, i32MemoryOverlap);
            rui8Buffer            = &rui8Buffer[ui32BufferSize];
            ui32FullBlockAddress += ui32BufferSize;
            ui32BufferSize        = i32MemoryOverlap;
         }
         else
         {
            // Whole block consumed
            ui32BufferSize = 0;
         }
      }
      else if (ui32FullBlockAddress > pxMemory->pxMemoryblockTail->ui32BlockAddress)
      {
         // Tail
         pxMemoryblock    = pxMemory->pxMemoryblockTail;
         i32MemoryOverlap = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32FullBlockAddress;
         if (i32MemoryOverlap > 0)
         {
            if (i32MemoryOverlap > ui32BufferSize)
            {
               LogTest("memory::i32MemoryAdd: OP-Tail-0 at [%x] of %d", pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize - i32MemoryOverlap, ui32BufferSize);
               memcpy(&pxMemoryblock->pui8Buffer[pxMemoryblock->ui32BlockSize - i32MemoryOverlap], rui8Buffer, ui32BufferSize);
               ui32BufferSize = 0;
            }
            else
            {
               LogTest("memory::i32MemoryAdd: OP-Tail-1 at [%x] of %d", pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize - i32MemoryOverlap, i32MemoryOverlap);
               memcpy(&pxMemoryblock->pui8Buffer[pxMemoryblock->ui32BlockSize - i32MemoryOverlap], rui8Buffer, i32MemoryOverlap);
               ui32FullBlockAddress += i32MemoryOverlap;
               ui32BufferSize       -= i32MemoryOverlap;
               rui8Buffer            = &rui8Buffer[i32MemoryOverlap];
            }
         }
         if (ui32BufferSize > 0)
         {
            // Prepend Block
            pxMemoryblock = pxMemoryCreateBlock(pxMemory, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
            pxMemory->pxMemoryblockTail->pxMemoryblockNext = pxMemoryblock;
            pxMemory->pxMemoryblockTail = pxMemoryblock;
            ui32BufferSize = 0;
         }
      }


      // Searching forward
      // Until no blocks left
      //-------------------------------------------------
      pxMemoryblockForward = pxMemory->pxMemoryblockHead;
      while (pxMemoryblockForward->pxMemoryblockNext != NULL)
      {
         if (ui32FullBlockAddress >= pxMemoryblockForward->pxMemoryblockNext->ui32BlockAddress)
         {
            pxMemoryblockForward = pxMemoryblockForward->pxMemoryblockNext;
         }
         else
         {
            break;
         }
      }

      // Move foreward
      while (ui32BufferSize > 0)
      {
         LogTest("memory::i32MemoryAdd: Iteration at [%x] of %d with previous Base [%x]", ui32FullBlockAddress, ui32BufferSize, pxMemoryblockForward->ui32BlockAddress);


         // Previous block overlaps with the new region
         // Reduce overlap to size
         i32MemoryOverlap = (pxMemoryblockForward->ui32BlockAddress + pxMemoryblockForward->ui32BlockSize) - ui32FullBlockAddress;
         if (i32MemoryOverlap > 0)
         {
            i32MemoryOverlap = i32MemoryOverlap > ui32BufferSize?ui32BufferSize:i32MemoryOverlap;

            LogTest("memory::i32MemoryAdd: OP-1 at [%x] of %d", (pxMemoryblockForward->ui32BlockAddress + pxMemoryblockForward->ui32BlockSize - i32MemoryOverlap), i32MemoryOverlap);
            memcpy(&pxMemoryblockForward->pui8Buffer[pxMemoryblockForward->ui32BlockSize - i32MemoryOverlap], rui8Buffer, i32MemoryOverlap);
            ui32FullBlockAddress += i32MemoryOverlap;
            ui32BufferSize       -= i32MemoryOverlap;
            rui8Buffer            = &rui8Buffer[i32MemoryOverlap];
         }
         //No Next block
         else if (pxMemoryblockForward->pxMemoryblockNext == NULL)
         {
            LogTest("memory::i32MemoryAdd: CB-0 at [%x] of %d", ui32FullBlockAddress, ui32BufferSize);
            pxMemoryblock = pxMemoryCreateBlock(pxMemory, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
            pxMemoryblock->pxMemoryblockNext        = pxMemoryblockForward->pxMemoryblockNext;
            pxMemoryblockForward->pxMemoryblockNext = pxMemoryblock;
            ui32BufferSize = 0;
         }

         // Following the copying
         else
         {
            // Get the next block
            i32FreeSpace = (pxMemoryblockForward->pxMemoryblockNext->ui32BlockAddress - ui32FullBlockAddress);
            if (i32FreeSpace > 0)
            {
               // Limit the size of block
               i32FreeSpace = i32FreeSpace > ui32BufferSize?ui32BufferSize:i32FreeSpace;

               LogTest("memory::i32MemoryAdd: CB-1 at [%x] of %d, between %x %x", ui32FullBlockAddress, i32FreeSpace, pxMemoryblockForward->ui32BlockAddress, pxMemoryblockForward->pxMemoryblockNext->ui32BlockAddress);
               pxMemoryblock = pxMemoryCreateBlock(pxMemory, ui32FullBlockAddress, i32FreeSpace, rui8Buffer);
               pxMemoryblock->pxMemoryblockNext        = pxMemoryblockForward->pxMemoryblockNext;
               pxMemoryblockForward->pxMemoryblockNext = pxMemoryblock;

               ui32FullBlockAddress += i32FreeSpace;
               ui32BufferSize       -= i32FreeSpace;
               rui8Buffer            = &rui8Buffer[i32FreeSpace];
            }
            else if (i32FreeSpace == 0)
            {
               // Max copy size is set to available region size
               i32MemoryOverlap = ui32BufferSize > pxMemoryblockForward->pxMemoryblockNext->ui32BlockSize? pxMemoryblockForward->pxMemoryblockNext->ui32BlockSize :ui32BufferSize;

               LogTest("memory::i32MemoryAdd: OP-2 at [%x] of %d", (pxMemoryblockForward->pxMemoryblockNext->ui32BlockAddress), i32MemoryOverlap);
               memcpy(pxMemoryblockForward->pxMemoryblockNext->pui8Buffer, rui8Buffer, i32MemoryOverlap);
               ui32FullBlockAddress += i32MemoryOverlap;
               ui32BufferSize       -= i32MemoryOverlap;
               rui8Buffer            = &rui8Buffer[i32MemoryOverlap];
            }

            pxMemoryblockForward = pxMemoryblockForward->pxMemoryblockNext;
         }
      }
   }


   LogTest("memory::i32MemoryAdd: Done");
   return(i32Error);
}
