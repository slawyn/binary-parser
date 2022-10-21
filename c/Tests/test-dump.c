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

const uint8_t array_rising[]  = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };
const uint8_t array_falling[] = { 0xff, 0xee, 0xdd, 0xcc, 0xbb, 0xaa, 0x99, 0x88, 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00 };

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
 * @brief Tests for NULL creation
 ******************************************************************************/
void test01_DumpIsNULL()
{
   Dump_t *testDump = pxDumpCreate(0, 0);
   TEST_ASSERT(testDump == NULL);
}

/*****************************************************************************
 * @brief Tests for failed deallocation
 ******************************************************************************/
void test02_DumpNotDeallocated()
{
   int32_t status = i32DumpDestroy(NULL);
   TEST_ASSERT(status != 0);
}

/*****************************************************************************
 * @brief Tests for successful allocation
 ******************************************************************************/
void test03_DumpCreatedAndDestroyed()
{
   #define TSIZE03    1
   #define TADDR03    100
   Dump_t *testDump = pxDumpCreate(TADDR03, TSIZE03);
   TEST_ASSERT(testDump != NULL);
   TEST_ASSERT(testDump->ui32Size == TSIZE03);
   TEST_ASSERT(testDump->ui32BaseAddress == TADDR03);
   TEST_ASSERT(testDump->pui8Data != NULL);
   TEST_ASSERT(testDump->ui32Offset == 0);
   int32_t status = i32DumpDestroy(testDump);
   TEST_ASSERT(status == 0);
}

/*****************************************************************************
 * @brief Tests for successfull filling
 ******************************************************************************/
void test04_DumpIsFilled()
{
   #define TARRA04    array_rising
   #define TSIZE04    sizeof(TARRA04)
   #define TADDR04    100
   Dump_t * testDump = pxDumpCreate(TADDR04, TSIZE04);

   int32_t status_add = i32DumpAddBuffer(testDump, TSIZE04, TARRA04);
   TEST_ASSERT(status_add == 0);

   int32_t status_mc = memcmp(testDump->pui8Data, TARRA04, TSIZE04);
   TEST_ASSERT(status_mc == 0);

   int32_t status = i32DumpDestroy(testDump);
   TEST_ASSERT(status == 0);
}

/*****************************************************************************
 * @brief Tests for successful multi-step filling
 ******************************************************************************/
void test05_DumpIsFilledMultiple()
{
   #define TARRA051    array_rising
   #define TARRA052    array_falling

   #define TSIZE051    sizeof(TARRA051)
   #define TSIZE052    sizeof(TARRA052)
   #define TSIZE05x    (TSIZE051 + TSIZE052)
   #define TADDR05x    0
   uint8_t array_total[TSIZE05x];

   Dump_t *testDump = pxDumpCreate(TADDR05x, TSIZE05x);

   memcpy(array_total, TARRA051, TSIZE051);
   memcpy(array_total, TARRA052 + TSIZE051, TSIZE052);

   int32_t status_add1 = i32DumpAddBuffer(testDump, TSIZE051, array_total);
   TEST_ASSERT(status_add1 == 0);

   int32_t status_add2 = i32DumpAddBuffer(testDump, TSIZE052, array_total + TSIZE051);
   TEST_ASSERT(status_add2 == 0);

   int32_t status_mc1 = memcmp(testDump->pui8Data, array_total, TSIZE05x);
   TEST_ASSERT(status_mc1 == 0);

   int32_t status = i32DumpDestroy(testDump);
   TEST_ASSERT(status == 0);
}

/*****************************************************************************
 * @brief Tests for failed comparison
 ******************************************************************************/
void test06_DumpsAreDifferent()
{
   #define TARRA06x    array_rising

   #define TSIZE061    sizeof(TARRA06x)
   #define TSIZE062    sizeof(TARRA06x)
   #define TSIZE063    (sizeof(TARRA06x) - 1)
   #define TSIZE064    TSIZE063
   #define TSIZE065    TSIZE063

   #define TADDR061    100
   #define TADDR062    (TADDR061 + 1)
   #define TADDR063    TADDR061
   #define TADDR064    TADDR061
   #define TADDR065    TADDR061

   Dump_t *testDump1 = pxDumpCreate(TADDR061, TSIZE061);
   Dump_t *testDump2 = pxDumpCreate(TADDR062, TSIZE062);
   Dump_t *testDump3 = pxDumpCreate(TADDR063, TSIZE063);
   Dump_t *testDump4 = pxDumpCreate(TADDR064, TSIZE064);
   Dump_t *testDump5 = pxDumpCreate(TADDR065, TSIZE065);

   TEST_ASSERT(testDump1 != NULL);
   TEST_ASSERT(testDump2 != NULL);
   TEST_ASSERT(testDump3 != NULL);
   TEST_ASSERT(testDump4 != NULL);
   TEST_ASSERT(testDump5 != NULL);

   int32_t status_add1 = i32DumpAddBuffer(testDump1, TSIZE061, TARRA06x);
   TEST_ASSERT(status_add1 == 0);

   int32_t status_add2 = i32DumpAddBuffer(testDump2, TSIZE062, TARRA06x);
   TEST_ASSERT(status_add2 == 0);

   int32_t status_add3 = i32DumpAddBuffer(testDump3, TSIZE063, TARRA06x);
   TEST_ASSERT(status_add3 == 0);

   int32_t status_add4 = i32DumpAddBuffer(testDump4, TSIZE064, TARRA06x);
   TEST_ASSERT(status_add4 == 0);

   int32_t status_add5 = i32DumpAddBuffer(testDump5, testDump4->ui32Size, testDump4->pui8Data);
   testDump5->pui8Data[testDump5->ui32Size - 1] = testDump5->pui8Data[0];
   TEST_ASSERT(status_add5 == 0);

   int32_t status_compx = i32DumpCompare(testDump1, testDump1);
   TEST_ASSERT(status_compx == 0);

   int32_t status_comp1 = i32DumpCompare(testDump1, testDump2);
   TEST_ASSERT(status_comp1 == 0);

   int32_t status_comp2 = i32DumpCompare(testDump1, testDump3);
   TEST_ASSERT(status_comp2 != 0);

   int32_t status_comp3 = i32DumpCompare(testDump1, testDump4);
   TEST_ASSERT(status_comp3 != 0);

   int32_t status_comp4 = i32DumpCompare(testDump4, testDump5);
   TEST_ASSERT(status_comp4 != 0);

   int32_t status_dest_null1 = i32DumpCompare(testDump3, NULL);
   TEST_ASSERT(status_dest_null1 != 0);

   int32_t status_dest_null2 = i32DumpCompare(NULL, testDump4);
   TEST_ASSERT(status_dest_null2 != 0);

   int32_t status_dest_null3 = i32DumpCompare(NULL, NULL);
   TEST_ASSERT(status_dest_null3 != 0);

   int32_t status_dest1 = i32DumpDestroy(testDump1);
   TEST_ASSERT(status_dest1 == 0);

   int32_t status_dest2 = i32DumpDestroy(testDump2);
   TEST_ASSERT(status_dest2 == 0);

   int32_t status_dest3 = i32DumpDestroy(testDump3);
   TEST_ASSERT(status_dest3 == 0);

   int32_t status_dest4 = i32DumpDestroy(testDump4);
   TEST_ASSERT(status_dest4 == 0);

   int32_t status_dest5 = i32DumpDestroy(testDump5);
   TEST_ASSERT(status_dest5 == 0);

   int32_t status_destx = i32DumpDestroy(testDump1);
   TEST_ASSERT(status_destx != 0);
}

/*****************************************************************************
 * @brief Tests for successful comparison
 ******************************************************************************/
void test07_DumpsAreEqual()
{
   #define TARRA07x    array_rising

   #define TSIZE071    sizeof(TARRA07x)
   #define TSIZE072    sizeof(TARRA07x)

   #define TADDR071    10000
   #define TADDR072    10000

   Dump_t * testDump1 = pxDumpCreate(TADDR071, TSIZE071);
   Dump_t *testDump2 = pxDumpCreate(TADDR072, TSIZE072);

   TEST_ASSERT(testDump1 != NULL);
   TEST_ASSERT(testDump2 != NULL);

   int32_t status_add1 = i32DumpAddBuffer(testDump1, TSIZE061, TARRA06x);
   TEST_ASSERT(status_add1 == 0);

   for (int i = 0; i < TSIZE062; ++i)
   {
      int32_t status_add2 = i32DumpAddBuffer(testDump2, 1, &TARRA06x[i]);
      TEST_ASSERT(status_add2 == 0);
   }

   int32_t status_compx = i32DumpCompare(testDump1, testDump2);
   TEST_ASSERT(status_compx == 0);

   int32_t status_dest1 = i32DumpDestroy(testDump1);
   TEST_ASSERT(status_dest1 == 0);

   int32_t status_dest2 = i32DumpDestroy(testDump2);
   TEST_ASSERT(status_dest2 == 0);
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

/*****************************************************************************
 * @param argc argument count
 * @param argv string arguments
 ******************************************************************************/
int main(int argc, char *argv[])
{
   UnityBegin(__FILE__);
   RUN_TEST(test01_DumpIsNULL, 0);
   RUN_TEST(test02_DumpNotDeallocated, 0);
   RUN_TEST(test03_DumpCreatedAndDestroyed, 0);
   RUN_TEST(test04_DumpIsFilled, 0);
   RUN_TEST(test05_DumpIsFilledMultiple, 0);
   RUN_TEST(test06_DumpsAreDifferent, 0);
   RUN_TEST(test07_DumpsAreEqual, 0)

   return(UnityEnd());
}
