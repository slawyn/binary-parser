#ifndef MEMORY_H
#define MEMORY_H


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
   uint32_t       ui32BaseAddress;
   Memoryblock_t *pxMemoryblockHead;
   Memoryblock_t *pxMemoryblockTail;
}
Memory_t;


extern void vMemoryInitialize(Memory_t *pxMemory);
int32_t i32MemoryDeinitialize(Memory_t *pxMemory);
extern int32_t i32MemoryPrint(Memory_t *pxMemory);
extern uint32_t ui32MemoryGetTotalSize(Memory_t *pxMemory);
extern int32_t i32MemoryAdd(Memory_t *pxMemory, uint32_t ui32BlockAddress, uint32_t ui32Buffersize, uint8_t const *pui8Buffer);
extern int32_t i32MemoryDeleteRegion(Memory_t *pxMemory, uint32_t ui32RegionStartingAddress, uint32_t ui32RegionEndingAddress);
extern int32_t i32MemoryCopyRegion(Memory_t *pxMemory, uint32_t ui32SourceAddress, uint32_t ui32DestinationAddress, int32_t i32SizeToCopy);

#endif
