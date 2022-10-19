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

#include "config.h"
#include "types.h"
#include "misc/memory.h"
#include "misc/file.h"
#include "misc/helpers.h"
#include "misc/dump.h"

/* Unity */
#include "unity_config.h"
#include "unity.h"



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

Dump_t rxDumpAddExpected[] = { { 0x100, sizeof(rui8DumpAddTest0), rui8DumpAddTest0 },    //0
                               { 0x100, sizeof(rui8DumpAddTest1), rui8DumpAddTest1 },    //1
                               { 0x100, sizeof(rui8DumpAddTest2), rui8DumpAddTest2 },    //2
                               { 0x100, sizeof(rui8DumpAddTest3), rui8DumpAddTest3 },    //3
                               { 0x100, sizeof(rui8DumpAddTest4), rui8DumpAddTest4 },    //4
                               {  0xa0, sizeof(rui8DumpAddTest5), rui8DumpAddTest5 },    //5
                               {  0xa0, sizeof(rui8DumpAddTest6), rui8DumpAddTest6 },    //6
                               {  0xa0, sizeof(rui8DumpAddTest7), rui8DumpAddTest7 },    //7
                               {  0xa0, sizeof(rui8DumpAddTest8), rui8DumpAddTest8 },    //8
                               {  0xa0, sizeof(rui8DumpAddTest9), rui8DumpAddTest9 }, }; //9

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
Dump_t           rxDumpCopyExpected[] = { { 0xa0, sizeof(rui8DumpCopyTest0), rui8DumpCopyTest0 } }; //0


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
void test_DumpIsNULL()
{
   Dump_t *testDump = pxDumpCreate(0, 0);
   TEST_ASSERT(testDump == NULL);
}

/*****************************************************************************
 * @brief Tests for failed deallocation
 ******************************************************************************/
void test_DumpNotDeallocated()
{
   int32_t status = i32DumpDestroy(NULL);
   TEST_ASSERT(status != 0);
}

/*****************************************************************************
 * @brief Tests for successful allocation
 ******************************************************************************/
void test_DumpCreatedAndDestroyed()
{
   #define TSIZE    1
   #define TADDR    100
   Dump_t *testDump = pxDumpCreate(TADDR, TSIZE);
   TEST_ASSERT(testDump != NULL);
   TEST_ASSERT(testDump->ui32Size == TSIZE);
   TEST_ASSERT(testDump->ui32BaseAddress == TADDR);
   int32_t status = i32DumpDestroy(testDump);
   TEST_ASSERT(status == 0);
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
      LogTest("main::vTestMemory: Test-Add[%d]: Writing %d bytes at %x", ui32LoopIndex, rxMemoryAddTests[ui32LoopIndex].ui32Size, rxMemoryAddTests[ui32LoopIndex].ui32DestinationAddress);
      i32MemoryAdd(&xMemory, rxMemoryAddTests[ui32LoopIndex].ui32DestinationAddress, rxMemoryAddTests[ui32LoopIndex].ui32Size, rxMemoryAddTests[ui32LoopIndex].pui8Data);

      // Generate Dump
      Dump_t *pxDump = pxDumpGenerateFromMemory(&xMemory, FB);
      if (i32DumpCompare(&rxDumpAddExpected[ui32LoopIndex], pxDump))
      {
         ui8Error = TRUE;
      }

      //
      if (ui8Error)
      {
         LogTest("main::vTestMemory: Test-Add[%d] NOK!", ui32LoopIndex);
      }
      else
      {
         LogTest("main::vTestMemory: Test-Add[%d] OK!", ui32LoopIndex);
      }

      vMemoryPrint(&xMemory);
   }

// Copy test
//------------------------------------------------------------------------------------------------------
   for (uint32_t ui32LoopIndex = 0; ui32LoopIndex < SIZEOF(rxMemoryCopyTests) && !ui8Error; ++ui32LoopIndex)
   {
      LogTest("main::vTestMemory: Test-Copy[%d]: Copying %d bytes from %x to %x", ui32LoopIndex, rxMemoryCopyTests[ui32LoopIndex].ui32Size, rxMemoryCopyTests[ui32LoopIndex].ui32SourceAddress, rxMemoryCopyTests[ui32LoopIndex].ui32DestinationAddress);
      i32MemoryCopyRegion(&xMemory, rxMemoryCopyTests[ui32LoopIndex].ui32SourceAddress, rxMemoryCopyTests[ui32LoopIndex].ui32DestinationAddress, rxMemoryCopyTests[ui32LoopIndex].ui32Size);

      // Generate Dump
      Dump_t *pxDump = pxDumpGenerateFromMemory(&xMemory, FB);
      if (i32DumpCompare(&rxDumpCopyExpected[ui32LoopIndex], pxDump))
      {
         ui8Error = TRUE;
      }


      if (ui8Error)
      {
         LogTest("main::vTestMemory: Test-Copy[%d] NOK!", ui32LoopIndex);
      }
      else
      {
         LogTest("main::vTestMemory: Test-Copy[%d] OK!", ui32LoopIndex);
      }

      vMemoryPrint(&xMemory);
   }

   LogTest("main::vTestMemory: Testing Finished!\n");
}

/*****************************************************************************
 * @param argc argument count
 * @param argv string arguments
 ******************************************************************************/
int main(int argc, char *argv[])
{
   UnityBegin("test-target1.c");
   RUN_TEST(test_DumpIsNULL, 0);
   RUN_TEST(test_DumpNotDeallocated, 0);
   RUN_TEST(test_DumpCreatedAndDestroyed, 0);

   return(UnityEnd());
}
