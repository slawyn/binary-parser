/*=======Test Runner Used To Run Each Test Below=====*/
#define RUN_TEST(TestFunc, TestLineNum)          \
   {                                             \
      Unity.CurrentTestName       = #TestFunc;   \
      Unity.CurrentTestLineNumber = TestLineNum; \
      Unity.NumberOfTests++;                     \
      if (TEST_PROTECT())                        \
      {                                          \
         setUp();                                \
         TestFunc();                             \
      }                                          \
      if (TEST_PROTECT())                        \
      {                                          \
         tearDown();                             \
      }                                          \
      UnityConcludeTest();                       \
   }


#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "config.h"
#include "types.h"
#include "misc/memory.h"
#include "misc/file.h"
#include "misc/helpers.h"
#include "misc/dump.h"
#include "misc/memory-converter.h"

/* Unity */
#include "unity_config.h "
#include "unity.h "



typedef struct
{
   uint32_t ui32DestinationAddress;
   uint32_t ui32Size;
   uint8_t *pui8Data;
} TestAddMemory_t;

typedef struct
{
   uint32_t ui32SourceAddress;
   uint32_t ui32DestinationAddress;
   uint32_t ui32Size;
} TestCopyMemory_t;

#define FB    (0xFE)

uint8_t const array_rising[]    = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };
uint8_t const array_falling[]   = { 0xff, 0xee, 0xdd, 0xcc, 0xbb, 0xaa, 0x99, 0x88, 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00 };
uint8_t const array_freebytes[] = { FB, FB, FB, FB, FB, FB, FB, FB, FB, FB, FB, FB, FB, FB, FB, FB, };

// Add
uint8_t rui8DumpAddTest0[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };

uint8_t rui8DumpAddTest1[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
                               0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };

uint8_t rui8DumpAddTest2[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
                               0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff, FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };

uint8_t rui8DumpAddTest3[] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                               0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff, FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };

uint8_t rui8DumpAddTest4[] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                               0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };

uint8_t rui8DumpAddTest5[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                               0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };

uint8_t rui8DumpAddTest6[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                               0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };

uint8_t rui8DumpAddTest7[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                               0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0xee, 0xff };

uint8_t rui8DumpAddTest8[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                               0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
                               0xff, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0xee, 0xff };

uint8_t rui8DumpAddTest9[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                               0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                               0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
                               0xff, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0xee, 0xff };

Dump_t rxDumpAddExpected[] = { { 0x100, sizeof(rui8DumpAddTest0), 0, rui8DumpAddTest0 },    //0
                               { 0x100, sizeof(rui8DumpAddTest1), 0, rui8DumpAddTest1 },    //1
                               { 0x100, sizeof(rui8DumpAddTest2), 0, rui8DumpAddTest2 },    //2
                               { 0x100, sizeof(rui8DumpAddTest3), 0, rui8DumpAddTest3 },    //3
                               { 0x100, sizeof(rui8DumpAddTest4), 0, rui8DumpAddTest4 },    //4
                               {  0xa0, sizeof(rui8DumpAddTest5), 0, rui8DumpAddTest5 },    //5
                               {  0xa0, sizeof(rui8DumpAddTest6), 0, rui8DumpAddTest6 },    //6
                               {  0xa0, sizeof(rui8DumpAddTest7), 0, rui8DumpAddTest7 },    //7
                               {  0xa0, sizeof(rui8DumpAddTest8), 0, rui8DumpAddTest8 },    //8
                               {  0xa0, sizeof(rui8DumpAddTest9), 0, rui8DumpAddTest9 }, }; //9

uint8_t rui8TestArray[]                  = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };
uint8_t rui8TestArrayZeroes[]            = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
uint8_t rui8TestArrayFfs[]               = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };
const TestAddMemory_t rxMemoryAddTests[] = { { 0x100, 16, rui8TestArray       },   //0
                                             { 0x108, 16, rui8TestArray       },   //1
                                             { 0x120, 16, rui8TestArray       },   //2
                                             { 0x100, 16, rui8TestArrayZeroes },   //3
                                             { 0x110, 16, rui8TestArrayZeroes },   //4
                                             {  0xa0, 16, rui8TestArray       },   //5
                                             { 0x117,  1, &rui8TestArray[1]   },   //6
                                             { 0x127,  7, &rui8TestArray[0]   },   //7
                                             { 0x111, 16, rui8TestArrayFfs    },   //8
                                             { 0x100, 16, rui8TestArray       } }; //9
// Copy
uint8_t rui8DumpCopyTest0[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                                FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,   FB,
                                0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                                0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                                0xff, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0xee, 0xff };

TestCopyMemory_t rxMemoryCopyTests[]  = { { 0x100, 0x110, 15 } };
Dump_t           rxDumpCopyExpected[] = { { 0xa0, sizeof(rui8DumpCopyTest0), 0, rui8DumpCopyTest0 } }; //0


Dump_t *rpxDumpTest[2];

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
void test01_MemoryisInitialized()
{
   #define T01_ADDR_01     100
   #define T01_ARRAY_01    array_falling
   #define T01_SIZE_01     sizeof(array_falling)

   Memory_t memory;
   vMemoryInitialize(&memory);

   TEST_ASSERT(memory.pxMemoryblockHead == NULL);
   TEST_ASSERT(memory.pxMemoryblockTail == NULL);
   TEST_ASSERT(memory.ui32BaseAddress == 0);
   TEST_ASSERT(memory.ui32BlockCount == 0);

   int32_t i32statusadd1 = i32MemoryAdd(&memory, T01_ADDR_01, T01_SIZE_01, T01_ARRAY_01);
   TEST_ASSERT(i32statusadd1 == 0);
   TEST_ASSERT(memory.pxMemoryblockHead != NULL);
   TEST_ASSERT(memory.pxMemoryblockTail != NULL);
   TEST_ASSERT(memory.pxMemoryblockHead == memory.pxMemoryblockHead);
   TEST_ASSERT(memory.ui32BaseAddress == 0);
   TEST_ASSERT(memory.ui32BlockCount == 1);

   int32_t i32status = i32MemoryDeinitialize(&memory);
   TEST_ASSERT(i32status == 0);
   TEST_ASSERT(memory.pxMemoryblockHead == NULL);
   TEST_ASSERT(memory.pxMemoryblockTail == NULL);
   TEST_ASSERT(memory.ui32BaseAddress == 0);
   TEST_ASSERT(memory.ui32BlockCount == 0);

   #undef T01_ADDR_01
   #undef T01_ARRAY_01
   #undef T01_SIZE_01
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
   vMemoryInitialize(&memory);


   int32_t i32statusadd1 = i32MemoryAdd(&memory, T02_ADDR_01, T02_SIZE_01, T02_ARRAY_01);
   TEST_ASSERT(i32statusadd1 == 0);

   int32_t i32statusadd2 = i32MemoryAdd(&memory, T02_ADDR_02, T02_SIZE_02, T02_ARRAY_02);
   TEST_ASSERT(i32statusadd2 == 0);


   TEST_ASSERT(memory.pxMemoryblockHead != NULL);
   TEST_ASSERT(memory.pxMemoryblockTail != NULL);
   TEST_ASSERT(memory.ui32BaseAddress == 0);
   TEST_ASSERT(memory.ui32BlockCount == 2);



   // Missing Buffer
   // remove memory leak
   free(memory.pxMemoryblockTail->pui8Buffer);
   memory.pxMemoryblockTail->pui8Buffer = NULL;
   int32_t i32status1 = i32MemoryDeinitialize(&memory);
   TEST_ASSERT(i32status1 != 0);
   free(memory.pxMemoryblockTail);
   memory.pxMemoryblockTail = NULL;


   // Missing head
   free(memory.pxMemoryblockHead->pui8Buffer);
   free(memory.pxMemoryblockHead);
   memory.pxMemoryblockHead = NULL;
   int32_t i32status2 = i32MemoryDeinitialize(&memory);
   TEST_ASSERT(i32status2 != 0);

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
   vMemoryInitialize(&memory);

   uint32_t size = ui32MemoryGetTotalSize(&memory);
   TEST_ASSERT(size == 0);

   ++memory.ui32BlockCount;

   int32_t i32status = i32MemoryDeinitialize(&memory);
   TEST_ASSERT(i32status != 0);
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
   vMemoryInitialize(&memory);

   int32_t status_add = i32MemoryAdd(&memory, T04_ADDR_01, T04_SIZE_01, T04_ARRAY_01);
   TEST_ASSERT(status_add == 0);

   uint32_t size = ui32MemoryGetTotalSize(&memory);
   TEST_ASSERT(size == T04_SIZE_01);

   int32_t i32status = i32MemoryDeinitialize(&memory);
   TEST_ASSERT(i32status == 0);

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
   vMemoryInitialize(&memory);

   int32_t status_add = i32MemoryAdd(&memory, T05_ADDR_01, T05_SIZE_01, T05_ARRAY_01);
   TEST_ASSERT(status_add == 0);

   int32_t status_add2 = i32MemoryAdd(&memory, T05_ADDR_02, T05_SIZE_02, T05_ARRAY_01);
   TEST_ASSERT(status_add2 == 0);

   uint32_t size = ui32MemoryGetTotalSize(&memory);
   TEST_ASSERT(size == (T05_RESULT));

   int32_t i32status = i32MemoryDeinitialize(&memory);
   TEST_ASSERT(i32status == 0);

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
   vMemoryInitialize(&memory);

   int32_t status_add = i32MemoryAdd(&memory, T06_ADDR_01, T06_SIZE_01, T06_ARRAY_01);
   TEST_ASSERT(status_add == 0);

   int32_t status_print1 = i32MemoryPrint(&memory);
   TEST_ASSERT(status_print1 == 0);

   int32_t status_print2 = i32MemoryPrint(NULL);
   TEST_ASSERT(status_print2 != 0);

   int32_t status_del = i32MemoryDeleteRegion(&memory, T06_ADDR_01, T06_ADDR_01 + T06_SIZE_01);
   TEST_ASSERT(status_del == 0);

   int32_t status_print3 = i32MemoryPrint(&memory);
   TEST_ASSERT(status_print3 == 0);

   int32_t i32status = i32MemoryDeinitialize(&memory);
   TEST_ASSERT(i32status == 0);

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

   #define T07_ARRAZ_02    T07_ARRAZ_01
   #define T07_SIZE_02     sizeof(T07_ARRAZ_02)
   #define T07_ADDR_02     100

   #define T07_ARRAZ_03    T07_ARRAZ_01
   #define T07_SIZE_03     sizeof(T07_ARRAZ_03)
   #define T07_ADDR_03     101

   Memory_t memory1;
   Memory_t memory2;
   Memory_t memory3;
   Memory_t memory4;

   vMemoryInitialize(&memory1);
   vMemoryInitialize(&memory2);
   vMemoryInitialize(&memory3);
   vMemoryInitialize(&memory4);

   int32_t status_add = i32MemoryAdd(&memory1, T07_ADDR_01, T07_SIZE_01, T07_ARRAZ_01);
   TEST_ASSERT(status_add == 0);

   int32_t status_add2 = i32MemoryAdd(&memory4, T07_ADDR_01, (T07_SIZE_01 - 1), T07_ARRAZ_01);
   TEST_ASSERT(status_add2 == 0);

   int32_t i32Status_comp0 = i32MemoryCompare(&memory1, &memory4, FB);
   TEST_ASSERT(i32Status_comp0 != 0);

   // add ary and unary
   int32_t i = T07_SIZE_02 % 2;
   while (i < T07_SIZE_02)
   {
      int32_t status_add = i32MemoryAdd(&memory2, T07_ADDR_02 + i, 1, &T07_ARRAZ_01[i]);
      TEST_ASSERT(status_add == 0);

      int32_t status_add2 = i32MemoryAdd(&memory3, T07_ADDR_03 + i, 1, &T07_ARRAZ_03[i]);
      TEST_ASSERT(status_add2 == 0);

      i += 2;
      if (i == T07_SIZE_02)
      {
         i = ((T07_SIZE_02 % 2) + 1) % T07_SIZE_02;
      }
   }

   int32_t i32Status_comp1 = i32MemoryCompare(&memory1, &memory2, FB);
   TEST_ASSERT(i32Status_comp1 == 0);

   // NULL Checks
   int32_t i32Status_comp2 = i32MemoryCompare(NULL, &memory2, FB);
   TEST_ASSERT(i32Status_comp2 != 0);

   int32_t i32Status_comp3 = i32MemoryCompare(&memory1, NULL, FB);
   TEST_ASSERT(i32Status_comp3 != 0);

   int32_t i32Status_comp4 = i32MemoryCompare(NULL, NULL, FB);
   TEST_ASSERT(i32Status_comp4 != 0);

   int32_t i32Status_comp5 = i32MemoryCompare(&memory2, &memory3, FB);
   TEST_ASSERT(i32Status_comp5 != 0);

   int32_t i32status1 = i32MemoryDeinitialize(&memory1);
   TEST_ASSERT(i32status1 == 0);

   int32_t i32status2 = i32MemoryDeinitialize(&memory2);
   TEST_ASSERT(i32status2 == 0);

   int32_t i32status3 = i32MemoryDeinitialize(&memory3);
   TEST_ASSERT(i32status3 == 0);

   int32_t i32status4 = i32MemoryDeinitialize(&memory4);
   TEST_ASSERT(i32status4 == 0);

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
   #define T08_SIZE_01     sizeof(T08_SIZE_01)
   #define T08_ARRAY_02    array_freebytes
   #define T08_SIZE_02     sizeof(T08_ARRAY_02)



   #undef T08_ARRAY_01
   #undef T08_SIZE_01
   #undef T08_ARRAY_02
   #undef T08_SIZE_02
}

/*****************************************************************************
 * @brief Tests for successful comparison
 ******************************************************************************/
void test0x_MemoryisGeneratingEqualDumps()
{
   uint8_t  freebyte = 0xAA;
   Memory_t memory;
   vMemoryInitialize(&memory);


   Dump_t *dump = pxConvertMemoryToDump(&memory, freebyte);
}

void othertest()
{
   Memory_t xMemory;
   uint8_t  ui8Error = FALSE;

   vMemoryInitialize(&xMemory);

// Add test
//------------------------------------------------------------------------------------------------------
   for (uint32_t ui32LoopIndex = 0; ui32LoopIndex < SIZEOF(rxMemoryAddTests) && !ui8Error; ++ui32LoopIndex)
   {
      LogDebug("main ::vTestMemory: Test - Add[% d] : Writing % d bytes at % x ", ui32LoopIndex, rxMemoryAddTests[ui32LoopIndex].ui32Size, rxMemoryAddTests[ui32LoopIndex].ui32DestinationAddress);
      i32MemoryAdd(&xMemory, rxMemoryAddTests[ui32LoopIndex].ui32DestinationAddress, rxMemoryAddTests[ui32LoopIndex].ui32Size, rxMemoryAddTests[ui32LoopIndex].pui8Data);

      // Generate Dump
      Dump_t *pxDump = pxConvertMemoryToDump(&xMemory, FB);
      if (i32DumpCompare(&rxDumpAddExpected[ui32LoopIndex], pxDump))
      {
         ui8Error = TRUE;
      }

      //
      if (ui8Error)
      {
         LogDebug("main ::vTestMemory: Test - Add[% d] NOK !", ui32LoopIndex);
      }
      else
      {
         LogDebug("main ::vTestMemory: Test - Add[% d] OK !", ui32LoopIndex);
      }

      i32MemoryPrint(&xMemory);
   }

// Copy test
//------------------------------------------------------------------------------------------------------
   for (uint32_t ui32LoopIndex = 0; ui32LoopIndex < SIZEOF(rxMemoryCopyTests) && !ui8Error; ++ui32LoopIndex)
   {
      LogDebug("main ::vTestMemory: Test - Copy[% d] : Copying % d bytes from % x to % x ", ui32LoopIndex, rxMemoryCopyTests[ui32LoopIndex].ui32Size, rxMemoryCopyTests[ui32LoopIndex].ui32SourceAddress, rxMemoryCopyTests[ui32LoopIndex].ui32DestinationAddress);
      i32MemoryCopyRegion(&xMemory, rxMemoryCopyTests[ui32LoopIndex].ui32SourceAddress, rxMemoryCopyTests[ui32LoopIndex].ui32DestinationAddress, rxMemoryCopyTests[ui32LoopIndex].ui32Size);

      // Generate Dump
      Dump_t *pxDump = pxConvertMemoryToDump(&xMemory, FB);
      if (i32DumpCompare(&rxDumpCopyExpected[ui32LoopIndex], pxDump))
      {
         ui8Error = TRUE;
      }


      if (ui8Error)
      {
         LogDebug("main ::vTestMemory: Test - Copy[% d] NOK !", ui32LoopIndex);
      }
      else
      {
         LogDebug("main ::vTestMemory: Test - Copy[% d] OK !", ui32LoopIndex);
      }

      i32MemoryPrint(&xMemory);
   }

   LogDebug("main ::vTestMemory: Testing Finished !\n ");
}

/*****************************************************************************
 * @param argc argument count
 * @param argv string arguments
 ******************************************************************************/
int main(int argc, char *argv[])
{
   UnityBegin(__BASE_FILE__);
   RUN_TEST(test01_MemoryisInitialized, 0);
   RUN_TEST(test02_MemoryHasFailedDeinitialization, 0);
   RUN_TEST(test03_MemorySizeIsZero, 0);
   RUN_TEST(test04_MemorySizeIsOneBlock, 0);
   RUN_TEST(test05_MemorySizeIsTwoBlocks, 0);
   RUN_TEST(test06_MemoryisPrintable, 0);
   RUN_TEST(test07_MemoryisComparable, 0);
   RUN_TEST(test08_MemoryHasGaps, 0);
   return(UnityEnd());
}
