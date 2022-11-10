#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "config.h"
#include "types.h"
#include "misc/helpers.h"

/* Unity */
#include "unity_config.h "
#include "unity.h "

PROTOTYPE uint32_t ui32ConvertHexNibbleToUint(char cHex);

/*****************************************************************************
 * @brief Unity Setup and Teardowns
 ******************************************************************************/
void setUp(void)
{
}

void tearDown(void)
{
}

void test00_NibbleIsConvertable(void)
{
   char test_array[16] = { '0', '1', '2', '3', '4', '5', '6', '7',
                           '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', };

   for (int i = 0; i < sizeof(test_array); ++i)
   {
      uint32_t result = ui32ConvertHexNibbleToUint(test_array[i]);
      TEST_ASSERT(result == i);
   }
}

void test01_NibblesIsNotConvertable(void)
{
   uint32_t result = ui32ConvertHexNibbleToUint('G');
   TEST_ASSERT(result == 0xFFFFFFFF);
}

void test02_TwoNibblesAreConvertable(void)
{
   char *FE = "FE";
   char *D1 = "D1";

   uint32_t result = ui32ConvertHexStringToByte(FE);
   TEST_ASSERT(result == 0xFE);
   result = ui32ConvertHexStringToByte(D1);
   TEST_ASSERT(result == 0xD1);
}

void test03_BuffersAreConvertable(void)
{
   char *  FEED              = "FEED";
   char *  DEADCAFE01        = "DEADCAFE01";
   uint8_t test_feed[]       = { 0xFE, 0xED };
   uint8_t test_deadcafe01[] = { 0xDE, 0xAD, 0xCA, 0xFE, 0x01 };

   uint8_t buffer[100];

   vConvertHexStringToByteBuffer(FEED, (uint8_t *)&buffer, (strlen(FEED)) >> 1);
   TEST_ASSERT(memcmp(buffer, test_feed, sizeof(test_feed)) == 0);

   vConvertHexStringToByteBuffer(DEADCAFE01, (uint8_t *)&buffer, (strlen(DEADCAFE01)) >> 1);
   TEST_ASSERT(memcmp(buffer, test_deadcafe01, sizeof(test_deadcafe01)) == 0);
}

void test04_4NibblesAreConvertable(void)
{
   char *   FEED = "FEED";
   uint16_t feed = 0xFEED;

   uint16_t word = ui32ConvertHexStringToWord(FEED);
   TEST_ASSERT(word == feed);
}

void test05_8NibblesAreConvertable(void)
{
   char *   FEEDfood = "F00DFEED";
   uint32_t feedfood = 0xf00dFEED;

   uint32_t dword = ui32ConvertHexStringToDword(FEEDfood);
   TEST_ASSERT(dword == feedfood);
}

/*****************************************************************************
 * @param argc argument count
 * @param argv string arguments
 ******************************************************************************/
int main(int argc, char *argv[])
{
   UnityBegin(__FILE__);
   RUN_TEST(test00_NibbleIsConvertable, 0);
   RUN_TEST(test01_NibblesIsNotConvertable, 0);
   RUN_TEST(test02_TwoNibblesAreConvertable, 0);
   RUN_TEST(test03_BuffersAreConvertable, 0);
   RUN_TEST(test04_4NibblesAreConvertable, 0);
   RUN_TEST(test05_8NibblesAreConvertable, 0);

   return(UnityEnd());
}
