#ifndef MEMORY_H
#define MEMORY_H


typedef struct
{
   void *   pxMemoryblockNext;
   uint32_t ui32BlockAddress;
   uint32_t ui32BlockSize;
   uint8_t *pui8Buffer;
} Memoryblock_t;

typedef struct
{
   uint32_t       ui32BlockCount;
   uint32_t       ui32BaseAddress;
   Memoryblock_t *pxMemoryblockHead;
   Memoryblock_t *pxMemoryblockLast;
}
Memory_t;


extern void vMemoryInit(Memory_t *pxMemory);
extern void vMemoryPrint(Memory_t *pxMemory);
extern int32_t i32MemoryblockInit(Memory_t *pxMemory, uint32_t ui32BlockAddress, uint32_t ui32Buffersize, uint8_t *pui8Buffer);

#endif
