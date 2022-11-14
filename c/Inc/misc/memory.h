#ifndef MEMORY_H
#define MEMORY_H

#include "types.h"

/* Public types */
typedef struct memblock_
{
   struct memblock_ *pxMemoryblockNext;
   struct memblock_ *pxMemoryblockPrevious;
   uint32_t          ui32BlockAddress;
   uint32_t          ui32BlockSize;
   uint8_t *         pui8Buffer;
} Memoryblock_t;

typedef struct
{
   uint32_t       ui32BlockCount;
   Memoryblock_t *pxMemoryblockHead;
   Memoryblock_t *pxMemoryblockTail;
}
Memory_t;


/* Public prototypes */
extern int32_t i32MemoryInitialize(Memory_t *pxMemory);
extern int32_t i32MemoryDeinitialize(Memory_t *pxMemory);
extern int32_t i32MemoryPrint(Memory_t *pxMemory);
extern uint32_t ui32MemoryGetTotalSize(Memory_t *pxMemory);
extern int32_t i32MemoryAdd(Memory_t *pxMemory, uint32_t ui32BlockAddress, uint32_t ui32Buffersize, uint8_t const *pui8Buffer);
extern int32_t i32MemoryDeleteRegion(Memory_t *pxMemory, uint32_t ui32RegionStartingAddress, uint32_t ui32RegionEndingAddress);
extern int32_t i32MemoryCompare(Memory_t *pxMemoryOriginal, Memory_t *pxMemorySecondary, uint8_t ui8Freebyte);
extern int32_t i32MemoryCopyRegion(Memory_t *pxMemory, uint32_t ui32SourceAddress, uint32_t ui32DestinationAddress, int32_t i32SizeToCopy);

#endif
