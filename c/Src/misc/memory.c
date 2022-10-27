#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "config.h"
#include "types.h"
#include "misc/helpers.h"
#include "misc/memory.h"
#include "misc/dump.h"


/* Private Functions*/
static int32_t i32MemoryRemoveBlock(Memory_t *pxMemory, Memoryblock_t *pxMemoryblock);
static Memoryblock_t * pxMemoryCreateBlock(uint32_t ui32BlockAddress, uint32_t ui32BufferSize, uint8_t const rui8Buffer[]);



/*************************************************************
 * @param pxMemory Pointer to Memory
 * @param ui32BlockAddress Block base address
 * @param ui32BufferSize Byte Count
 * @param rui8Buffer Buffer Pointer
 **************************************************************/
static Memoryblock_t * pxMemoryCreateBlock(uint32_t ui32BlockAddress, uint32_t ui32BufferSize, uint8_t const rui8Buffer[])
{
   Memoryblock_t *pxMemoryblock = (Memoryblock_t *)malloc(sizeof(Memoryblock_t));

   if (ui32BufferSize > 0 || pxMemoryblock != NULL)
   {
      pxMemoryblock->pui8Buffer = malloc(ui32BufferSize);
   }

   // Continue if buffer was allocated
   if (pxMemoryblock->pui8Buffer == NULL)
   {
      free(pxMemoryblock);
      pxMemoryblock = NULL;
   }
   else
   {
      // Init block
      memcpy(pxMemoryblock->pui8Buffer, rui8Buffer, ui32BufferSize);
      pxMemoryblock->ui32BlockAddress      = ui32BlockAddress;
      pxMemoryblock->ui32BlockSize         = ui32BufferSize;
      pxMemoryblock->pxMemoryblockNext     = NULL;
      pxMemoryblock->pxMemoryblockPrevious = NULL;
   }

   return(pxMemoryblock);
}

static int32_t i32MemoryInsertBlock(Memory_t *pxMemory, Memoryblock_t *pxMemoryblockBase, Memoryblock_t *pxMemoryblock)
{
   int32_t i32Status = 0;

   // Set  Head and tail
   if (pxMemory->pxMemoryblockHead == NULL)
   {
      pxMemory->pxMemoryblockHead = pxMemoryblock;
      pxMemory->pxMemoryblockTail = pxMemoryblock;
      ++pxMemory->ui32BlockCount;
      LogDebug(__BASE_FILE__ "::i32MemoryInsertBlock:: Set Head [%x} {%d}", pxMemoryblock->ui32BlockAddress, pxMemoryblock->ui32BlockSize);
   }
   else if (pxMemoryblock == NULL)
   {
      LogDebug(__BASE_FILE__ "::i32MemoryInsertBlock:: Error");
      i32Status = -1;
   }
   else
   {
      // Connect to next block
      if (pxMemoryblockBase != NULL)
      {
         // Connect forward to base -> current -> base+1
         pxMemoryblock->pxMemoryblockNext     = pxMemoryblockBase->pxMemoryblockNext;
         pxMemoryblockBase->pxMemoryblockNext = pxMemoryblock;

         // Connect backward base <- current <- base+1
         pxMemoryblock->pxMemoryblockPrevious = pxMemoryblockBase;
         if (pxMemoryblock->pxMemoryblockNext != NULL)
         {
            pxMemoryblock->pxMemoryblockNext->pxMemoryblockPrevious = pxMemoryblock;
            LogDebug(__BASE_FILE__ "::i32MemoryInsertBlock:: [%x]{%d}->[%x]{%d}->[%x]{%d]", pxMemoryblockBase->ui32BlockAddress, pxMemoryblockBase->ui32BlockSize, pxMemoryblock->ui32BlockAddress, pxMemoryblock->ui32BlockSize, pxMemoryblock->pxMemoryblockNext->ui32BlockAddress, pxMemoryblock->pxMemoryblockNext->ui32BlockSize);
         }
         else
         {
            LogDebug(__BASE_FILE__ "::i32MemoryInsertBlock:: [%x]{%d}->[%x]{%d}->[NULL]", pxMemoryblockBase->ui32BlockAddress, pxMemoryblockBase->ui32BlockSize, pxMemoryblock->ui32BlockAddress, pxMemoryblock->ui32BlockSize);
         }

         // Update tail
         if (pxMemoryblock->ui32BlockAddress > pxMemory->pxMemoryblockTail->ui32BlockAddress)
         {
            LogDebug(__BASE_FILE__ "::i32MemoryInsertBlock:: Set Tail [%x} {%d}", pxMemoryblock->ui32BlockAddress, pxMemoryblock->ui32BlockSize);
            pxMemory->pxMemoryblockTail = pxMemoryblock;
         }
      }
      // Prepend to head
      else
      {
         pxMemoryblock->pxMemoryblockNext = pxMemory->pxMemoryblockHead;
         pxMemory->pxMemoryblockHead->pxMemoryblockPrevious = pxMemoryblock;
         pxMemory->pxMemoryblockHead = pxMemoryblock;
         LogDebug(__BASE_FILE__ "::i32MemoryInsertBlock:: Prepend Head [%x} {%d}", pxMemoryblock->ui32BlockAddress, pxMemoryblock->ui32BlockSize);
      }

      ++pxMemory->ui32BlockCount;
   }


   return(i32Status);
}

/*************************************************************
 * @param pxMemoryblock Memory block to update
 * @param ui32BufferOffset Offset in buffer
 * @param ui32BufferSize Byte Count
 * @param rui8Buffer Buffer Pointer
 **************************************************************/
static int32_t i32MemoryUpdateBlock(Memoryblock_t *pxMemoryblock, uint32_t ui32BufferOffset, uint32_t ui32BufferSize, uint8_t const rui8Buffer[])
{
   int32_t i32Status = 0;
   if (pxMemoryblock == NULL)
   {
      LogDebug(__BASE_FILE__ "::i32MemoryUpdateBlock:: Error: NULL block", pxMemoryblock->ui32BlockAddress + ui32BufferOffset, ui32BufferSize);
      i32Status - 1;
   }
   else if ((ui32BufferOffset + ui32BufferSize) <= pxMemoryblock->ui32BlockSize)
   {
      LogDebug(__BASE_FILE__ "::i32MemoryUpdateBlock:: Update block [%x} {%d}", pxMemoryblock->ui32BlockAddress + ui32BufferOffset, ui32BufferSize);
      memcpy(&pxMemoryblock->pui8Buffer[ui32BufferOffset], rui8Buffer, ui32BufferSize);
   }
   else
   {
      LogDebug(__BASE_FILE__ "::i32MemoryUpdateBlock:: Error: Block [%x] {%d}", pxMemoryblock->ui32BlockAddress + ui32BufferOffset, ui32BufferSize);
      i32Status - 1;
   }

   return(i32Status);
}

/***************************************************************
* @param pxMemory Pointer to Memory
* @param ui32BlockAddress Block base address
* @param ui32BufferSize Byte Count
* @param rui8Buffer Buffer Pointer
***************************************************************/
static int32_t i32MemoryRemoveBlock(Memory_t *pxMemory, Memoryblock_t *pxMemoryblock)
{
   int32_t i32Status = 0;
   if (pxMemoryblock == NULL || pxMemoryblock->pui8Buffer == NULL || !pxMemory->ui32BlockCount)
   {
      i32Status = -1;
   }
   else
   {
      // Reconnect
      if (pxMemoryblock->pxMemoryblockPrevious != NULL)
      {
         pxMemoryblock->pxMemoryblockPrevious->pxMemoryblockNext = pxMemoryblock->pxMemoryblockNext;
      }

      if (pxMemoryblock->pxMemoryblockNext != NULL)
      {
         pxMemoryblock->pxMemoryblockNext->pxMemoryblockPrevious = pxMemoryblock->pxMemoryblockPrevious;
      }

      // Update Tail
      if (pxMemoryblock == pxMemory->pxMemoryblockTail)
      {
         pxMemory->pxMemoryblockTail = pxMemory->pxMemoryblockTail->pxMemoryblockPrevious;
         if (pxMemory->pxMemoryblockTail)
         {
            pxMemory->pxMemoryblockTail->pxMemoryblockNext = NULL;
         }
      }

      // Update Head
      if (pxMemoryblock == pxMemory->pxMemoryblockHead)
      {
         pxMemory->pxMemoryblockHead = pxMemory->pxMemoryblockHead->pxMemoryblockNext;
         if (pxMemory->pxMemoryblockHead)
         {
            pxMemory->pxMemoryblockHead->pxMemoryblockPrevious = NULL;
         }
      }



      // Free
      free(pxMemoryblock->pui8Buffer);
      free(pxMemoryblock);
      --pxMemory->ui32BlockCount;
   }
   return(i32Status);
}

/***************************************************************
 * @param pxMemory Pointer to Memory
 **************************************************************/
void vMemoryInitialize(Memory_t *pxMemory)
{
   pxMemory->ui32BlockCount    = 0;
   pxMemory->ui32BaseAddress   = 0;
   pxMemory->pxMemoryblockTail = NULL;
   pxMemory->pxMemoryblockHead = NULL;
}

/***************************************************************
 * @param pxMemory Pointer to Memory
 **************************************************************/
int32_t i32MemoryDeinitialize(Memory_t *pxMemory)
{
   Memoryblock_t *pxMemoryblock = pxMemory->pxMemoryblockHead;
   Memoryblock_t *pxMemoryblockNext;
   int32_t        i32Status = 0;

   while (!i32Status && pxMemory->ui32BlockCount)
   {
      if (pxMemoryblock == NULL)
      {
         i32Status = -1;
      }
      else
      {
         // Deallocate and move head
         pxMemoryblockNext = pxMemoryblock->pxMemoryblockNext;
         if (0 == i32MemoryRemoveBlock(pxMemory, pxMemoryblock))
         {
            pxMemory->pxMemoryblockHead = pxMemoryblockNext;
            pxMemoryblock = pxMemoryblockNext;
         }
         else
         {
            i32Status = -2;
         }
      }
   }

   // Reset memory
   if (!i32Status)
   {
      pxMemory->ui32BaseAddress   = 0;
      pxMemory->pxMemoryblockTail = NULL;
      pxMemory->pxMemoryblockHead = NULL;
   }
   else
   {
      LogError(__BASE_FILE__ "::i32MemoryDeinitialize:: Error with Memoryblock %d", pxMemory->ui32BlockCount);
   }

   return(i32Status);
}

/***************************************************************
* @param pxMemory Pointer to Memory
* @return   0  equal
*           x  not equal
***************************************************************/
int32_t i32MemoryCompare(Memory_t *pxMemoryOriginal, Memory_t *pxMemorySecondary, uint8_t ui8Freebyte)
{
   Memoryblock_t *pxMemoryblockOriginal;
   Memoryblock_t *pxMemoryblockSecondary;
   int32_t        i32Status = 0;

   if (pxMemorySecondary == NULL || pxMemoryOriginal == NULL)
   {
      i32Status = -1;
   }
   else
   {
      uint32_t ui32Index1 = 0;
      uint32_t ui32Index2 = 0;
      pxMemoryblockOriginal  = pxMemoryOriginal->pxMemoryblockHead;
      pxMemoryblockSecondary = pxMemorySecondary->pxMemoryblockHead;

      while (!i32Status && pxMemoryblockOriginal != NULL && pxMemoryblockSecondary != NULL)
      {
         // One is lagging behind
         if ((pxMemoryblockOriginal->ui32BlockAddress + ui32Index1) > (pxMemoryblockSecondary->ui32BlockAddress + ui32Index2))
         {
            if (ui8Freebyte != pxMemoryblockSecondary->pui8Buffer[ui32Index2++])
            {
               i32Status = -4;
            }
         }
         // The other is lagging behind
         else if ((pxMemoryblockOriginal->ui32BlockAddress + ui32Index1) < (pxMemoryblockSecondary->ui32BlockAddress + ui32Index2))
         {
            if (ui8Freebyte != pxMemoryblockOriginal->pui8Buffer[ui32Index1++])
            {
               i32Status = -3;
            }
         }
         // At equal addresses
         else if (pxMemoryblockOriginal->pui8Buffer[ui32Index1] == pxMemoryblockSecondary->pui8Buffer[ui32Index2])
         {
            ++ui32Index1;
            ++ui32Index2;
         }
         else
         {
            i32Status = -5;
         }

         // Switch Original here to next block
         if (ui32Index1 >= pxMemoryblockOriginal->ui32BlockSize)
         {
            pxMemoryblockOriginal = pxMemoryblockOriginal->pxMemoryblockNext;
            ui32Index1            = 0;
         }

         // Switch Secondary here to next block
         if (ui32Index2 >= pxMemoryblockSecondary->ui32BlockSize)
         {
            pxMemoryblockSecondary = pxMemoryblockSecondary->pxMemoryblockNext;
            ui32Index2             = 0;
         }
      }

      // Compare the rest against free bytes
      while (!i32Status && pxMemoryblockOriginal != NULL)
      {
         // Switch Original here to next block
         if (ui32Index1 >= pxMemoryblockOriginal->ui32BlockSize)
         {
            pxMemoryblockOriginal = pxMemoryblockOriginal->pxMemoryblockNext;
            ui32Index1            = 0;
         }
         else if (pxMemoryblockOriginal->pui8Buffer[ui32Index1++] != ui8Freebyte)
         {
            i32Status = -6;
         }
      }


      while (!i32Status && pxMemoryblockSecondary != NULL)
      {
         // Switch Original here to next block
         if (ui32Index2 >= pxMemoryblockSecondary->ui32BlockSize)
         {
            pxMemoryblockSecondary = pxMemoryblockSecondary->pxMemoryblockNext;
            ui32Index2             = 0;
         }
         else if (pxMemoryblockSecondary->pui8Buffer[ui32Index2++] != ui8Freebyte)
         {
            i32Status = -7;
         }
      }
   }

   return(i32Status);
}

/***************************************************************
* @param pxMemory Pointer to Memory
* @return Size of Memory
***************************************************************/
uint32_t ui32MemoryGetTotalSize(Memory_t *pxMemory)
{
   uint32_t ui32Size;
   if (pxMemory->pxMemoryblockHead == NULL)
   {
      ui32Size = 0;
   }
   else if ((pxMemory->pxMemoryblockHead != pxMemory->pxMemoryblockTail))
   {
      ui32Size = (pxMemory->pxMemoryblockTail->ui32BlockAddress - pxMemory->pxMemoryblockHead->ui32BlockAddress) + pxMemory->pxMemoryblockTail->ui32BlockSize;
   }
   else
   {
      ui32Size = pxMemory->pxMemoryblockHead->ui32BlockSize;
   }

   return(ui32Size);
}

/***************************************************************
* @param pxMemory Pointer to Memory
***************************************************************/
int32_t i32MemoryPrint(Memory_t *pxMemory)
{
   #define ALIGN    16

   uint32_t       ui32BlockIndex;
   uint32_t       ui32InnerBufferIndex;
   Memoryblock_t *pxMemoryblock;
   int32_t        i32Status = 0;

   if (pxMemory == NULL)
   {
      i32Status = -1;
   }
   else
   {
      // Print contents
      printf("Memory:[%-d]", pxMemory->ui32BlockCount);
      pxMemoryblock = pxMemory->pxMemoryblockHead;

      for (ui32BlockIndex = 0; ui32BlockIndex < pxMemory->ui32BlockCount; ++ui32BlockIndex)
      {
         ui32InnerBufferIndex = 0;
         while (ui32InnerBufferIndex < (pxMemoryblock->ui32BlockSize))
         {
            if (ui32InnerBufferIndex % ALIGN == 0)
            {
               printf("\n%010x[%02d]", (pxMemoryblock->ui32BlockAddress + ui32InnerBufferIndex), (pxMemoryblock->ui32BlockSize - ui32InnerBufferIndex) > ALIGN?ALIGN: (pxMemoryblock->ui32BlockSize - ui32InnerBufferIndex));
            }

            printf(" %02x", pxMemoryblock->pui8Buffer[ui32InnerBufferIndex]);
            ++ui32InnerBufferIndex;
         }
         pxMemoryblock = pxMemoryblock->pxMemoryblockNext;
      }
      printf("\n");
   }

   return(i32Status);
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
   Memoryblock_t *pxMemoryblockAwaiting;
   uint32_t       ui32RegionSize = ui32RegionEndingAddress - ui32RegionStartingAddress;
   int8_t         i8Error        = 0;
   int32_t        i32Overlap;

   // Free Destination blocks
   //-----------------------------------------
   pxMemoryblock = pxMemory->pxMemoryblockTail;
   while (!i8Error && (pxMemoryblock != NULL))
   {
      pxMemoryblockAwaiting = pxMemoryblock->pxMemoryblockPrevious;
      if (pxMemoryblock->ui32BlockAddress <= ui32RegionEndingAddress)
      {
         // ||***DEL***||
         if ((pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) <= ui32RegionEndingAddress)
         {
            i8Error = i32MemoryRemoveBlock(pxMemory, pxMemoryblock);
         }

         // ||***DEL***||__N__||
         else
         {
            int32_t  i32SpaceN    = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32RegionEndingAddress;
            uint32_t ui32OffsetN  = pxMemoryblock->ui32BlockSize - i32SpaceN;
            uint32_t ui32AddressN = pxMemoryblock->ui32BlockAddress + ui32OffsetN;

            Memoryblock_t *pxMemoryblockn = pxMemoryCreateBlock(ui32AddressN, i32SpaceN, &pxMemoryblock->pui8Buffer[ui32OffsetN]);

            i8Error |= i32MemoryRemoveBlock(pxMemory, pxMemoryblock);
            i8Error |= i32MemoryInsertBlock(pxMemory, pxMemoryblockAwaiting, pxMemoryblockn);
         }
      }
      else if ((pxMemoryblock->ui32BlockAddress) < ui32RegionStartingAddress)
      {
         // ||__P__||***DEL***||_N_||
         if ((pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) > ui32RegionEndingAddress)
         {
            uint32_t       ui32SpaceP     = ui32RegionStartingAddress - pxMemoryblock->ui32BlockAddress;
            uint32_t       ui32OffsetP    = 0;
            uint32_t       ui32AddressP   = pxMemoryblock->ui32BlockAddress + ui32OffsetP;
            Memoryblock_t *pxMemoryblockp = pxMemoryCreateBlock(ui32AddressP, ui32SpaceP, &pxMemoryblock->pui8Buffer[ui32OffsetP]);

            uint32_t       ui32SpaceN     = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32RegionEndingAddress;
            uint32_t       ui32OffsetN    = (pxMemoryblock->ui32BlockSize) - ui32SpaceN;
            uint32_t       ui32AddressN   = pxMemoryblock->ui32BlockAddress + ui32OffsetN;
            Memoryblock_t *pxMemoryblockn = pxMemoryCreateBlock(ui32AddressN, ui32SpaceN, &pxMemoryblock->pui8Buffer[ui32OffsetN]);

            i8Error |= i32MemoryRemoveBlock(pxMemory, pxMemoryblock);
            i8Error |= i32MemoryInsertBlock(pxMemory, pxMemoryblockAwaiting, pxMemoryblockp);
            i8Error |= i32MemoryInsertBlock(pxMemory, pxMemoryblockp, pxMemoryblockn);
         }
         // |__P__||****DEL*******||
         else if (ui32RegionStartingAddress <= (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize))
         {
            uint32_t       ui32SpaceP     = ui32RegionStartingAddress - pxMemoryblock->ui32BlockAddress;
            uint32_t       ui32OffsetP    = 0;
            uint32_t       ui32AddressP   = pxMemoryblock->ui32BlockAddress + ui32OffsetP;
            Memoryblock_t *pxMemoryblockp = pxMemoryCreateBlock(ui32AddressP, ui32SpaceP, &pxMemoryblock->pui8Buffer[ui32OffsetP]);

            //
            i8Error |= i32MemoryRemoveBlock(pxMemory, pxMemoryblock);
            i8Error |= i32MemoryInsertBlock(pxMemory, pxMemoryblockAwaiting, pxMemoryblockp);
         }
         // Done reached HEAD
         pxMemoryblockAwaiting = NULL;
      }

      // Update block
      pxMemoryblock = pxMemoryblockAwaiting;
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
   Memoryblock_t *pxMemoryblockPrevious;

   uint32_t ui32SourceEndAddress      = ui32SourceStartAddress + i32RegionSize;
   uint32_t ui32DestinationEndAddress = ui32DestinationStartAddress + i32RegionSize;
   int32_t  i32Offset = 0;
   uint32_t ui32TempSize;
   int32_t  i32Overlap;
   uint8_t  ui8Done = FALSE;
   int8_t   i8Error = 0;

   // Invalid Pointers
   if (pxMemory->pxMemoryblockHead == NULL || pxMemory->pxMemoryblockTail == NULL)
   {
      LogDebug(__BASE_FILE__ "::i32MemoryCopyRegion:: Error:Head or Tail NULL");
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
      LogDebug(__BASE_FILE__ "::i32MemoryCopyRegion:: Error:Regions overlap");
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
      pxMemoryblockPrevious = pxMemoryblock->pxMemoryblockNext;

      // Inside region
      if (((pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) >= ui32SourceStartAddress))
      {
         // Split block
         if (pxMemoryblock->ui32BlockAddress < ui32SourceStartAddress)
         {
            i32Overlap = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32SourceStartAddress;
            if (i32Overlap > 0)
            {
               LogDebug(__BASE_FILE__ "::i32MemoryCopyRegion:: [D]Splitting-0 Source Block at %x", pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize - i32Overlap);

               // Assign new buffer
               pxMemoryblock->ui32BlockSize -= i32Overlap;

               // Buffer outside of range, create new block
               if ((ui32SourceStartAddress + i32Overlap) >= ui32SourceEndAddress)
               {
                  LogDebug(__BASE_FILE__ "::i32MemoryCopyRegion:: [D]Adding-0 Source Block at %x of %d bytes", ui32SourceStartAddress, i32Overlap);
                  i8Error = i32MemoryAdd(pxMemory, ui32SourceStartAddress, i32Overlap, (pxMemoryblock->pui8Buffer + pxMemoryblock->ui32BlockSize));
               }

               // Copy to destination
               i8Error |= i32MemoryAdd(pxMemory, ui32DestinationStartAddress, i32Overlap, (pxMemoryblock->pui8Buffer + pxMemoryblock->ui32BlockSize));
            }
         }
         else if (pxMemoryblock->ui32BlockAddress < ui32SourceEndAddress)
         {
            i32Overlap = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32SourceEndAddress;
            if (i32Overlap > 0)
            {
               ui32TempSize = (pxMemoryblock->ui32BlockSize - i32Overlap);
            }

            LogDebug(__BASE_FILE__ "::i32MemoryCopyRegion:: [D]Adding-1 Destination Block at %x of %d", pxMemoryblock->ui32BlockAddress + i32Offset, ui32TempSize);
            i8Error = i32MemoryAdd(pxMemory, pxMemoryblock->ui32BlockAddress + i32Offset, ui32TempSize, pxMemoryblock->pui8Buffer);
         }
         else
         {
            pxMemoryblockPrevious = NULL;
         }
      }

      // Get next block
      if (pxMemoryblockPrevious == NULL)
      {
         ui8Done = TRUE;
      }
      else
      {
         pxMemoryblock = pxMemoryblockPrevious;
      }
   }

   return(i8Error);
}

/**************************************************************
* @param pxMemory Pointer to Memory
* @param ui32BlockAddress Block base address
* @param ui32BufferSize Byte Count
* @param rui8Buffer Buffer Pointer
**************************************************************/
int32_t i32MemoryAdd(Memory_t *pxMemory, uint32_t ui32BlockAddress, uint32_t ui32BufferSize, uint8_t const rui8Buffer[])
{
   Memoryblock_t *pxMemoryblock;
   Memoryblock_t *pxMemoryblockTraversee;
   uint32_t       ui32FullBlockAddress = (ui32BlockAddress + pxMemory->ui32BaseAddress);
   int32_t        i32Overlap           = 0;
   int32_t        i32FreeSpace         = 0;
   int32_t        i32Error             = 0;

   if (0 == ui32BufferSize)
   {
      i32Error = -1;
   }

   else if (pxMemory->pxMemoryblockHead == NULL)
   {
      pxMemoryblock = pxMemoryCreateBlock(ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
      i32Error      = i32MemoryInsertBlock(pxMemory, pxMemory->pxMemoryblockHead, pxMemoryblock);
   }
   else
   {
      // Set default to head
      pxMemoryblockTraversee = pxMemory->pxMemoryblockHead;

      // Prepend to Head
      //---------------------------------------------------------------------
      if (ui32FullBlockAddress < pxMemory->pxMemoryblockHead->ui32BlockAddress)
      {
         i32Overlap = (ui32FullBlockAddress + ui32BufferSize) - pxMemory->pxMemoryblockHead->ui32BlockAddress;
         if (i32Overlap > 0)
         {
            ui32BufferSize -= i32Overlap;
         }
         else
         {
            i32Overlap = 0;
         }

         // Prepend Block
         pxMemoryblock = pxMemoryCreateBlock(ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
         i32Error      = i32MemoryInsertBlock(pxMemory, NULL, pxMemoryblock);

         // Reduced block
         rui8Buffer            = &rui8Buffer[ui32BufferSize];
         ui32FullBlockAddress += ui32BufferSize;
         ui32BufferSize        = i32Overlap;
      }

      // Let the loop handle appending
      //---------------------------------------------------------------------
      else if (ui32FullBlockAddress >= pxMemory->pxMemoryblockTail->ui32BlockAddress)
      {
         pxMemoryblockTraversee = pxMemory->pxMemoryblockTail;
      }


      // Searching forward
      // Mova forward until no blocks left
      //-------------------------------------------------
      while (!i32Error && ui32BufferSize > 0)
      {
         // Update Current
         if ((pxMemoryblockTraversee->ui32BlockAddress <= ui32FullBlockAddress) &&
             (ui32FullBlockAddress < (pxMemoryblockTraversee->ui32BlockAddress + pxMemoryblockTraversee->ui32BlockSize)))
         {
            int32_t i32Offset = (ui32FullBlockAddress - pxMemoryblockTraversee->ui32BlockAddress);
            i32FreeSpace = (pxMemoryblockTraversee->ui32BlockSize - i32Offset);
            i32Overlap   = (i32FreeSpace > ui32BufferSize)?ui32BufferSize:i32FreeSpace;
            i32Error     = i32MemoryUpdateBlock(pxMemoryblockTraversee, i32Offset, i32Overlap, rui8Buffer);
         }

         // Update Forward
         else
         {
            //No Next block
            if (pxMemoryblockTraversee->pxMemoryblockNext == NULL)
            {
               i32FreeSpace = ui32BufferSize;
            }
            else
            {
               i32FreeSpace = (pxMemoryblockTraversee->pxMemoryblockNext->ui32BlockAddress - ui32FullBlockAddress);
            }

            //
            if (i32FreeSpace > 0)
            {
               // Limit the size of block
               i32Overlap    = i32FreeSpace > ui32BufferSize?ui32BufferSize:i32FreeSpace;
               pxMemoryblock = pxMemoryCreateBlock(ui32FullBlockAddress, i32Overlap, rui8Buffer);
               i32Error      = i32MemoryInsertBlock(pxMemory, pxMemoryblockTraversee, pxMemoryblock);
            }
            else if (i32FreeSpace == 0)
            {
               // Max copy size is set to available region size
               i32Overlap = (ui32BufferSize > pxMemoryblockTraversee->pxMemoryblockNext->ui32BlockSize)? pxMemoryblockTraversee->pxMemoryblockNext->ui32BlockSize :ui32BufferSize;
               i32Error   = i32MemoryUpdateBlock(pxMemoryblockTraversee->pxMemoryblockNext, 0, i32Overlap, rui8Buffer);
            }
            else
            {
               i32Overlap             = 0;
               pxMemoryblockTraversee = pxMemoryblockTraversee->pxMemoryblockNext;
            }
         }

         // Reduce Buffer
         ui32FullBlockAddress += i32Overlap;
         ui32BufferSize       -= i32Overlap;
         rui8Buffer            = &rui8Buffer[i32Overlap];
      }
   }

   return(i32Error);
}
