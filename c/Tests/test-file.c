#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "config.h"
#include "types.h"
#include "misc/memory.h"
#include "misc/file.h"


/* Unity */
#include "unity_config.h "
#include "unity.h "


PROTOTYPE size_t xGetLine(uint8_t **ppui8LineBuffer, const size_t xReadMax, FILE *pxFileHandle);

/*****************************************************************************
 * @brief Unity Setup and Teardowns
 ******************************************************************************/
void setUp(void)
{
}

void tearDown(void)
{
}

void test00_xGetLineisNULL(void)
{
   #define T00_Filename    "./Data/sdn3pd.s19"

   uint8_t  buf[2];
   uint8_t *ptr = (uint8_t *)&buf;

   FILE *file = fopen(T00_Filename, "r");
   TEST_ASSERT(file != NULL);

   // NULL BUffer
   size_t size = xGetLine(NULL, 100, file);
   TEST_ASSERT(size == 0);

   // SMall max
   size = xGetLine(&ptr, sizeof(buf), file);
   TEST_ASSERT(size == 0);

   fclose(file);
}

void test01_FileLoadArgumentsAreNull(void)
{
   #define Filename    "./Data/sdn3pd.s19"

   Memory_t memory;
   (void)i32MemoryInitialize(&memory);

   int32_t status = i32FileLoad(NULL, &memory);
   TEST_ASSERT(status != 0);

   status = i32FileLoad(Filename, NULL);
   TEST_ASSERT(status != 0);

   #undef  Filename
}

void test02_FileIsS19Loaded(void)
{
    #define Filename    "./Data/sdn3pd.s19"
   Memory_t memory;
   (void)i32MemoryInitialize(&memory);

   int32_t status = i32FileLoad(Filename, &memory);
   TEST_ASSERT(status == 0);
   (void)i32MemoryDeinitialize(&memory);

    #undef Filename
}

void test03_FileIsDummyNotLoaded(void)
{
    #define Filename    "./Data/fake-dummy.bla"
   Memory_t memory;
   (void)i32MemoryInitialize(&memory);

   int32_t status = i32FileLoad(Filename, &memory);
   TEST_ASSERT(status != 0);
   (void)i32MemoryDeinitialize(&memory);

    #undef Filename
}

void test04_FileIsHexLoaded(void)
{
    #define Filename    "./Data/hdn3pd-romrep.hex"
   Memory_t memory;
   (void)i32MemoryInitialize(&memory);

   int32_t status = i32FileLoad(Filename, &memory);
   TEST_ASSERT(status == 0);
   (void)i32MemoryDeinitialize(&memory);

    #undef Filename
}

void test05_FileIsNotFound(void)
{
    #define Filename    "./Data/missing-file.hex"
   Memory_t memory;
   (void)i32MemoryInitialize(&memory);

   int32_t status = i32FileLoad(Filename, &memory);
   TEST_ASSERT(status != 0);
   (void)i32MemoryDeinitialize(&memory);

    #undef Filename
}

/*****************************************************************************
 * @param argc argument count
 * @param argv string arguments
 ******************************************************************************/
int main(int argc, char *argv[])
{
   UnityBegin(__FILE__);
   RUN_TEST(test00_xGetLineisNULL, 0);
   RUN_TEST(test01_FileLoadArgumentsAreNull, 0);
   RUN_TEST(test02_FileIsS19Loaded, 0);
   RUN_TEST(test03_FileIsDummyNotLoaded, 0);
   RUN_TEST(test04_FileIsHexLoaded, 0);
   RUN_TEST(test05_FileIsNotFound, 0);
   return(UnityEnd());
}
