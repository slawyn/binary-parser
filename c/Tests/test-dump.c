#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "config.h"
#include "types.h"
#include "misc/dump.h"
#include "misc/helpers.h"

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
   #define T03_SIZE_01    1
   #define T03_ADDR_01    100

   Dump_t *testDump = pxDumpCreate(T03_ADDR_01, T03_SIZE_01);
   TEST_ASSERT(testDump != NULL);
   TEST_ASSERT(testDump->ui32Size == T03_SIZE_01);
   TEST_ASSERT(testDump->ui32BaseAddress == T03_ADDR_01);
   TEST_ASSERT(testDump->pui8Data != NULL);
   TEST_ASSERT(testDump->ui32Offset == 0);
   int32_t status = i32DumpDestroy(testDump);
   TEST_ASSERT(status == 0);

   #undef T03_SIZE_01
   #undef T03_ADDR_01
}

/*****************************************************************************
 * @brief Tests for successfull filling
 ******************************************************************************/
void test04_DumpIsFilled()
{
   #define T04_ARRAY_01    array_rising
   #define T04_SIZE_01     sizeof(T04_ARRAY_01)
   #define T04_ADDR_01     100
   Dump_t * testDump = pxDumpCreate(T04_ADDR_01, T04_SIZE_01);

   int32_t status_add = i32DumpAddBuffer(testDump, T04_SIZE_01, T04_ARRAY_01);
   TEST_ASSERT(status_add == 0);

   int32_t status_mc = memcmp(testDump->pui8Data, T04_ARRAY_01, T04_SIZE_01);
   TEST_ASSERT(status_mc == 0);

   int32_t status = i32DumpDestroy(testDump);
   TEST_ASSERT(status == 0);

   #undef T04_ARRAY_01
   #undef T04_SIZE_01
   #undef T04_ADDR_01
}

/*****************************************************************************
 * @brief Tests for successful multi-step filling
 ******************************************************************************/
void test05_DumpIsFilledMultiple()
{
   #define T05_ADDR_01     0
   #define T05_ARRAY_01    array_rising
   #define T05_ARRAY_02    array_falling
   #define T05_SIZE_01     sizeof(T05_ARRAY_01)
   #define T05_SIZE_02     sizeof(T05_ARRAY_02)
   #define T05_SIZE_03     (T05_SIZE_01 + T05_SIZE_02)


   uint8_t array_total[T05_SIZE_03];

   Dump_t *testDump = pxDumpCreate(T05_ADDR_01, T05_SIZE_03);

   memcpy(array_total, T05_ARRAY_01, T05_SIZE_01);
   memcpy(array_total, T05_ARRAY_02 + T05_SIZE_01, T05_SIZE_02);

   int32_t status = i32DumpAddBuffer(testDump, T05_SIZE_01, array_total);
   TEST_ASSERT(status == 0);

   status = i32DumpAddBuffer(testDump, T05_SIZE_02, array_total + T05_SIZE_01);
   TEST_ASSERT(status == 0);

   status = i32DumpAddBuffer(testDump, 0, array_total + T05_SIZE_01);
   TEST_ASSERT(status != 0);

   status = memcmp(testDump->pui8Data, array_total, T05_SIZE_03);
   TEST_ASSERT(status == 0);

   status = i32DumpDestroy(testDump);
   TEST_ASSERT(status == 0);

   #undef T05_ARRAY_01
   #undef T05_ARRAY_02
   #undef T05_SIZE_01
   #undef T05_SIZE_02
   #undef T05_SIZE_03
   #undef T05_ADDR_01
}

/*****************************************************************************
 * @brief Tests for failed comparison
 ******************************************************************************/
void test06_DumpsAreDifferent()
{
   #define T06_ARRAY_01    array_rising
   #define T06_SIZE_01     sizeof(T06_ARRAY_01)
   #define T06_SIZE_02     sizeof(T06_ARRAY_01)
   #define T06_SIZE_03     (sizeof(T06_ARRAY_01) - 1)
   #define T06_SIZE_04     T06_SIZE_03
   #define T06_SIZE_05     T06_SIZE_03
   #define T06_ADDR_01     100
   #define T06_ADDR_02     (T06_ADDR_01 + 1)
   #define T06_ADDR_03     T06_ADDR_01
   #define T06_ADDR_04     T06_ADDR_01
   #define T06_ADDR_05     T06_ADDR_01

   Dump_t *testDump1 = pxDumpCreate(T06_ADDR_01, T06_SIZE_01);
   Dump_t *testDump2 = pxDumpCreate(T06_ADDR_02, T06_SIZE_02);
   Dump_t *testDump3 = pxDumpCreate(T06_ADDR_03, T06_SIZE_03);
   Dump_t *testDump4 = pxDumpCreate(T06_ADDR_04, T06_SIZE_04);
   Dump_t *testDump5 = pxDumpCreate(T06_ADDR_05, T06_SIZE_05);

   TEST_ASSERT(testDump1 != NULL);
   TEST_ASSERT(testDump2 != NULL);
   TEST_ASSERT(testDump3 != NULL);
   TEST_ASSERT(testDump4 != NULL);
   TEST_ASSERT(testDump5 != NULL);

   int32_t status_add1 = i32DumpAddBuffer(testDump1, T06_SIZE_01, T06_ARRAY_01);
   TEST_ASSERT(status_add1 == 0);

   int32_t status_add2 = i32DumpAddBuffer(testDump2, T06_SIZE_02, T06_ARRAY_01);
   TEST_ASSERT(status_add2 == 0);

   int32_t status_add3 = i32DumpAddBuffer(testDump3, T06_SIZE_03, T06_ARRAY_01);
   TEST_ASSERT(status_add3 == 0);

   int32_t status_add4 = i32DumpAddBuffer(testDump4, T06_SIZE_04, T06_ARRAY_01);
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

   #undef T06_ARRAY_01
   #undef T06_SIZE_01
   #undef T06_SIZE_02
   #undef T06_SIZE_03
   #undef T06_SIZE_04
   #undef T06_SIZE_05
   #undef T06_ADDR_01
   #undef T06_ADDR_02
   #undef T06_ADDR_03
   #undef T06_ADDR_04
   #undef T06_ADDR_05
}

/*****************************************************************************
 * @brief Tests for successful comparison
 ******************************************************************************/
void test07_DumpsAreEqual()
{
   #define T07_ARRAY_01    array_rising
   #define T07_SIZE_01     sizeof(T07_ARRAY_01)
   #define T07_SIZE_02     sizeof(T07_ARRAY_01)
   #define T07_ADDR_01     10000
   #define T07_ADDR_02     10000

   Dump_t * testDump1 = pxDumpCreate(T07_ADDR_01, T07_SIZE_01);
   Dump_t *testDump2 = pxDumpCreate(T07_ADDR_02, T07_SIZE_02);

   TEST_ASSERT(testDump1 != NULL);
   TEST_ASSERT(testDump2 != NULL);

   int32_t status_add1 = i32DumpAddBuffer(testDump1, T07_SIZE_01, T07_ARRAY_01);
   TEST_ASSERT(status_add1 == 0);

   for (int i = 0; i < T07_SIZE_02; ++i)
   {
      int32_t status_add2 = i32DumpAddBuffer(testDump2, 1, &T07_ARRAY_01[i]);
      TEST_ASSERT(status_add2 == 0);
   }

   int32_t status_compx = i32DumpCompare(testDump1, testDump2);
   TEST_ASSERT(status_compx == 0);

   int32_t status_dest1 = i32DumpDestroy(testDump1);
   TEST_ASSERT(status_dest1 == 0);

   int32_t status_dest2 = i32DumpDestroy(testDump2);
   TEST_ASSERT(status_dest2 == 0);

   #undef T07_ARRAY_01
   #undef T07_SIZE_01
   #undef T07_SIZE_02
   #undef T07_ADDR_01
   #undef T07_ADDR_02
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
