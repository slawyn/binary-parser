#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "config.h"
#include "types.h"
#include "misc/helpers.h"
#include "misc/memory.h"

#define DUMP_ALIGNMENT    (16 - 1)

static int32_t i32MemoryDestroyBlock(Memory_t *pxMemory, Memoryblock_t *pxMemoryblock);
static Memoryblock_t * pxMemoryCreateBlock(Memory_t *pxMemory, Memoryblock_t *pxBlockNext, Memoryblock_t *pxBlockPrevious, uint32_t ui32BlockAddress, uint32_t ui32BufferSize, uint8_t rui8Buffer[]);



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
* @param ui32Address Destination Address
* *************************************************************/
static Memoryblock_t *pxMemoryFindBlock(Memory_t *pxMemory, uint32_t ui32Address)
{
   uint8_t        ui8Found              = FALSE;
   Memoryblock_t *pxMemoryblockForward  = pxMemory->pxMemoryblockHead;
   Memoryblock_t *pxMemoryblockBackward = pxMemory->pxMemoryblockTail;
   Memoryblock_t *pxMemoryblockResult   = NULL;

   while (!ui8Found)
   {
      // Looking for block forward
      if (pxMemoryblockForward != NULL)
      {
         if ((ui32Address >= pxMemoryblockForward->ui32BlockAddress) &&
             ((ui32Address <= (pxMemoryblockForward->ui32BlockAddress + pxMemoryblockForward->ui32BlockSize))))
         {
            pxMemoryblockResult = pxMemoryblockForward;
            ui8Found            = TRUE;
         }
         else
         {
            pxMemoryblockForward = pxMemoryblockForward->pxMemoryblockNext;
         }
      }
      else
      {
         pxMemoryblockResult = pxMemoryblockForward;
         ui8Found            = TRUE;
      }

      // Looking for block backward
      if (pxMemoryblockBackward != NULL)
      {
         if ((ui32Address >= pxMemoryblockBackward->ui32BlockAddress) &&
             ((ui32Address <= (pxMemoryblockBackward->ui32BlockAddress + pxMemoryblockBackward->ui32BlockSize))))
         {
            pxMemoryblockResult = pxMemoryblockBackward;
            ui8Found            = TRUE;
         }
         else
         {
            pxMemoryblockBackward = pxMemoryblockBackward->pxMemoryblockPrevious;
         }
      }
      else
      {
         pxMemoryblockResult = pxMemoryblockBackward;
         ui8Found            = TRUE;
      }
   }

   return(pxMemoryblockResult);
}

/***************************************************************
* @param pxMemory Pointer to Memory
* @return Size of Memory
***************************************************************/
uint32_t ui32MemoryGetTotalSize(Memory_t *pxMemory)
{
   uint32_t ui32Size = 0;
   if (pxMemory->pxMemoryblockHead != NULL)
   {
      if ((pxMemory->pxMemoryblockHead != pxMemory->pxMemoryblockTail))
      {
         ui32Size = (pxMemory->pxMemoryblockTail->ui32BlockAddress - pxMemory->pxMemoryblockHead->ui32BlockAddress) + pxMemory->pxMemoryblockTail->ui32BlockSize;
      }
      else
      {
         ui32Size = pxMemory->pxMemoryblockHead->ui32BlockSize;
      }
   }

   return(ui32Size);
}

/***************************************************************
* @param pxMemory Pointer to Memory
* @param ui8FreeByte Fill Byte between the blocks
* @return Pointer tp Dump struct
***************************************************************/
Dump_t * pxMemoryGenerateDump(Memory_t *pxMemory, uint8_t ui8FreeByte)
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

/***************************************************************
 * @param pxMemory Pointer to Memory
 * @param ui32DestinationAddress Destination Address
 * @param ui32Size Size of Data
 * @param pui8Data Poiinter to Data
 **************************************************************/
int32_t i32MemoryCompareDump(Dump_t *pxOriginalDump, Dump_t *pxSecondaryDump)
{
   uint8_t  i8Comparison = 0;
   uint32_t ui32Size     = pxOriginalDump->ui32Size;
   if (pxOriginalDump->ui32BaseAddress != pxSecondaryDump->ui32BaseAddress)
   {
      LogTest("memory::i32MemoryCompareDump: Error! Dump different Base Addrresses %d %d", (pxOriginalDump->ui32BaseAddress), pxSecondaryDump->ui32BaseAddress);
      i8Comparison = -1;
   }

   if (pxOriginalDump->ui32Size != pxSecondaryDump->ui32Size)
   {
      LogTest("memory::i32MemoryCompareDump: Error! Dump different sizes %d %d", (pxOriginalDump->ui32Size), pxSecondaryDump->ui32Size);
      i8Comparison = -2;
   }

   // Continue of there is no error
   if (!i8Comparison)
   {
      for (uint32_t ui32ArrayIndex = 0; ui32ArrayIndex < ui32Size; ++ui32ArrayIndex)
      {
         if (pxOriginalDump->pui8Data[ui32ArrayIndex] != pxSecondaryDump->pui8Data[ui32ArrayIndex])
         {
            LogTest("memory::i32MemoryCompareDump: Error! Dump different at %x %x %x", (pxOriginalDump->ui32BaseAddress + ui32ArrayIndex), pxOriginalDump->pui8Data[ui32ArrayIndex], pxSecondaryDump->pui8Data[ui32ArrayIndex]);
            i8Comparison = -3;
         }
      }
   }

   return(i8Comparison);
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
   printf("Memory:[%-2d]", pxMemory->ui32BlockCount);

   // Print contents
   pxMemoryblock = pxMemory->pxMemoryblockHead;
   for (ui32BlockIndex = 0; ui32BlockIndex < pxMemory->ui32BlockCount; ++ui32BlockIndex)
   {
      printf("\n%010x[%02d]", pxMemoryblock->ui32BlockAddress, pxMemoryblock->ui32BlockSize);
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
* @param ui32RegionStartingAddress Starting Address
* @param ui32RegionEndingAddress Ending Address
* @return Status
***************************************************************/
int32_t i32MemoryDeleteRegion(Memory_t *pxMemory, uint32_t ui32RegionStartingAddress, uint32_t ui32RegionEndingAddress)
{
   Memoryblock_t *pxMemoryblock;
   Memoryblock_t *pxMemoryTempblock;
   uint8_t        ui8Done = FALSE;
   int8_t         i8Error = 0;
   int32_t        i32MemoryOverlap;

   // Free Destination blocks
   //-----------------------------------------
   pxMemoryblock = pxMemory->pxMemoryblockHead;

   while (!ui8Done && !i8Error)
   {
      // Preserve pointer to next for traversing
      pxMemoryTempblock = pxMemoryblock->pxMemoryblockNext;

      // Split the first intersecting block in the destination region
      if (((pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) >= ui32RegionStartingAddress))
      {
         LogTest("memory::i32MemoryDeleteRegion: Traversing Block at %x", pxMemoryblock->ui32BlockAddress);
         if (pxMemoryblock->ui32BlockAddress < ui32RegionStartingAddress)
         {
            i32MemoryOverlap = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32RegionStartingAddress;
            if (i32MemoryOverlap > 0)
            {
               LogTest("memory::i32MemoryDeleteRegion: Splitting-0 Destination Block at %x", pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize - i32MemoryOverlap);

               // Create new buffer
               uint8_t *pui8SplitBuffer = malloc((pxMemoryblock->ui32BlockSize - i32MemoryOverlap));
               uint8_t *pui8TempBuffer  = pxMemoryblock->pui8Buffer;
               memcpy(pui8SplitBuffer, pui8TempBuffer, (pxMemoryblock->ui32BlockSize - i32MemoryOverlap));

               // Assign new buffer
               pxMemoryblock->pui8Buffer     = pui8SplitBuffer;
               pxMemoryblock->ui32BlockSize -= i32MemoryOverlap;

               // Buffer outside of range, create new block
               if ((ui32RegionStartingAddress + i32MemoryOverlap) >= ui32RegionEndingAddress)
               {
                  LogTest("memory::i32MemoryDeleteRegion: Adding-0 Destination Block at %x of %d bytes", ui32RegionEndingAddress, i32MemoryOverlap);
                  i8Error = i32MemoryAdd(pxMemory, ui32RegionStartingAddress, i32MemoryOverlap, pui8TempBuffer);
               }

               // Free old buffer
               free(pui8TempBuffer);
            }
         }
         else if (pxMemoryblock->ui32BlockAddress < ui32RegionEndingAddress)
         {
            i32MemoryOverlap = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32RegionEndingAddress;
            if (i32MemoryOverlap > 0)
            {
               LogTest("memory::i32MemoryDeleteRegion: Splitting-1 Destination Block at %x", pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize - i32MemoryOverlap);

               // Create new buffer
               uint8_t *pui8SplitBuffer = malloc(i32MemoryOverlap);
               uint8_t *pui8TempBuffer  = pxMemoryblock->pui8Buffer;
               memcpy(pui8SplitBuffer, (pui8TempBuffer + pxMemoryblock->ui32BlockSize - i32MemoryOverlap), i32MemoryOverlap);

               // Assign new buffer and size
               pxMemoryblock->ui32BlockAddress += pxMemoryblock->ui32BlockSize - i32MemoryOverlap;
               pxMemoryblock->pui8Buffer        = pui8SplitBuffer;
               pxMemoryblock->ui32BlockSize     = i32MemoryOverlap;

               // Free old buffer
               free(pui8TempBuffer);
            }
            else
            {
               LogTest("memory::i32MemoryDeleteRegion: Destroying-1 Destination Block at %x", pxMemoryblock->ui32BlockAddress);
               i8Error = i32MemoryDestroyBlock(pxMemory, pxMemoryblock);
            }
         }
         else
         {
            pxMemoryTempblock = NULL;
         }
      }


      // Get next block
      if (pxMemoryTempblock == NULL)
      {
         ui8Done = TRUE;
      }
      else
      {
         pxMemoryblock = pxMemoryTempblock;
      }
   }

   return(i8Error);
}

/***************************************************************
* @param pxMemory Pointer to Memory
* @param ui32SourceStartAddress Source Address
* @param ui32DestinationStartAddress Destination Address
* @param i32RegionSize Size to Copy
***************************************************************/
int32_t i32MemoryCopyRegion(Memory_t *pxMemory, uint32_t ui32SourceStartAddress, uint32_t ui32DestinationStartAddress, int32_t i32RegionSize)
{
   Memoryblock_t *pxMemoryblock;
   Memoryblock_t *pxMemoryTempblock;

   uint32_t ui32SourceEndAddress      = ui32SourceStartAddress + i32RegionSize;
   uint32_t ui32DestinationEndAddress = ui32DestinationStartAddress + i32RegionSize;
   int32_t  i32Offset = 0;
   uint32_t ui32TempSize;
   int32_t  i32MemoryOverlap;
   uint8_t  ui8Done = FALSE;
   int8_t   i8Error = 0;

   // Invalid Pointers
   if (pxMemory->pxMemoryblockHead == NULL || pxMemory->pxMemoryblockTail == NULL)
   {
      LogTest("memory::i32MemoryCopyRegion: Error:Head or Tail NULL");
      return(-1);
   }

   // Size is overlapping
   if (ui32DestinationStartAddress > ui32SourceStartAddress)
   {
      i32Offset = ui32DestinationStartAddress - ui32SourceStartAddress;
   }
   else
   {
      i32Offset = ui32SourceStartAddress - ui32DestinationStartAddress;
   }

   // Space between source and destination regions is smaller than copy size
   if (i32Offset < i32RegionSize)
   {
      LogTest("memory::i32MemoryCopyRegion: Error:Regions overlap");
      return(-2);
   }

   // Free Destination Region
   //--------------------------
   i8Error = i32MemoryDeleteRegion(pxMemory, ui32DestinationStartAddress, ui32DestinationEndAddress);


   // Copy blocks
   //-----------------------------------------
   ui8Done       = FALSE;
   pxMemoryblock = pxMemory->pxMemoryblockHead;
   while (!ui8Done && !i8Error)
   {
      // Preserve pointer to next for traversing
      pxMemoryTempblock = pxMemoryblock->pxMemoryblockNext;

      // Inside region
      if (((pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) >= ui32SourceStartAddress))
      {
         // Split block
         if (pxMemoryblock->ui32BlockAddress < ui32SourceStartAddress)
         {
            i32MemoryOverlap = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32SourceStartAddress;
            if (i32MemoryOverlap > 0)
            {
               LogTest("memory::i32MemoryCopyRegion: [D]Splitting-0 Source Block at %x", pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize - i32MemoryOverlap);

               // Assign new buffer
               pxMemoryblock->ui32BlockSize -= i32MemoryOverlap;

               // Buffer outside of range, create new block
               if ((ui32SourceStartAddress + i32MemoryOverlap) >= ui32SourceEndAddress)
               {
                  LogTest("memory::i32MemoryCopyRegion: [D]Adding-0 Source Block at %x of %d bytes", ui32SourceStartAddress, i32MemoryOverlap);
                  i8Error = i32MemoryAdd(pxMemory, ui32SourceStartAddress, i32MemoryOverlap, (pxMemoryblock->pui8Buffer + pxMemoryblock->ui32BlockSize));
               }

               // Copy to destination
               i8Error |= i32MemoryAdd(pxMemory, ui32DestinationStartAddress, i32MemoryOverlap, (pxMemoryblock->pui8Buffer + pxMemoryblock->ui32BlockSize));
            }
         }
         else if (pxMemoryblock->ui32BlockAddress < ui32SourceEndAddress)
         {
            i32MemoryOverlap = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32SourceEndAddress;
            if (i32MemoryOverlap > 0)
            {
               ui32TempSize = (pxMemoryblock->ui32BlockSize - i32MemoryOverlap);
            }

            LogTest("memory::i32MemoryCopyRegion: [D]Adding-1 Destination Block at %x of %d", pxMemoryblock->ui32BlockAddress + i32Offset, ui32TempSize);
            i8Error = i32MemoryAdd(pxMemory, pxMemoryblock->ui32BlockAddress + i32Offset, ui32TempSize, pxMemoryblock->pui8Buffer);
         }
         else
         {
            pxMemoryTempblock = NULL;
         }
      }

      // Get next block
      if (pxMemoryTempblock == NULL)
      {
         ui8Done = TRUE;
      }
      else
      {
         pxMemoryblock = pxMemoryTempblock;
      }
   }

   return(i8Error);
}

/*************************************************************
 * @param pxMemory Pointer to Memory
 * @param ui32BlockAddress Block base address
 * @param ui32BufferSize Byte Count
 * @param rui8Buffer Buffer Pointer
 **************************************************************/
static Memoryblock_t * pxMemoryCreateBlock(Memory_t *pxMemory, Memoryblock_t *pxBlockPrevious, Memoryblock_t *pxBlockNext, uint32_t ui32BlockAddress, uint32_t ui32BufferSize, uint8_t rui8Buffer[])
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
   pxMemoryblock->ui32BlockAddress      = ui32BlockAddress;
   pxMemoryblock->ui32BlockSize         = ui32BufferSize;
   pxMemoryblock->pui8Buffer            = pui8Buffer;
   pxMemoryblock->pxMemoryblockNext     = NULL;
   pxMemoryblock->pxMemoryblockPrevious = NULL;

   // Connect blocks
   if (pxBlockNext != NULL)
   {
      pxMemoryblock->pxMemoryblockNext   = pxBlockNext;
      pxBlockNext->pxMemoryblockPrevious = pxMemoryblock;
   }

   if (pxBlockPrevious != NULL)
   {
      pxMemoryblock->pxMemoryblockPrevious = pxBlockPrevious;
      pxBlockPrevious->pxMemoryblockNext   = pxMemoryblock;
   }

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

   // Reconnect
   if (pxMemoryblock->pxMemoryblockPrevious != NULL)
   {
      pxMemoryblock->pxMemoryblockPrevious->pxMemoryblockNext = pxMemoryblock->pxMemoryblockNext;
   }

   if (pxMemoryblock->pxMemoryblockNext != NULL)
   {
      pxMemoryblock->pxMemoryblockNext->pxMemoryblockPrevious = pxMemoryblock->pxMemoryblockPrevious;
   }

   // Free
   if (pxMemoryblock->pui8Buffer != NULL)
   {
      free(pxMemoryblock->pui8Buffer);
   }
   free(pxMemoryblock);
   --pxMemory->ui32BlockCount;
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
   Memoryblock_t *pxMemoryblockTraversee;
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
      pxMemoryblock = pxMemoryCreateBlock(pxMemory, NULL, NULL, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
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
         pxMemoryblock = pxMemoryCreateBlock(pxMemory, NULL, pxMemory->pxMemoryblockHead, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
         if (pxMemoryblock == NULL)
         {
            return(-2);
         }

         pxMemory->pxMemoryblockHead = pxMemoryblock;

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
            // Memory consumed by previous block
            if (i32MemoryOverlap > ui32BufferSize)
            {
               LogTest("memory::i32MemoryAdd: OP-Tail-0 at [%x] of %d", pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize - i32MemoryOverlap, ui32BufferSize);
               memcpy(&pxMemoryblock->pui8Buffer[pxMemoryblock->ui32BlockSize - i32MemoryOverlap], rui8Buffer, ui32BufferSize);
               ui32BufferSize = 0;
            }
            // Only part of region is consumed
            else
            {
               LogTest("memory::i32MemoryAdd: OP-Tail-1 at [%x] of %d", pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize - i32MemoryOverlap, i32MemoryOverlap);
               memcpy(&pxMemoryblock->pui8Buffer[pxMemoryblock->ui32BlockSize - i32MemoryOverlap], rui8Buffer, i32MemoryOverlap);
               ui32FullBlockAddress += i32MemoryOverlap;
               ui32BufferSize       -= i32MemoryOverlap;
               rui8Buffer            = &rui8Buffer[i32MemoryOverlap];
            }
         }

         // Prepend Block with valid size
         if (ui32BufferSize > 0)
         {
            pxMemoryblock = pxMemoryCreateBlock(pxMemory, pxMemory->pxMemoryblockTail, NULL, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
            if (pxMemoryblock == NULL)
            {
               return(-2);
            }
            pxMemory->pxMemoryblockTail = pxMemoryblock;
            ui32BufferSize = 0;
         }
      }


      // Searching forward
      // Mova forward until no blocks left
      //-------------------------------------------------
      pxMemoryblockTraversee = pxMemory->pxMemoryblockHead;
      while (ui32BufferSize > 0)
      {
         LogTest("memory::i32MemoryAdd: Iteration at [%x] of %d with previous Base [%x]", ui32FullBlockAddress, ui32BufferSize, pxMemoryblockTraversee->ui32BlockAddress);

         // Previous block overlaps with the new region
         // Reduce overlap to size
         i32MemoryOverlap = (pxMemoryblockTraversee->ui32BlockAddress + pxMemoryblockTraversee->ui32BlockSize) - ui32FullBlockAddress;
         if (i32MemoryOverlap > 0)
         {
            i32MemoryOverlap = i32MemoryOverlap > ui32BufferSize?ui32BufferSize:i32MemoryOverlap;

            LogTest("memory::i32MemoryAdd: OP-1 at [%x] of %d", (pxMemoryblockTraversee->ui32BlockAddress + pxMemoryblockTraversee->ui32BlockSize - i32MemoryOverlap), i32MemoryOverlap);
            memcpy(&pxMemoryblockTraversee->pui8Buffer[pxMemoryblockTraversee->ui32BlockSize - i32MemoryOverlap], rui8Buffer, i32MemoryOverlap);
            ui32FullBlockAddress += i32MemoryOverlap;
            ui32BufferSize       -= i32MemoryOverlap;
            rui8Buffer            = &rui8Buffer[i32MemoryOverlap];
         }
         //No Next block
         else if (pxMemoryblockTraversee->pxMemoryblockNext == NULL)
         {
            LogTest("memory::i32MemoryAdd: CB-0 at [%x] of %d", ui32FullBlockAddress, ui32BufferSize);
            pxMemoryblock = pxMemoryCreateBlock(pxMemory, pxMemoryblockTraversee, pxMemoryblockTraversee->pxMemoryblockNext, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
            if (pxMemoryblock == NULL)
            {
               return(-2);
            }
            ui32BufferSize = 0;
         }

         // Following the copying
         else
         {
            // Get the next block
            i32FreeSpace = (pxMemoryblockTraversee->pxMemoryblockNext->ui32BlockAddress - ui32FullBlockAddress);
            if (i32FreeSpace > 0)
            {
               // Limit the size of block
               i32FreeSpace = i32FreeSpace > ui32BufferSize?ui32BufferSize:i32FreeSpace;

               LogTest("memory::i32MemoryAdd: CB-1 at [%x] of %d, between %x %x", ui32FullBlockAddress, i32FreeSpace, pxMemoryblockTraversee->ui32BlockAddress, pxMemoryblockTraversee->pxMemoryblockNext->ui32BlockAddress);
               pxMemoryblock = pxMemoryCreateBlock(pxMemory, pxMemoryblockTraversee, pxMemoryblockTraversee->pxMemoryblockNext, ui32FullBlockAddress, i32FreeSpace, rui8Buffer);
               if (pxMemoryblock == NULL)
               {
                  return(-2);
               }

               // Update values
               ui32FullBlockAddress += i32FreeSpace;
               ui32BufferSize       -= i32FreeSpace;
               rui8Buffer            = &rui8Buffer[i32FreeSpace];
            }
            else if (i32FreeSpace == 0)
            {
               // Max copy size is set to available region size
               i32MemoryOverlap = ui32BufferSize > pxMemoryblockTraversee->pxMemoryblockNext->ui32BlockSize? pxMemoryblockTraversee->pxMemoryblockNext->ui32BlockSize :ui32BufferSize;

               LogTest("memory::i32MemoryAdd: OP-2 at [%x] of %d", (pxMemoryblockTraversee->pxMemoryblockNext->ui32BlockAddress), i32MemoryOverlap);
               memcpy(pxMemoryblockTraversee->pxMemoryblockNext->pui8Buffer, rui8Buffer, i32MemoryOverlap);
               ui32FullBlockAddress += i32MemoryOverlap;
               ui32BufferSize       -= i32MemoryOverlap;
               rui8Buffer            = &rui8Buffer[i32MemoryOverlap];
            }

            pxMemoryblockTraversee = pxMemoryblockTraversee->pxMemoryblockNext;
         }
      }
   }


   LogTest("memory::i32MemoryAdd: Done");
   return(i32Error);
}
