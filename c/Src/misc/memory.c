#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "config.h"
#include "types.h"
#include "assert.h"
#include "misc/memory.h"
#include "misc/helpers.h"



/* Private prototypes */
PROTOTYPE int32_t i32MemoryRemoveBlock(Memory_t *pxMemory, Memoryblock_t *pxMemoryblock);
PROTOTYPE int32_t i32MemoryFreeBlock(Memoryblock_t *pxMemoryblock);
PROTOTYPE int32_t i32MemoryInsertBlock(Memory_t *pxMemory, Memoryblock_t *pxMemoryblockPrevious, Memoryblock_t *pxMemoryblock);
PROTOTYPE int32_t i32MemoryUpdateBlock(Memoryblock_t *pxMemoryblock, uint32_t ui32BufferOffset, uint32_t ui32BufferSize, uint8_t const rui8Buffer[]);
PROTOTYPE Memoryblock_t * pxMemoryAllocateBlock(uint32_t ui32BlockAddress, uint32_t ui32BufferSize, uint8_t const rui8Buffer[]);

/* Private functions */


/*************************************************************
 * @param ui32BlockAddress Block base address
 * @param ui32BufferSize Byte Count
 * @param rui8Buffer Buffer Pointer
 * @return Allocated Memory Block
 **************************************************************/
STATIC Memoryblock_t * pxMemoryAllocateBlock(uint32_t ui32BlockAddress, uint32_t ui32BufferSize, uint8_t const rui8Buffer[])
{
   REQUIRE(rui8Buffer);
   REQUIRE(ui32BufferSize);

   uint8_t *      pui8Buffer    = malloc(ui32BufferSize);
   Memoryblock_t *pxMemoryblock = malloc(sizeof(Memoryblock_t));

   // Continue if buffer was allocated
   if ((ui32BufferSize == 0) || pui8Buffer == NULL || pxMemoryblock == NULL || rui8Buffer == NULL)
   {
      free(pxMemoryblock);
      free(pui8Buffer);
      pxMemoryblock = NULL;
   }

   // Init block
   else
   {
      memcpy(pui8Buffer, rui8Buffer, ui32BufferSize);
      pxMemoryblock->ui32BlockAddress      = ui32BlockAddress;
      pxMemoryblock->ui32BlockSize         = ui32BufferSize;
      pxMemoryblock->pui8Buffer            = pui8Buffer;
      pxMemoryblock->pxMemoryblockNext     = NULL;
      pxMemoryblock->pxMemoryblockPrevious = NULL;
      LogDebug(__BASE_FILE__ "::pxMemoryAllocateBlock:: Allocating [%x]{%d}", pxMemoryblock->ui32BlockAddress, pxMemoryblock->ui32BlockSize);
   }

   return(pxMemoryblock);
}

/*************************************************************
 * @param pxMemoryblock Memoryblock to delete
 * @return     0  OK
 *             x  NOK
 **************************************************************/
STATIC int32_t i32MemoryFreeBlock(Memoryblock_t *pxMemoryblock)
{
   REQUIRE((pxMemoryblock && pxMemoryblock->pui8Buffer));

   int32_t i32Status = -1;
   if (pxMemoryblock && pxMemoryblock->pui8Buffer)
   {
      LogDebug(__BASE_FILE__ "::i32MemoryFreeBlock:: Freeing [%x]{%d}", pxMemoryblock->ui32BlockAddress, pxMemoryblock->ui32BlockSize);
      free(pxMemoryblock->pui8Buffer);
      pxMemoryblock->pui8Buffer = NULL;

      free(pxMemoryblock);
      i32Status = 0;
   }

   return(i32Status);
}

STATIC int32_t i32MemoryInsertBlock(Memory_t *pxMemory, Memoryblock_t *pxMemoryblockPrevious, Memoryblock_t *pxMemoryblock)
{
   REQUIRE(pxMemory);
   REQUIRE(pxMemoryblock);

   int32_t i32Status = 0;

   if (pxMemory == NULL || pxMemoryblock == NULL)
   {
      i32Status = -1;
      LogDebug(__BASE_FILE__ "::i32MemoryInsertBlock:: Error %d", i32Status);
   }
   // Set Head and Tail
   else if (pxMemory->pxMemoryblockHead == NULL)
   {
      pxMemory->pxMemoryblockHead = pxMemoryblock;
      pxMemory->pxMemoryblockTail = pxMemoryblock;
      ++pxMemory->ui32BlockCount;

      LogDebug(__BASE_FILE__ "::i32MemoryInsertBlock:: Set Head/Tail [%x} {%d}", pxMemoryblock->ui32BlockAddress, pxMemoryblock->ui32BlockSize);
   }
   // Connect to next block
   else if (pxMemoryblockPrevious == NULL)
   {
      pxMemory->pxMemoryblockHead->pxMemoryblockPrevious = pxMemoryblock;
      pxMemoryblock->pxMemoryblockNext = pxMemory->pxMemoryblockHead;
      pxMemory->pxMemoryblockHead      = pxMemoryblock;
      LogDebug(__BASE_FILE__ "::i32MemoryInsertBlock:: Prepend Head [%x} {%d}", pxMemoryblock->ui32BlockAddress, pxMemoryblock->ui32BlockSize);
   }
   // Prepend to head
   else
   {
      // Connect forward to base -> current -> base+1
      pxMemoryblock->pxMemoryblockNext         = pxMemoryblockPrevious->pxMemoryblockNext;
      pxMemoryblockPrevious->pxMemoryblockNext = pxMemoryblock;

      // Connect backward base <- current <- base+1
      pxMemoryblock->pxMemoryblockPrevious = pxMemoryblockPrevious;
      if (pxMemoryblock->pxMemoryblockNext != NULL)
      {
         pxMemoryblock->pxMemoryblockNext->pxMemoryblockPrevious = pxMemoryblock;
         LogDebug(__BASE_FILE__ "::i32MemoryInsertBlock:: [%x]{%d}->[%x]{%d}->[%x]{%d]", pxMemoryblockPrevious->ui32BlockAddress, pxMemoryblockPrevious->ui32BlockSize, pxMemoryblock->ui32BlockAddress, pxMemoryblock->ui32BlockSize, pxMemoryblock->pxMemoryblockNext->ui32BlockAddress, pxMemoryblock->pxMemoryblockNext->ui32BlockSize);
      }
      else
      {
         LogDebug(__BASE_FILE__ "::i32MemoryInsertBlock:: [%x]{%d}->[%x]{%d}->[NULL]", pxMemoryblockPrevious->ui32BlockAddress, pxMemoryblockPrevious->ui32BlockSize, pxMemoryblock->ui32BlockAddress, pxMemoryblock->ui32BlockSize);
      }

      // Update tail
      if (pxMemoryblock->ui32BlockAddress > pxMemory->pxMemoryblockTail->ui32BlockAddress)
      {
         pxMemory->pxMemoryblockTail = pxMemoryblock;
         LogDebug(__BASE_FILE__ "::i32MemoryInsertBlock:: Set Tail [%x} {%d}", pxMemoryblock->ui32BlockAddress, pxMemoryblock->ui32BlockSize);
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
STATIC int32_t i32MemoryUpdateBlock(Memoryblock_t *pxMemoryblock, uint32_t ui32BufferOffset, uint32_t ui32BufferSize, uint8_t const rui8Buffer[])
{
   REQUIRE(pxMemoryblock);
   REQUIRE(rui8Buffer);

   int32_t i32Status = 0;
   if (pxMemoryblock == NULL || rui8Buffer == NULL)
   {
      LogError(__BASE_FILE__ "::i32MemoryUpdateBlock:: Error: NULL block");
      i32Status = -1;
   }
   else if ((ui32BufferOffset + ui32BufferSize) <= pxMemoryblock->ui32BlockSize)
   {
      LogDebug(__BASE_FILE__ "::i32MemoryUpdateBlock:: Update block [%x} {%d}", pxMemoryblock->ui32BlockAddress + ui32BufferOffset, ui32BufferSize);
      memcpy(&pxMemoryblock->pui8Buffer[ui32BufferOffset], rui8Buffer, ui32BufferSize);
   }
   else
   {
      LogError(__BASE_FILE__ "::i32MemoryUpdateBlock:: Error: Block [%x] {%d}", pxMemoryblock->ui32BlockAddress + ui32BufferOffset, ui32BufferSize);
      i32Status = -1;
   }

   return(i32Status);
}

/***************************************************************
* @param pxMemory Pointer to Memory
* @param ui32BlockAddress Block base address
* @param ui32BufferSize Byte Count
* @param rui8Buffer Buffer Pointer
***************************************************************/
STATIC int32_t i32MemoryRemoveBlock(Memory_t *pxMemory, Memoryblock_t *pxMemoryblock)
{
   REQUIRE(pxMemory);
   REQUIRE(pxMemoryblock);

   int32_t i32Status = 0;
   if (pxMemoryblock == NULL || pxMemoryblock->pui8Buffer == NULL || !pxMemory->ui32BlockCount)
   {
      i32Status = -1;
      LogError(__BASE_FILE__ "::i32MemoryRemoveBlock:: Error: NULL block");
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


      i32Status = i32MemoryFreeBlock(pxMemoryblock);
      --pxMemory->ui32BlockCount;
   }
   return(i32Status);
}

/***************************************************************
 * @param pxMemory Pointer to Memory
 **************************************************************/
int32_t i32MemoryInitialize(Memory_t *pxMemory)
{
   REQUIRE(pxMemory);
   int32_t i32Error = 0;

   if (pxMemory == NULL)
   {
      i32Error = -1;
   }
   else
   {
      pxMemory->ui32BlockCount    = 0;
      pxMemory->ui32BaseAddress   = 0;
      pxMemory->pxMemoryblockTail = NULL;
      pxMemory->pxMemoryblockHead = NULL;
   }

   return(i32Error);
}

/***************************************************************
 * @param pxMemory Pointer to Memory
 **************************************************************/
int32_t i32MemoryDeinitialize(Memory_t *pxMemory)
{
   REQUIRE(pxMemory);

   int32_t i32Error = 0;
   if (pxMemory == NULL)
   {
      i32Error = 1;
      LogError(__BASE_FILE__ "::i32MemoryDeinitialize:: Memory is NULL");
   }
   else
   {
      Memoryblock_t *pxMemoryblock = pxMemory->pxMemoryblockTail;
      while (!i32Error && pxMemory->ui32BlockCount)
      {
         if (pxMemoryblock == NULL)
         {
            i32Error = -1;
            LogError(__BASE_FILE__ "::i32MemoryDeinitialize:: Error at Count %d", pxMemory->ui32BlockCount);
         }
         else
         {
            Memoryblock_t *pxMemoryblockBackward = pxMemoryblock->pxMemoryblockPrevious;
            i32Error      = i32MemoryRemoveBlock(pxMemory, pxMemoryblock);
            pxMemoryblock = pxMemoryblockBackward;
         }
      }

      // Reset memory
      if (!i32Error)
      {
         pxMemory->ui32BaseAddress   = 0;
         pxMemory->pxMemoryblockTail = NULL;
         pxMemory->pxMemoryblockHead = NULL;
      }
   }


   return(i32Error);
}

/***************************************************************
* @param pxMemory Pointer to Memory
* @return   0  equal
*           x  not equal
***************************************************************/
int32_t i32MemoryCompare(Memory_t *pxMemoryOriginal, Memory_t *pxMemorySecondary, uint8_t ui8Freebyte)
{
   REQUIRE(pxMemoryOriginal);
   REQUIRE(pxMemorySecondary);

   Memoryblock_t *pxMemoryblockOriginal;
   Memoryblock_t *pxMemoryblockSecondary;
   int32_t        i32Error = 0;

   if (pxMemorySecondary == NULL || pxMemoryOriginal == NULL)
   {
      i32Error = -1;
   }
   else
   {
      uint32_t ui32Index1 = 0;
      uint32_t ui32Index2 = 0;
      pxMemoryblockOriginal  = pxMemoryOriginal->pxMemoryblockHead;
      pxMemoryblockSecondary = pxMemorySecondary->pxMemoryblockHead;

      while (!i32Error && pxMemoryblockOriginal != NULL && pxMemoryblockSecondary != NULL)
      {
         // One is lagging behind
         if ((pxMemoryblockOriginal->ui32BlockAddress + ui32Index1) > (pxMemoryblockSecondary->ui32BlockAddress + ui32Index2))
         {
            if (ui8Freebyte != pxMemoryblockSecondary->pui8Buffer[ui32Index2++])
            {
               i32Error = -4;
            }
         }
         // The other is lagging behind
         else if ((pxMemoryblockOriginal->ui32BlockAddress + ui32Index1) < (pxMemoryblockSecondary->ui32BlockAddress + ui32Index2))
         {
            if (ui8Freebyte != pxMemoryblockOriginal->pui8Buffer[ui32Index1++])
            {
               i32Error = -3;
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
            i32Error = -5;
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
      while (!i32Error && pxMemoryblockOriginal != NULL)
      {
         // Switch Original here to next block
         if (ui32Index1 >= pxMemoryblockOriginal->ui32BlockSize)
         {
            pxMemoryblockOriginal = pxMemoryblockOriginal->pxMemoryblockNext;
            ui32Index1            = 0;
         }
         else if (pxMemoryblockOriginal->pui8Buffer[ui32Index1++] != ui8Freebyte)
         {
            i32Error = -6;
         }
      }


      while (!i32Error && pxMemoryblockSecondary != NULL)
      {
         // Switch Original here to next block
         if (ui32Index2 >= pxMemoryblockSecondary->ui32BlockSize)
         {
            pxMemoryblockSecondary = pxMemoryblockSecondary->pxMemoryblockNext;
            ui32Index2             = 0;
         }
         else if (pxMemoryblockSecondary->pui8Buffer[ui32Index2++] != ui8Freebyte)
         {
            i32Error = -7;
         }
      }
   }

   return(i32Error);
}

/***************************************************************
* @param pxMemory Pointer to Memory
* @return Size of Memory
***************************************************************/
uint32_t ui32MemoryGetTotalSize(Memory_t *pxMemory)
{
   REQUIRE(pxMemory);

   uint32_t ui32Size;
   if (pxMemory == NULL || pxMemory->pxMemoryblockHead == NULL)
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
   REQUIRE(pxMemory);

   #define ALIGN    16
   uint32_t       ui32BlockIndex;
   uint32_t       ui32InnerBufferIndex;
   Memoryblock_t *pxMemoryblock;
   int32_t        i32Error = 0;

   if (pxMemory == NULL)
   {
      i32Error = -1;
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

   return(i32Error);
}

/***************************************************************
* @param pxMemory Pointer to Memory
* @param ui32RegionStartingAddress Starting Address
* @param ui32RegionEndingAddress Ending Address
* @return Status
***************************************************************/
int32_t i32MemoryDeleteRegion(Memory_t *pxMemory, uint32_t ui32RegionStartingAddress, uint32_t ui32RegionEndingAddress)
{
   REQUIRE(pxMemory);

   Memoryblock_t *pxMemoryblock;
   Memoryblock_t *pxMemoryblockAwaiting;
   int8_t         i8Error = 0;

   // Free Destination blocks
   //-----------------------------------------
   pxMemoryblock = pxMemory->pxMemoryblockTail;
   while (!i8Error && (pxMemoryblock))
   {
      pxMemoryblockAwaiting = pxMemoryblock->pxMemoryblockPrevious;

      if (ui32RegionEndingAddress < (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) &&
          (pxMemoryblock->ui32BlockAddress < ui32RegionEndingAddress) &&
          (pxMemoryblock->ui32BlockAddress) >= ui32RegionStartingAddress)
      {
         // ||***DEL***||__N__||
         int32_t  i32SpaceN    = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32RegionEndingAddress;
         uint32_t ui32OffsetN  = pxMemoryblock->ui32BlockSize - i32SpaceN;
         uint32_t ui32AddressN = pxMemoryblock->ui32BlockAddress + ui32OffsetN;

         Memoryblock_t *pxMemoryblockn = pxMemoryAllocateBlock(ui32AddressN, i32SpaceN, &pxMemoryblock->pui8Buffer[ui32OffsetN]);

         i8Error |= i32MemoryRemoveBlock(pxMemory, pxMemoryblock);
         i8Error |= i32MemoryInsertBlock(pxMemory, pxMemoryblockAwaiting, pxMemoryblockn);
      }


      if ((pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) <= ui32RegionEndingAddress &&
          ui32RegionStartingAddress <= pxMemoryblock->ui32BlockAddress)
      {
         // ||***DEL***||
         i8Error = i32MemoryRemoveBlock(pxMemory, pxMemoryblock);
      }

      if ((pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) > ui32RegionEndingAddress &&
          (pxMemoryblock->ui32BlockAddress < ui32RegionStartingAddress))
      {
         // ||__P__||***DEL***||_N_||
         uint32_t ui32SpaceP = ui32RegionStartingAddress - pxMemoryblock->ui32BlockAddress;

         uint32_t       ui32OffsetP    = 0;
         uint32_t       ui32AddressP   = pxMemoryblock->ui32BlockAddress + ui32OffsetP;
         Memoryblock_t *pxMemoryblockp = pxMemoryAllocateBlock(ui32AddressP, ui32SpaceP, &pxMemoryblock->pui8Buffer[ui32OffsetP]);

         uint32_t       ui32SpaceN     = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32RegionEndingAddress;
         uint32_t       ui32OffsetN    = (pxMemoryblock->ui32BlockSize) - ui32SpaceN;
         uint32_t       ui32AddressN   = pxMemoryblock->ui32BlockAddress + ui32OffsetN;
         Memoryblock_t *pxMemoryblockn = pxMemoryAllocateBlock(ui32AddressN, ui32SpaceN, &pxMemoryblock->pui8Buffer[ui32OffsetN]);

         i8Error |= i32MemoryRemoveBlock(pxMemory, pxMemoryblock);
         i8Error |= i32MemoryInsertBlock(pxMemory, pxMemoryblockAwaiting, pxMemoryblockp);
         i8Error |= i32MemoryInsertBlock(pxMemory, pxMemoryblockp, pxMemoryblockn);
      }

      // |__P__||****DEL*******||
      if ((pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) <= ui32RegionEndingAddress &&
          (pxMemoryblock->ui32BlockAddress < ui32RegionStartingAddress) &&
          ui32RegionStartingAddress < (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize))
      {
         uint32_t       ui32SpaceP     = ui32RegionStartingAddress - pxMemoryblock->ui32BlockAddress;
         uint32_t       ui32OffsetP    = 0;
         uint32_t       ui32AddressP   = pxMemoryblock->ui32BlockAddress + ui32OffsetP;
         Memoryblock_t *pxMemoryblockp = pxMemoryAllocateBlock(ui32AddressP, ui32SpaceP, &pxMemoryblock->pui8Buffer[ui32OffsetP]);

         //
         i8Error |= i32MemoryRemoveBlock(pxMemory, pxMemoryblock);
         i8Error |= i32MemoryInsertBlock(pxMemory, pxMemoryblockAwaiting, pxMemoryblockp);
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
   REQUIRE(pxMemory && pxMemory->pxMemoryblockHead && pxMemory->pxMemoryblockTail);

   Memoryblock_t *pxMemoryblock;
   Memoryblock_t *pxMemoryblockTemporary;

   uint32_t ui32SourceEndAddress      = ui32SourceStartAddress + i32RegionSize;
   uint32_t ui32DestinationEndAddress = ui32DestinationStartAddress + i32RegionSize;
   int32_t  i32Offset = 0;
   int32_t  i32FreeSize;
   int32_t  i32Overlap;
   int8_t   i8Error = 0;

   // Invalid Pointers
   if (pxMemory == NULL || pxMemory->pxMemoryblockHead == NULL || pxMemory->pxMemoryblockTail == NULL)
   {
      LogDebug(__BASE_FILE__ "::i32MemoryCopyRegion:: Error:Head or Tail NULL");
      i8Error = (-1);
   }
   else
   {
      // Size is overlapping
      i32Offset = ui32DestinationStartAddress - ui32SourceStartAddress;
      i32Offset = i32Offset < 0 ? -i32Offset:i32Offset;

      // Space between source and destination regions is smaller than copy size
      if (0 == i32RegionSize || i32Offset < i32RegionSize)
      {
         LogDebug(__BASE_FILE__ "::i32MemoryCopyRegion:: Error:Regions overlap");
         i8Error = (-2);
      }
      else
      {
         // Free Destination Region
         i8Error = i32MemoryDeleteRegion(pxMemory, ui32DestinationStartAddress, ui32DestinationEndAddress);

         // Copy blocks
         pxMemoryblock = pxMemory->pxMemoryblockHead;
         while (!i8Error && pxMemoryblock)
         {
            // Preserve pointer to next for traversing
            pxMemoryblockTemporary = pxMemoryblock->pxMemoryblockNext;
            i32FreeSize            = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32SourceStartAddress;

            // Whole block
            if (i32FreeSize > 0)
            {
               if (i32FreeSize >= pxMemoryblock->ui32BlockSize)
               {
                  // Whole block
                  //|COPY|
                  if ((pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) <= ui32SourceEndAddress)
                  {
                     i32Offset  = pxMemoryblock->ui32BlockAddress - ui32SourceStartAddress;
                     i32Overlap = pxMemoryblock->ui32BlockSize;
                     i8Error   |= i32MemoryAdd(pxMemory, ui32DestinationStartAddress + i32Offset, i32Overlap, (pxMemoryblock->pui8Buffer));
                  }
                  // Split
                  //|COPY|____|
                  else if (pxMemoryblock->ui32BlockAddress < ui32SourceEndAddress)
                  {
                     i32Offset              = pxMemoryblock->ui32BlockAddress - ui32SourceStartAddress;
                     i32Overlap             = pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize - ui32SourceEndAddress;
                     i8Error               |= i32MemoryAdd(pxMemory, ui32DestinationStartAddress + i32Offset, i32Overlap, (pxMemoryblock->pui8Buffer));
                     pxMemoryblockTemporary = NULL;
                  }
                  else
                  {
                     pxMemoryblockTemporary = NULL;
                  }
               }
               // Part of block
               else
               {
                  // Split
                  //|____|COPY|
                  if ((pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) <= ui32SourceEndAddress)
                  {
                     i32Offset  = ui32SourceStartAddress - pxMemoryblock->ui32BlockAddress;
                     i32Overlap = i32FreeSize;
                     i8Error   |= i32MemoryAdd(pxMemory, ui32DestinationStartAddress, i32Overlap, (pxMemoryblock->pui8Buffer + i32Offset));
                  }
                  // Split
                  //|____|COPY|____|
                  else if (pxMemoryblock->ui32BlockAddress < ui32SourceEndAddress)
                  {
                     i32Offset              = ui32SourceStartAddress - pxMemoryblock->ui32BlockAddress;
                     i32Overlap             = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32SourceEndAddress;
                     i32Overlap             = pxMemoryblock->ui32BlockSize - i32Overlap - i32Offset;
                     i8Error               |= i32MemoryAdd(pxMemory, ui32DestinationStartAddress, i32Overlap, (pxMemoryblock->pui8Buffer + i32Offset));
                     pxMemoryblockTemporary = NULL;
                  }
                  else
                  {
                     //pxMemoryblockTemporary = NULL;
                  }
               }
            }

            pxMemoryblock = pxMemoryblockTemporary;
         }
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
   REQUIRE(pxMemory);
   REQUIRE(ui32BufferSize);

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
      pxMemoryblock = pxMemoryAllocateBlock(ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
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
         pxMemoryblock = pxMemoryAllocateBlock(ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
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
               pxMemoryblock = pxMemoryAllocateBlock(ui32FullBlockAddress, i32Overlap, rui8Buffer);
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
