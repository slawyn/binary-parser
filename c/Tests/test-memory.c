#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "config.h"
#include "types.h"
#include "misc/memory.h"
#include "misc/dump.h"
#include "misc/helpers.h"

/* Includes Unity */
#include "unity_config.h "
#include "unity.h "

#warning Need to override malloc!
#define FB    (0xFE)

PROTOTYPE int32_t i32MemoryRemoveBlock(Memory_t *pxMemory, Memoryblock_t *pxMemoryblock);
PROTOTYPE int32_t i32MemoryFreeBlock(Memoryblock_t *pxMemoryblock);
PROTOTYPE int32_t i32MemoryInsertBlock(Memory_t *pxMemory, Memoryblock_t *pxMemoryblockBase, Memoryblock_t *pxMemoryblock);
PROTOTYPE Memoryblock_t * pxMemoryAllocateBlock(uint32_t ui32BlockAddress, uint32_t ui32BufferSize, uint8_t const rui8Buffer[]);
PROTOTYPE int32_t i32MemoryUpdateBlock(Memoryblock_t *pxMemoryblock, uint32_t ui32BufferOffset, uint32_t ui32BufferSize, uint8_t const rui8Buffer[]);


typedef struct
{
   uint32_t       ui32Address;
   uint32_t       ui32Size;
   uint32_t       ui32aaa;
   uint8_t const *pui8Data;
} TestMemoryStructure_t;

typedef struct
{
   uint32_t ui32SourceAddress;
   uint32_t ui32Address;
   uint32_t ui32Size;
} TestCopyMemory_t;


uint8_t const array_rising[]    = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };
uint8_t const array_falling[]   = { 0xff, 0xee, 0xdd, 0xcc, 0xbb, 0xaa, 0x99, 0x88, 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00 };
uint8_t const array_freebytes[] = { FB, FB, FB, FB, FB, FB, FB, FB, FB, FB, FB, FB, FB, FB, FB, FB, };
uint8_t const array_zeroes[]    = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
uint8_t const arraz_ffs[]       = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };

// Add
uint8_t memory_add_expected0[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };

uint8_t memory_add_expected1[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
                                   0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };

uint8_t memory_add_expected2[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
                                   0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff, FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };

uint8_t memory_add_expected3[] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                   0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff, FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };

uint8_t memory_add_expected4[] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                   0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };

uint8_t memory_add_expected5[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                   0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };

uint8_t memory_add_expected6[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                   0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };

uint8_t memory_add_expected7[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                   0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0xee, 0xff };

uint8_t memory_add_expected8[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                   0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
                                   0xff, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0xee, 0xff };

uint8_t memory_add_expected9[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                                   0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
                                   0xff, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0xee, 0xff };

uint8_t memory_add_expected10[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
                                    0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                                    FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,  FB,    FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                    FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,  FB,    FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                    FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,  FB,    FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                    FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,  FB,    FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                    FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,  FB,    FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                    0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                                    0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
                                    0xff, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0xee, 0xff };

TestMemoryStructure_t const array_add_expected[] = { { 0x100, sizeof(memory_add_expected0),  0, memory_add_expected0  },    //0
                                                     { 0x100, sizeof(memory_add_expected1),  0, memory_add_expected1  },    //1
                                                     { 0x100, sizeof(memory_add_expected2),  0, memory_add_expected2  },    //2
                                                     { 0x100, sizeof(memory_add_expected3),  0, memory_add_expected3  },    //3
                                                     { 0x100, sizeof(memory_add_expected4),  0, memory_add_expected4  },    //4
                                                     {  0xa0, sizeof(memory_add_expected5),  0, memory_add_expected5  },    //5
                                                     {  0xa0, sizeof(memory_add_expected6),  0, memory_add_expected6  },    //6
                                                     {  0xa0, sizeof(memory_add_expected7),  0, memory_add_expected7  },    //7
                                                     {  0xa0, sizeof(memory_add_expected8),  0, memory_add_expected8  },    //8
                                                     {  0xa0, sizeof(memory_add_expected9),  0, memory_add_expected9  },
                                                     {  0x98, sizeof(memory_add_expected10), 0, memory_add_expected10 }, }; //9



TestMemoryStructure_t const array_add_action[] = { { 0x100, 16, 0, array_rising     },   //0
                                                   { 0x108, 16, 0, array_rising     },   //1
                                                   { 0x120, 16, 0, array_rising     },   //2
                                                   { 0x100, 16, 0, array_zeroes     },   //3
                                                   { 0x110, 16, 0, array_zeroes     },   //4
                                                   {  0xa0, 16, 0, array_rising     },   //5
                                                   { 0x117,  1, 0, &array_rising[1] },   //6
                                                   { 0x127,  7, 0, &array_rising[0] },   //7
                                                   { 0x111, 16, 0, arraz_ffs        },   //8
                                                   { 0x100, 16, 0, array_rising     },
                                                   {  0x98, 16, 0, array_rising     } }; //9



uint8_t memory_del_base[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                              0xff, 0xee, 0xdd, 0xcc, 0xbb, 0xaa, 0x99, 0x88, 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00,
                              0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                              0xff, 0xee, 0xdd, 0xcc, 0xbb, 0xaa, 0x99, 0x88, 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00,
                              0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                              0xff, 0xee, 0xdd, 0xcc, 0xbb, 0xaa, 0x99, 0x88, 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00,
                              0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                              0xff, 0xee, 0xdd, 0xcc, 0xbb, 0xaa, 0x99, 0x88, 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00,
                              0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };

uint8_t memory_del_expected0[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   0x00, 0x11, 0x22,   33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                                   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };

uint8_t memory_del_expected1[] = { FB, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, FB,
                                   FB, FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, FB,
                                   FB, FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB, 0x11, 0x22,   33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, FB,
                                   FB, FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, FB,
                                   FB, FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                   FB, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, FB, };
uint8_t memory_del_expected2[] = { 0, 0 };

uint32_t array_del_action0[][2] = { {                16,                32 },
                                    {           16 + 32,           32 + 32 },
                                    {      16 + 32 + 32,      32 + 32 + 32 },
                                    { 16 + 32 + 32 + 32, 32 + 32 + 32 + 32 }, };

uint32_t array_del_action1[][2] = { {       0,       1 }, {       15,       16 },
                                    {  0 + 16,  1 + 16 }, {  15 + 16,  16 + 16 },
                                    {  0 + 32,  1 + 32 }, {  15 + 32,  16 + 32 },
                                    {  0 + 48,  1 + 48 }, {  15 + 48,  16 + 48 },
                                    {  0 + 64,  1 + 64 }, {  15 + 64,  16 + 64 },
                                    {  0 + 80,  1 + 80 }, {  15 + 80,  16 + 80 },
                                    {  0 + 96,  1 + 96 }, {  15 + 96,  16 + 96 },
                                    { 0 + 112, 1 + 112 }, { 15 + 112, 16 + 112 },
                                    { 0 + 128, 1 + 128 }, { 15 + 128, 16 + 128 }, };


/* For Copy Tests */
uint8_t array_copy_base[]  = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };
uint8_t array_copy_test0[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,    //0x60
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0x70
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0x80
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0x90
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0xA0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0xB0
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };  //0xC0

uint8_t array_copy_test1[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,    //0x60
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0x70
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0x80
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0x90
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0xA0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0xB0
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,    //0xC0
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,    //0xD0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0xE0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0xF0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0x100
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0x110
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0x120
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };  //0x130

uint8_t array_copy_test2[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,    //0x60
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0x70
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0x80
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0x90
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0xA0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0xB0
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,    //0xC0
                               0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,    //0xD0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0xE0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0xF0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0x100
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0x110
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB, FB,        //0x120
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };  //0x130

uint8_t array_copy_test3[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,    //0x60
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x70
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x80
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x90
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0xA0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0xB0
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,    //0xC0
                               0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,    //0xD0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0xE0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0xF0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x100
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x110
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x120
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,    //0x130
                               0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff, }; //0x140

uint8_t array_copy_test4[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,    //0x60
                               FB,   0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, FB,      //0x70
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x80
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x90
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0xA0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0xB0
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,    //0xC0
                               0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,    //0xD0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0xE0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0xF0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x100
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x110
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x120
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,    //0x130
                               0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff, }; //0x140

uint8_t array_copy_test5[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,    //0x60
                               FB,   0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, FB,      //0x70
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x80
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x90
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0xA0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0xB0
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,    //0xC0
                               0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,    //0xD0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0xE0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0xF0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,    //0x100
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x110
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x120
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,    //0x130
                               0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff, }; //0x140

uint8_t array_copy_test6[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,    //0x60
                               FB,   0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, FB,      //0x70
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x80
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x90
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0xA0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0xB0
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,    //0xC0
                               0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,    //0xD0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0xE0
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0xF0
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,    //0x100
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x110
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,      //0x120
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,    //0x130
                               0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff, }; //0x140

#define COPY_BASE    0x60
TestMemoryStructure_t array_copy_expected[] = { { COPY_BASE, sizeof(array_copy_test0), 0, array_copy_test0 },
                                                { COPY_BASE, sizeof(array_copy_test1), 0, array_copy_test1 },
                                                { COPY_BASE, sizeof(array_copy_test2), 0, array_copy_test2 },
                                                { COPY_BASE, sizeof(array_copy_test3), 0, array_copy_test3 },
                                                { COPY_BASE, sizeof(array_copy_test4), 0, array_copy_test4 },
                                                { COPY_BASE, sizeof(array_copy_test5), 0, array_copy_test5 },
                                                { COPY_BASE, sizeof(array_copy_test6), 0, array_copy_test6 } };   //0

uint32_t array_copy_action[][3] = { { COPY_BASE,        COPY_BASE + 0x60, 0x10 },
                                    { COPY_BASE,        COPY_BASE + 0x70, 0x70 },
                                    { COPY_BASE,        COPY_BASE + 0x68, 0x10 },
                                    { COPY_BASE + 0x60, COPY_BASE + 0xD0, 0x20 },
                                    { COPY_BASE + 0x01, COPY_BASE + 0x11, 0x0E },
                                    { COPY_BASE + 0x08, COPY_BASE + 0xA8, 0x08 },
                                    { COPY_BASE + 0x00, COPY_BASE + 0xA0, 0x08 } };


/*****************************************************************************
 * @brief Unity Setup and Teardowns
 ******************************************************************************/
void setUp(void)
{
}

void tearDown(void)
{
}

/*****************************************************************************
 * @brief Tests for successful instatiation
 ******************************************************************************/
void test00_MemoryisInitialized()
{
   #define T01_ADDR_01     100
   #define T01_ARRAY_01    array_falling
   #define T01_SIZE_01     sizeof(array_falling)

   Memory_t memory;
   int32_t status = i32MemoryInitialize(&memory);
   TEST_ASSERT(status == 0);

   TEST_ASSERT(memory.pxMemoryblockHead == NULL);
   TEST_ASSERT(memory.pxMemoryblockTail == NULL);
   TEST_ASSERT(memory.ui32BlockCount == 0);

   status = i32MemoryDeinitialize(&memory);
   TEST_ASSERT(status == 0);
   TEST_ASSERT(memory.pxMemoryblockHead == NULL);
   TEST_ASSERT(memory.pxMemoryblockTail == NULL);
   TEST_ASSERT(memory.ui32BlockCount == 0);

   #undef T01_ADDR_01
   #undef T01_ARRAY_01
   #undef T01_SIZE_01
}

/*****************************************************************************
 * @brief Tests for Successfull Memoryblock creation
 ******************************************************************************/
void test01_MemoryBlockIsCreatableAndFreeable()
{
   #define T01_ADDR_01     100
   #define T01_ARRAY_01    array_rising
   #define T01_SIZE_01     10
   #define T01_ADDR_02     101
   #define T01_ARRAY_02    array_rising
   #define T01_SIZE_02     1
   #define T01_ADDR_03     101
   #define T01_ARRAY_03    array_rising
   #define T01_SIZE_03     0
   #define T01_ADDR_04     101
   #define T01_ARRAY_04    NULL
   #define T01_SIZE_04     10

   // 1.
   Memoryblock_t * memory_block1 = pxMemoryAllocateBlock(T01_ADDR_01, T01_SIZE_01, T01_ARRAY_01);
   TEST_ASSERT(memory_block1 != NULL);

   Memoryblock_t *memory_block2 = pxMemoryAllocateBlock(T01_ADDR_02, T01_SIZE_02, T01_ARRAY_02);
   TEST_ASSERT(memory_block2 != NULL);

   Memoryblock_t *memory_block3 = pxMemoryAllocateBlock(T01_ADDR_03, T01_SIZE_03, T01_ARRAY_03);
   TEST_ASSERT(memory_block3 == NULL);

   Memoryblock_t *memory_block4 = pxMemoryAllocateBlock(T01_ADDR_04, T01_SIZE_04, T01_ARRAY_04);
   TEST_ASSERT(memory_block4 == NULL);

   int32_t status = i32MemoryFreeBlock(memory_block1);
   TEST_ASSERT(status == 0);

   status = i32MemoryFreeBlock(memory_block2);
   TEST_ASSERT(status == 0);

   status = i32MemoryFreeBlock(memory_block3);
   TEST_ASSERT(status != 0);

   status = i32MemoryFreeBlock(memory_block4);
   TEST_ASSERT(status != 0);

   #undef T01_ADDR_01
   #undef T01_ARRAY_01
   #undef T01_SIZE_01
   #undef T01_ADDR_02
   #undef T01_ARRAY_02
   #undef T01_SIZE_02
   #undef T01_ADDR_03
   #undef T01_ARRAY_03
   #undef T01_SIZE_03
   #undef T01_ADDR_04
   #undef T01_ARRAY_04
   #undef T01_SIZE_04
}

void test01_1_MemoryblockIsInsertableAndRemovable()
{
   #define T01_01_ADDR_01     100
   #define T01_01_ARRAY_01    array_rising
   #define T01_01_SIZE_01     10

   Memoryblock_t * memory_block1 = pxMemoryAllocateBlock(T01_01_ADDR_01, T01_01_SIZE_01, T01_01_ARRAY_01);
   TEST_ASSERT(memory_block1 != NULL);

   Memoryblock_t *memory_block2 = pxMemoryAllocateBlock(T01_01_ADDR_01, T01_01_SIZE_01, T01_01_ARRAY_01);
   TEST_ASSERT(memory_block2 != NULL);

   int32_t status = i32MemoryInsertBlock(NULL, NULL, NULL);
   TEST_ASSERT(status != 0);

   Memory_t memory;
   status = i32MemoryInitialize(&memory);
   TEST_ASSERT(status == 0);

   status = i32MemoryInsertBlock(&memory, NULL, NULL);
   TEST_ASSERT(status != 0);

   status = i32MemoryInsertBlock(&memory, memory_block1, NULL);
   TEST_ASSERT(status != 0);

   status = i32MemoryInsertBlock(&memory, NULL, NULL);
   TEST_ASSERT(status != 0);

   status = i32MemoryInsertBlock(&memory, NULL, memory_block1);
   TEST_ASSERT(status == 0);

   status = i32MemoryInsertBlock(&memory, memory_block1, memory_block2);
   TEST_ASSERT(status == 0);

   status = i32MemoryRemoveBlock(&memory, memory_block1);
   TEST_ASSERT(status == 0);

   status = i32MemoryRemoveBlock(&memory, memory_block2);
   TEST_ASSERT(status == 0);

   status = i32MemoryDeinitialize(&memory);
   TEST_ASSERT(status == 0);

   #undef T01_01_ADDR_01
   #undef T01_01_ARRAY_01
   #undef T01_01_SIZE_01
}

void test01_2_MemoryblockIsUpdatable()
{
   #define T01_02_ADDR_01     100
   #define T01_02_ARRAY_01    array_rising
   #define T01_02_SIZE_01     10
   #define T01_02_OFF_02      1
   #define T01_02_ARRAY_02    array_falling
   #define T01_02_SIZE_02     9

   Memoryblock_t * memory_block1 = pxMemoryAllocateBlock(T01_02_ADDR_01, T01_02_SIZE_01, T01_02_ARRAY_01);
   TEST_ASSERT(memory_block1 != NULL);

   int32_t status = i32MemoryUpdateBlock(memory_block1, T01_02_OFF_02, T01_02_SIZE_02, T01_02_ARRAY_02);
   TEST_ASSERT(status == 0);

   status = i32MemoryUpdateBlock(memory_block1, T01_02_OFF_02 + 1, T01_02_SIZE_02, T01_02_ARRAY_02);
   TEST_ASSERT(status != 0);

   status = memcmp(&memory_block1->pui8Buffer[T01_02_OFF_02], T01_02_ARRAY_02, T01_02_SIZE_02);
   TEST_ASSERT(status == 0);

   status = i32MemoryUpdateBlock(NULL, T01_02_OFF_02 + 1, T01_02_SIZE_02, T01_02_ARRAY_02);
   TEST_ASSERT(status != 0);

   status = i32MemoryUpdateBlock(memory_block1, T01_02_OFF_02 + 1, T01_02_SIZE_02, NULL);
   TEST_ASSERT(status != 0);

   status = i32MemoryFreeBlock(memory_block1);
   TEST_ASSERT(status == 0);

   #undef T01_02_ADDR_01
   #undef T01_02_ARRAY_01
   #undef T01_02_SIZE_01
   #undef T01_02_OFF_02
   #undef T01_02_ARRAY_02
   #undef T01_02_SIZE_02
}

/*****************************************************************************
 * @brief Tests for failed deinitialization
 ******************************************************************************/
void test02_MemoryHasFailedDeinitialization()
{
   #define T02_ADDR_01     100
   #define T02_ARRAY_01    array_falling
   #define T02_SIZE_01     sizeof(T02_ARRAY_01)
   #define T02_ADDR_02     (T02_ADDR_01 + T02_SIZE_01)
   #define T02_ARRAY_02    array_rising
   #define T02_SIZE_02     sizeof(T02_ARRAY_02)

   Memory_t memory;
   int32_t status = i32MemoryInitialize(&memory);
   TEST_ASSERT(status == 0);

   status = i32MemoryAdd(&memory, T02_ADDR_01, T02_SIZE_01, T02_ARRAY_01);
   TEST_ASSERT(status == 0);

   status = i32MemoryAdd(&memory, T02_ADDR_02, T02_SIZE_02, T02_ARRAY_02);
   TEST_ASSERT(status == 0);

   TEST_ASSERT(memory.pxMemoryblockHead != NULL);
   TEST_ASSERT(memory.pxMemoryblockTail != NULL);
   TEST_ASSERT(memory.ui32BlockCount == 2);

   // Missing Buffer
   // remove memory leak
   free(memory.pxMemoryblockTail->pui8Buffer);
   memory.pxMemoryblockTail->pui8Buffer = NULL;
   status = i32MemoryDeinitialize(&memory);
   TEST_ASSERT(status != 0);
   free(memory.pxMemoryblockTail);
   memory.pxMemoryblockTail = NULL;

   // Missing head
   free(memory.pxMemoryblockHead->pui8Buffer);
   free(memory.pxMemoryblockHead);
   memory.pxMemoryblockHead = NULL;
   status = i32MemoryDeinitialize(&memory);
   TEST_ASSERT(status != 0);

   //
   status = i32MemoryDeinitialize(NULL);
   TEST_ASSERT(status != 0);

   status = i32MemoryInitialize(NULL);
   TEST_ASSERT(status != 0);

   #undef T02_ADDR_01
   #undef T02_ARRAY_01
   #undef T02_SIZE_01
   #undef T02_ADDR_02
   #undef T02_ARRAY_02
   #undef T02_SIZE_02
}

/*****************************************************************************
 * @brief Tests for zero size
 ******************************************************************************/
void test03_MemorySizeIsZero()
{
   Memory_t memory;
   int32_t  status = i32MemoryInitialize(&memory);
   TEST_ASSERT(status == 0);

   uint32_t size = ui32MemoryGetTotalSize(&memory);
   TEST_ASSERT(size == 0);

   size = ui32MemoryGetTotalSize(NULL);
   TEST_ASSERT(size == 0);

   ++memory.ui32BlockCount;

   status = i32MemoryDeinitialize(&memory);
   TEST_ASSERT(status != 0);
}

/*****************************************************************************
 * @brief Tests for size of one block
 ******************************************************************************/
void test04_MemorySizeIsOneBlock()
{
   #define T04_ARRAY_01    array_falling
   #define T04_SIZE_01     sizeof(T04_ARRAY_01)
   #define T04_ADDR_01     0

   Memory_t memory;
   int32_t status = i32MemoryInitialize(&memory);
   TEST_ASSERT(status == 0);

   status = i32MemoryAdd(&memory, T04_ADDR_01, T04_SIZE_01, T04_ARRAY_01);
   TEST_ASSERT(status == 0);

   uint32_t size = ui32MemoryGetTotalSize(&memory);
   TEST_ASSERT(size == T04_SIZE_01);

   status = i32MemoryDeinitialize(&memory);
   TEST_ASSERT(status == 0);

   #undef T04_ARRAY_01
   #undef T04_SIZE_01
   #undef T04_ADDR_01
}

/*****************************************************************************
 * @brief Tests for size of one block
 ******************************************************************************/
void test05_MemorySizeIsTwoBlocks()
{
   #define T05_ARRAY_01    array_falling
   #define T05_SIZE_01     sizeof(T05_ARRAY_01)
   #define T05_ADDR_01     0
   #define T05_ARRAY_02    T05_ARRAY_01
   #define T05_SIZE_02     sizeof(T05_ARRAY_01) / 2
   #define T05_ADDR_02     100
   #define T05_RESULT      (T05_ADDR_02 - T05_ADDR_01 + T05_SIZE_02)

   Memory_t memory;
   int32_t status = i32MemoryInitialize(&memory);
   TEST_ASSERT(status == 0);

   status = i32MemoryAdd(&memory, T05_ADDR_01, T05_SIZE_01, T05_ARRAY_01);
   TEST_ASSERT(status == 0);

   status = i32MemoryAdd(&memory, T05_ADDR_02, T05_SIZE_02, T05_ARRAY_01);
   TEST_ASSERT(status == 0);

   uint32_t size = ui32MemoryGetTotalSize(&memory);
   TEST_ASSERT(size == (T05_RESULT));

   status = i32MemoryDeinitialize(&memory);
   TEST_ASSERT(status == 0);

   #undef T05_ARRAY_01
   #undef T05_SIZE_01
   #undef T05_ADDR_01
   #undef T05_ARRAY_02
   #undef T05_SIZE_02
   #undef T05_ADDR_02
   #undef T05_RESULT
}

/*****************************************************************************
 * @brief Tests for printability of memory
 ******************************************************************************/
void test06_MemoryisPrintable()
{
   #define T06_ARRAY_01    array_falling
   #define T06_SIZE_01     sizeof(T06_ARRAY_01)
   #define T06_ADDR_01     0

   Memory_t memory;
   int32_t status = i32MemoryInitialize(&memory);
   TEST_ASSERT(status == 0);

   status = i32MemoryAdd(&memory, T06_ADDR_01, T06_SIZE_01, T06_ARRAY_01);
   TEST_ASSERT(status == 0);

   status = i32MemoryPrint(&memory);
   TEST_ASSERT(status == 0);

   status = i32MemoryPrint(NULL);
   TEST_ASSERT(status != 0);

   status = i32MemoryDeleteRegion(&memory, T06_ADDR_01, T06_ADDR_01 + T06_SIZE_01);
   TEST_ASSERT(status == 0);

   status = i32MemoryPrint(&memory);
   TEST_ASSERT(status == 0);

   status = i32MemoryDeinitialize(&memory);
   TEST_ASSERT(status == 0);

   #undef T06_ARRAY_01
   #undef T06_SIZE_01
   #undef T06_ADDR_01
}

/*****************************************************************************
 * @brief Tests for printability of memory
 ******************************************************************************/
void test07_MemoryisComparable()
{
   #define T07_ARRAZ_01    array_falling
   #define T07_SIZE_01     sizeof(T07_ARRAZ_01)
   #define T07_ADDR_01     100
   #define T07_ARRAZ_02    array_falling
   #define T07_SIZE_02     sizeof(T07_ARRAZ_02)
   #define T07_ADDR_02     100
   #define T07_ARRAZ_03    array_falling
   #define T07_SIZE_03     sizeof(T07_ARRAZ_03)
   #define T07_ADDR_03     101

   Memory_t memory1;
   Memory_t memory2;
   Memory_t memory3;
   Memory_t memory4;

   int32_t status = i32MemoryInitialize(&memory1);
   TEST_ASSERT(status == 0);

   status = i32MemoryInitialize(&memory2);
   TEST_ASSERT(status == 0);

   status = i32MemoryInitialize(&memory3);
   TEST_ASSERT(status == 0);

   status = i32MemoryInitialize(&memory4);
   TEST_ASSERT(status == 0);

   status = i32MemoryAdd(&memory1, T07_ADDR_01, T07_SIZE_01, T07_ARRAZ_01);
   TEST_ASSERT(status == 0);

   status = i32MemoryAdd(&memory4, T07_ADDR_01, (T07_SIZE_01 - 1), T07_ARRAZ_01);
   TEST_ASSERT(status == 0);

   status = i32MemoryCompare(&memory1, &memory4, FB);
   TEST_ASSERT(status != 0);

   // add ary and unary
   int32_t i = T07_SIZE_02 % 2;
   while (i < T07_SIZE_02)
   {
      status = i32MemoryAdd(&memory2, T07_ADDR_02 + i, 1, &T07_ARRAZ_01[i]);
      TEST_ASSERT(status == 0);

      status = i32MemoryAdd(&memory3, T07_ADDR_03 + i, 1, &T07_ARRAZ_03[i]);
      TEST_ASSERT(status == 0);

      i += 2;
      if (i == T07_SIZE_02)
      {
         i = ((T07_SIZE_02 % 2) + 1) % T07_SIZE_02;
      }
   }
   // equal
   status = i32MemoryCompare(&memory1, &memory2, FB);
   TEST_ASSERT(status == 0);

   // one null
   status = i32MemoryCompare(NULL, &memory2, FB);
   TEST_ASSERT(status != 0);

   status = i32MemoryCompare(&memory1, NULL, FB);
   TEST_ASSERT(status != 0);

   // both null
   status = i32MemoryCompare(NULL, NULL, FB);
   TEST_ASSERT(status != 0);

   // shifted forward
   status = i32MemoryCompare(&memory2, &memory3, FB);
   TEST_ASSERT(status != 0);

   // shifted backward
   status = i32MemoryCompare(&memory3, &memory2, FB);
   TEST_ASSERT(status != 0);

   // one byte difference
   status = i32MemoryAdd(&memory2, T07_ADDR_02 + 1, 1, T07_ARRAZ_01);
   TEST_ASSERT(status == 0);

   status = i32MemoryCompare(&memory1, &memory2, FB);
   TEST_ASSERT(status != 0);

   status = i32MemoryDeinitialize(&memory1);
   TEST_ASSERT(status == 0);

   status = i32MemoryDeinitialize(&memory2);
   TEST_ASSERT(status == 0);

   status = i32MemoryDeinitialize(&memory3);
   TEST_ASSERT(status == 0);

   status = i32MemoryDeinitialize(&memory4);
   TEST_ASSERT(status == 0);

   #undef T07_ARRAZ_01
   #undef T07_SIZE_01
   #undef T07_ADDR_01
   #undef T07_ARRAZ_02
   #undef T07_SIZE_02
   #undef T07_ADDR_02
   #undef T07_ARRAZ_03
   #undef T07_SIZE_03
   #undef T07_ADDR_03
}

/*****************************************************************************
 * @brief Tests for printability of memory
 ******************************************************************************/
void test08_MemoryHasGaps()
{
   #define T08_ARRAY_01    array_falling
   #define T08_SIZE_01     sizeof(T08_ARRAY_01)
   #define T08_ARRAY_02    array_freebytes
   #define T08_SIZE_02     sizeof(T08_ARRAY_02)
   #define T08_ARRAY_03    array_falling
   #define T08_SIZE_03     1
   #define T08_ADDR_01     0xa0
   #define T08_ADDR_02     (T08_ADDR_01 + T08_SIZE_02)
   #define T08_ADDR_03     (T08_ADDR_01 + T08_SIZE_02 / 3)
   #define T08_ADDR_04     (T08_ADDR_02 + T08_SIZE_02) - 1

   Memory_t memory1;
   Memory_t memory2;

   // Init
   int32_t status = i32MemoryInitialize(&memory1);
   TEST_ASSERT(status == 0);

   status = i32MemoryInitialize(&memory2);
   TEST_ASSERT(status == 0);

   // Prefill with free bytes and place data into the middle
   status = i32MemoryAdd(&memory1, T08_ADDR_01, T08_SIZE_02, T08_ARRAY_02);
   TEST_ASSERT(status == 0);
   status = i32MemoryAdd(&memory1, T08_ADDR_02, T08_SIZE_02, T08_ARRAY_02);
   TEST_ASSERT(status == 0);
   status = i32MemoryAdd(&memory1, T08_ADDR_03, T08_SIZE_01, T08_ARRAY_01);
   TEST_ASSERT(status == 0);

   // Just place data
   status = i32MemoryAdd(&memory2, T08_ADDR_03, T08_SIZE_01, T08_ARRAY_01);
   TEST_ASSERT(status == 0);

   // Should be equal
   status = i32MemoryCompare(&memory1, &memory2, FB);
   TEST_ASSERT(status == 0);
   status = i32MemoryCompare(&memory2, &memory1, FB);
   TEST_ASSERT(status == 0);

   // Replace last byte by non-free byte value
   status = i32MemoryAdd(&memory1, T08_ADDR_04, T08_SIZE_03, T08_ARRAY_03);
   TEST_ASSERT(status == 0);
   status = i32MemoryCompare(&memory2, &memory1, FB);
   TEST_ASSERT(status != 0);
   status = i32MemoryCompare(&memory1, &memory2, FB);
   TEST_ASSERT(status != 0);

   // Same changes, should be equal
   status = i32MemoryAdd(&memory2, T08_ADDR_04, T08_SIZE_03, T08_ARRAY_03);
   TEST_ASSERT(status == 0);
   status = i32MemoryCompare(&memory1, &memory2, FB);
   TEST_ASSERT(status == 0);

   // Replace first byte by non-free byte value
   status = i32MemoryAdd(&memory1, T08_ADDR_01, T08_SIZE_03, T08_ARRAY_03);
   TEST_ASSERT(status == 0);
   status = i32MemoryCompare(&memory1, &memory2, FB);
   TEST_ASSERT(status != 0);
   status = i32MemoryCompare(&memory2, &memory1, FB);
   TEST_ASSERT(status != 0);

   status = i32MemoryAdd(&memory2, T08_ADDR_01, T08_SIZE_03, T08_ARRAY_03);
   TEST_ASSERT(status == 0);

   status = i32MemoryCompare(&memory2, &memory1, FB);
   TEST_ASSERT(status == 0);

   // Deinit
   status = i32MemoryDeinitialize(&memory1);
   TEST_ASSERT(status == 0);
   status = i32MemoryDeinitialize(&memory2);
   TEST_ASSERT(status == 0);

   #undef T08_ARRAY_01
   #undef T08_SIZE_01
   #undef T08_ARRAY_02
   #undef T08_SIZE_02
   #undef T08_ARRAY_03
   #undef T08_SIZE_03
   #undef T08_ADDR_01
   #undef T08_ADDR_02
   #undef T08_ADDR_03
   #undef T08_ADDR_04
}

/*****************************************************************************
 * @brief Tests for adding to memory
 ******************************************************************************/
void test09_MemoryAddTestsAreOkay()
{
   Memory_t memoryUnderTest;
   Memory_t memoryExpected;

   int32_t status = i32MemoryInitialize(&memoryUnderTest);
   TEST_ASSERT(status == 0);

   // zero size
   status = i32MemoryAdd(&memoryUnderTest, COPY_BASE, 0, array_copy_base);
   TEST_ASSERT(status != 0);

   for (uint32_t i = 0; i < SIZEOF(array_add_action); ++i)
   {
      status = i32MemoryAdd(&memoryUnderTest, array_add_action[i].ui32Address, array_add_action[i].ui32Size, array_add_action[i].pui8Data);
      TEST_ASSERT(status == 0);

      status = i32MemoryInitialize(&memoryExpected);
      TEST_ASSERT(status == 0);

      status = i32MemoryAdd(&memoryExpected, array_add_expected[i].ui32Address, array_add_expected[i].ui32Size, array_add_expected[i].pui8Data);
      TEST_ASSERT(status == 0);

      status = i32MemoryCompare(&memoryUnderTest, &memoryExpected, FB);
      TEST_ASSERT(status == 0);

      status = i32MemoryDeinitialize(&memoryExpected);
      TEST_ASSERT(status == 0);
   }

   // NULL pointer to buffer
   status = i32MemoryAdd(&memoryUnderTest, COPY_BASE, 0, NULL);
   TEST_ASSERT(status != 0);

   i32MemoryDeinitialize(&memoryUnderTest);
}

void test10_MemoryDeleteTestsAreOkay()
{
   Memory_t memoryUnderTest;
   Memory_t memoryExpected;

   int32_t status = i32MemoryInitialize(&memoryUnderTest);
   TEST_ASSERT(status == 0);

   status = i32MemoryAdd(&memoryUnderTest, 0, sizeof(memory_del_base), memory_del_base);
   TEST_ASSERT(status == 0);

   // 1st
   for (int32_t i = 0; i < SIZEOF(array_del_action0); ++i)
   {
      status = i32MemoryDeleteRegion(&memoryUnderTest, array_del_action0[i][0], array_del_action0[i][1]);
      TEST_ASSERT(status == 0);
   }

   status = i32MemoryInitialize(&memoryExpected);
   TEST_ASSERT(status == 0);
   status = i32MemoryAdd(&memoryExpected, 0, sizeof(memory_del_expected0), memory_del_expected0);
   TEST_ASSERT(status == 0);
   status = i32MemoryDeleteRegion(&memoryExpected, 0, sizeof(memory_del_expected0));
   TEST_ASSERT(status == 0);

   // 2nd
   for (int32_t i = 0; i < SIZEOF(array_del_action1); ++i)
   {
      status = i32MemoryDeleteRegion(&memoryUnderTest, array_del_action1[i][0], array_del_action1[i][1]);
      TEST_ASSERT(status == 0);
   }
   status = i32MemoryInitialize(&memoryExpected);
   TEST_ASSERT(status == 0);
   status = i32MemoryAdd(&memoryExpected, 0, sizeof(memory_del_expected1), memory_del_expected1);
   TEST_ASSERT(status == 0);
   status = i32MemoryDeleteRegion(&memoryExpected, 0, sizeof(memory_del_expected1));
   TEST_ASSERT(status == 0);


   status = i32MemoryCompare(&memoryUnderTest, &memoryExpected, FB);
   TEST_ASSERT(status != 0);
   status = i32MemoryDeinitialize(&memoryExpected);
   TEST_ASSERT(status == 0);
}

void test11_MemoryCopyTestAreOkay()
{
   Memory_t memoryUnderTest;
   Memory_t memoryExpected;

   int32_t status = i32MemoryInitialize(&memoryUnderTest);
   TEST_ASSERT(status == 0);

   status = i32MemoryAdd(&memoryUnderTest, COPY_BASE, sizeof(array_copy_base), array_copy_base);
   TEST_ASSERT(status == 0);


   for (uint32_t i = 0; i < SIZEOF(array_copy_action); ++i)
   {
      status = i32MemoryCopyRegion(&memoryUnderTest, array_copy_action[i][0], array_copy_action[i][1], array_copy_action[i][2]);
      TEST_ASSERT(status == 0);

      status = i32MemoryInitialize(&memoryExpected);
      TEST_ASSERT(status == 0);

      status = i32MemoryAdd(&memoryExpected, array_copy_expected[i].ui32Address, array_copy_expected[i].ui32Size, array_copy_expected[i].pui8Data);
      TEST_ASSERT(status == 0);

      status = i32MemoryCompare(&memoryUnderTest, &memoryExpected, FB);
      TEST_ASSERT(status == 0);

      status = i32MemoryDeinitialize(&memoryExpected);
      TEST_ASSERT(status == 0);
   }

   status = i32MemoryDeinitialize(&memoryUnderTest);
   TEST_ASSERT(status == 0);

   //
   status = i32MemoryInitialize(&memoryUnderTest);
   TEST_ASSERT(status == 0);

   // NULL check
   status = i32MemoryCopyRegion(NULL, 0, 1, 1);
   TEST_ASSERT(status != 0);

   // Head Tail
   status = i32MemoryCopyRegion(&memoryUnderTest, 0, 100, 1);
   TEST_ASSERT(status != 0);

   // Fill
   status = i32MemoryAdd(&memoryUnderTest, COPY_BASE, sizeof(array_copy_base), array_copy_base);
   TEST_ASSERT(status == 0);

   // zero Size
   status = i32MemoryCopyRegion(&memoryUnderTest, COPY_BASE, COPY_BASE + 1, 2);
   TEST_ASSERT(status != 0);

   // zero Size
   status = i32MemoryCopyRegion(&memoryUnderTest, COPY_BASE, COPY_BASE + 1, 0);
   TEST_ASSERT(status != 0);

   // Normal Size
   status = i32MemoryCopyRegion(&memoryUnderTest, COPY_BASE, COPY_BASE + 1, 1);
   TEST_ASSERT(status == 0);

   status = i32MemoryDeinitialize(&memoryUnderTest);
   TEST_ASSERT(status == 0);
}

/*****************************************************************************
 * @param argc argument count
 * @param argv string arguments
 ******************************************************************************/
int main(int argc, char *argv[])
{
   UnityBegin(__BASE_FILE__);
   RUN_TEST(test00_MemoryisInitialized, 0);
   RUN_TEST(test01_MemoryBlockIsCreatableAndFreeable, 0);
   RUN_TEST(test01_1_MemoryblockIsInsertableAndRemovable, 0);
   RUN_TEST(test01_2_MemoryblockIsUpdatable, 0);
   RUN_TEST(test02_MemoryHasFailedDeinitialization, 0);
   RUN_TEST(test03_MemorySizeIsZero, 0);
   RUN_TEST(test04_MemorySizeIsOneBlock, 0);
   RUN_TEST(test05_MemorySizeIsTwoBlocks, 0);
   RUN_TEST(test06_MemoryisPrintable, 0);
   RUN_TEST(test07_MemoryisComparable, 0);
   RUN_TEST(test08_MemoryHasGaps, 0);
   RUN_TEST(test09_MemoryAddTestsAreOkay, 0);
   RUN_TEST(test10_MemoryDeleteTestsAreOkay, 0);
   RUN_TEST(test11_MemoryCopyTestAreOkay, 0);
   return(UnityEnd());
}
