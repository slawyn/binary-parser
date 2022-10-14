#include <stdlib.h>

#include "types.h"
#include "misc/memory.h"
#include "misc/parsers.h"
#include "misc/helpers.h"


#define MAX_BUFFER_SIZE             (128)
#define BYTE_NIBBLES                (2)

// Size and offsets are for bytes not nibbles
#define HEX_HEAD_LINESTART          ':'
#define HEX_RT_DATA                 0x00
#define HEX_RT_EOF                  0x01
#define HEX_RT_EXT_SEG_ADR          0x02
#define HEX_RT_START_SEG_ADR        0x03
#define HEX_RT_EXT_LIN_ADR          0x04
#define HEX_RT_START_LIN_ADR        0x05
#define HEX_ADDRESS_SZ              4
#define HEX_RT_SZ                   2
#define HEX_LINESTART_IDX           0
#define HEX_BYTE_COUNT_IDX          1
#define HEX_ADDRESS_IDX             3
#define HEX_RECTYPE_IDX             7
#define HEX_DATA_BYTE0_IDX          9
#define HEX_DATA_ADDR_2BYTE_SZ      (2 << 1)
#define HEX_DATA_ADDR_4BYTE_SZ      (4 << 1)
#define HEX_CHECKSUM_SZ             (1 << 1)
#define HEX_MIN_SIZE                (HEX_RECTYPE_IDX1 + HEX_CHECKSUM_SZ)

#define S19_HEADER_SRECORD          'S'
#define S19_HEADER_S0               '0'
#define S19_HEADER_S1               '1'
#define S19_HEADER_S2               '2'
#define S19_HEADER_S3               '3'
#define S19_HEADER_S4               '4'
#define S19_HEADER_S5               '5'
#define S19_HEADER_S6               '6'
#define S19_HEADER_S7               '7'
#define S19_HEADER_S8               '8'
#define S19_HEADER_S9               '9'
#define S19_S_IDX                   (0)
#define S19_TYPE_IDX                (1)
#define S19_BYTE_COUNT_IDX          (1 << 1)

#define S19_ADDRESS_BYTE0_OFFSET    (1 << 1)
#define S19_ADDRESS_BYTE1_OFFSET    (2 << 1)
#define S19_DATA_BYTE0_OFFSET       (3 << 1)
#define S19_DATA_BYTE1_OFFSET       (4 << 1)
#define S19_DATA_BYTE2_OFFSET       (4 << 1)
#define S19_S_SZ                    (1 << 1)
#define S19_BYTE_COUNT_SZ           (1 << 1)
#define S19_ADDRESS2_SZ             (2 << 1)
#define S19_ADDRESS3_SZ             (3 << 1)
#define S19_ADDRESS4_SZ             (4 << 1)
#define S19_CHECKSUM_SZ             (1 << 1)

// Sx + ByteCount + Checksum
#define S19_MIN_SZ                  (S19_S_SZ + S19_BYTE_COUNT_SZ + S19_ADDRESS2_SZ + S19_CHECKSUM_SZ)

uint8_t rui8DataBuffer[MAX_BUFFER_SIZE];

/***************************************************************
* @param sRec .hex Records
* @param xSize Length of line
* @param pxMemory Pointer to Memory
* @return         -1: Error unknown format
*                 -2: Error unknown record
*                 -3: Error data length
*                 -4: Error checksum
*                 -5: Error record length
*                 -6: Error unimplemented
*                  0: OK
***************************************************************/
int32_t i32HexParse(char *sRec, size_t xSize, Memory_t *pxMemory)
{
   uint32_t ui32Temp;
   uint16_t ui16Address;
   uint8_t *pui8Buffer = NULL;

   uint8_t ui8ByteCount;
   uint8_t ui8RecordType;
   uint8_t ui8ByteIndex;
   uint8_t ui8Checksum = 0;

   // Check min length
   if ((sRec[HEX_LINESTART_IDX] == HEX_HEAD_LINESTART) && (xSize < (HEX_DATA_BYTE0_IDX + S19_CHECKSUM_SZ)))
   {
      i32Log("parsers::i32HexParse: Error: Not a Hex record %s", sRec);
      return(-1);
   }
   ui8ByteCount  = ui32ConvertHexStringToByte(&sRec[HEX_BYTE_COUNT_IDX]) * 2;
   ui16Address   = ui32ConvertHexStringToWord(&sRec[HEX_ADDRESS_IDX]);
   ui8RecordType = ui32ConvertHexStringToByte(&sRec[HEX_RECTYPE_IDX]);

   // Check type
   if (ui8RecordType > HEX_RT_START_LIN_ADR)
   {
      i32Log("parsers::i32HexParse: Not a know record type %x", ui8RecordType);
      return(-2);
   }

   // Check Data length
   if ((xSize - HEX_DATA_BYTE0_IDX) < (ui8ByteCount + HEX_CHECKSUM_SZ))
   {
      i32Log("parsers::i32HexParse: Error: Data is shorter than byte count %d %s", (ui8ByteCount) >> 1, sRec);
      return(-3);
   }

   // Validate checksum

   for (ui8ByteIndex = 1; ui8ByteIndex < ((ui8ByteCount + HEX_DATA_BYTE0_IDX)); ui8ByteIndex += 2)
   {
      ui8Checksum += ui32ConvertHexStringToByte(&sRec[ui8ByteIndex]);
   }

   ui8Checksum = (~ui8Checksum + 1);
   ui32Temp    = ui32ConvertHexStringToByte(&sRec[ui8ByteIndex]);
   if (ui8Checksum != (uint8_t)ui32Temp)
   {
      i32Log("parsers::i32HexParse: Error: Checksum calculated=%x expected=%x count=%d", ui8Checksum, ui32Temp, ui8ByteCount);
      return(-4);
   }

   // Parse Hex-Record
   sRec = &sRec[HEX_DATA_BYTE0_IDX];
   switch (ui8RecordType)
   {
   case HEX_RT_DATA:
      if (MAX_BUFFER_SIZE < (ui8ByteCount >> 1))
      {
         i32Log("parsers::i32HexParse: Error data too long at %x", ui32Temp);
      }
      else
      {
         vConvertHexStringToByteBuffer(&sRec[0], rui8DataBuffer, (ui8ByteCount >> 1));
      }

      if (i32MemoryAdd(pxMemory, ui16Address, (ui8ByteCount >> 1), rui8DataBuffer))
      {
         i32Log("parsers::i32HexParse: Problem creating block at %x", ui16Address);
      }
      break;

   case HEX_RT_EOF:
      i32Log("parsers::i32HexParse: End Of File");
      break;

   case HEX_RT_EXT_SEG_ADR:
      if ((ui8ByteCount) <= (HEX_DATA_ADDR_2BYTE_SZ))
      {
         i32Log("parsers::i32HexParse: 02:Error: Record size");
         return(-5);
      }
      pxMemory->ui32BaseAddress = ui32ConvertHexStringToWord(&sRec[0]);
      break;

   case HEX_RT_START_SEG_ADR:
      if ((ui8ByteCount) <= (HEX_DATA_ADDR_4BYTE_SZ))
      {
         i32Log("parsers::i32HexParse: 03:Error: Record size");
         return(-5);
      }
      // ui32BaseAddress = ui32ConvertHexStringToDword(&sRec[0]);
      i32Log("parsers::i32HexParse: 03:Warning: Unimplemented!");
      return(-6);

      break;

   case HEX_RT_EXT_LIN_ADR:
      if ((ui8ByteCount) <= (HEX_DATA_ADDR_2BYTE_SZ))
      {
         i32Log("parsers::i32HexParse: 04:Error: Record size");
         return(-5);
      }
      pxMemory->ui32BaseAddress = ui32ConvertHexStringToWord(&sRec[0]);
      break;

   case HEX_RT_START_LIN_ADR:
      if ((ui8ByteCount) <= (HEX_DATA_ADDR_4BYTE_SZ))
      {
         i32Log("parsers::i32HexParse: 05:Warning: Record size");
         return(-5);
      }

      i32Log("parsers::i32HexParse: 05:Error: Unimplemented!");
      return(-6);

      // ui32BaseAddress = ui32ConvertHexStringToDword(&sRec[0]);
      break;

   default:
      i32Log("parsers::i32HexParse: Unimplemented[%x] %s", ui8RecordType, sRec);
      break;
   }


   return(0);
}

/***************************************************************
* @param sRec .s19 Records
* @param xSize Length of line
* @param pxMemory Pointer to Memory
* @return         -1: Error unknown format
*                 -2: Error unknown record
*                 -3: Error data length
*                 -4: Error checksum
*                 -5: Error record length
*                  0: OK
***************************************************************/
int32_t i32S19Parse(char *sRec, size_t xSize, Memory_t *pxMemory)
{
   // Fields:
   // S  Type  ByteCount   Address   Data  Checksum

   // Reference:
   // https://en.wikipedia.org/wiki/SREC_(file_format)
   uint32_t ui32Temp;
   uint8_t *pui8Buffer = NULL;
   uint8_t  ui8ByteCount;
   uint8_t  ui8ByteIndex;
   uint8_t  ui8Checksum = 0;
   char     cRecordType;

   // Check if it is an s-record
   if ((xSize < S19_MIN_SZ) && (sRec[S19_S_IDX] == S19_HEADER_SRECORD))
   {
      i32Log("parsers::i32S19Parse: Error: Not a S19 record %s", sRec);
      return(-1);
   }
   // Check if the type is known
   //--------------------
   cRecordType = sRec[S19_TYPE_IDX];
   if (cRecordType > S19_HEADER_S9 || cRecordType < S19_HEADER_S0)
   {
      i32Log("parsers::i32S19Parse: Error: Not a known S19 type of record %c %s", cRecordType, sRec);
      return(-2);
   }
   else
   {
      // Trimm the record
      sRec = &sRec[S19_BYTE_COUNT_IDX];
   }

   // Check byte count
   //--------------------
   ui8ByteCount = ui32ConvertHexStringToByte(sRec);
   ui8ByteCount = ui8ByteCount * 2;
   if (xSize < ui8ByteCount)
   {
      i32Log("parsers::i32S19Parse: Error: Line is shorter than byte count %d %s", ui8ByteCount, sRec);
      return(-3);
   }

   // Check checksum
   //--------------------
   for (ui8ByteIndex = 0; ui8ByteIndex < ((ui8ByteCount)); ui8ByteIndex += 2)
   {
      ui8Checksum += ui32ConvertHexStringToByte(&sRec[(ui8ByteIndex)]);
   }

   ui8Checksum = ~ui8Checksum;
   ui32Temp    = ui32ConvertHexStringToByte(&sRec[(ui8ByteIndex)]);
   if (ui8Checksum != (uint8_t)ui32Temp)
   {
      i32Log("parsers::i32S19Parse: Error: Checksum calculated=%x expected=%x bytecount=%d", ui8Checksum, ui32Temp, (ui8ByteCount >> 1));
      return(-4);
   }

   // Trim and Parse S-Record
   sRec[ui8ByteCount] = '\0';
   switch (cRecordType)
   {
   // Header
   case S19_HEADER_S0:
      if ((ui8ByteCount) <= (S19_DATA_BYTE0_OFFSET))
      {
         i32Log("parsers::i32S19Parse: S0:Error: Record size");
         return(-5);
      }

      i32Log("parsers::i32S19Parse: Header:%s", &sRec[S19_DATA_BYTE0_OFFSET]);
      break;

   // Data
   case S19_HEADER_S1:
      if (ui8ByteCount <= (S19_DATA_BYTE0_OFFSET))
      {
         i32Log("parsers::i32S19Parse: S1:Error: Record size");
         return(-5);
      }
      else
      {
         // Address
         ui32Temp  = ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE0_OFFSET]) << 8;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE1_OFFSET]);

         // Byte series
         ui8ByteCount -= (S19_DATA_BYTE0_OFFSET);
         if (MAX_BUFFER_SIZE < (ui8ByteCount >> 1))
         {
            i32Log("parsers::i32S19Parse: Error data too long at %x", ui32Temp);
         }
         else
         {
            vConvertHexStringToByteBuffer(&sRec[S19_DATA_BYTE0_OFFSET], rui8DataBuffer, (ui8ByteCount >> 1));
         }


         // Create block
         if (i32MemoryAdd(pxMemory, ui32Temp, (ui8ByteCount >> 1), rui8DataBuffer))
         {
            i32Log("parsers::i32S19Parse: Error creating block at %x", ui32Temp);
         }
      }
      break;

   // Data
   case S19_HEADER_S2:
      if (ui8ByteCount <= (S19_DATA_BYTE1_OFFSET))
      {
         i32Log("parsers::i32S19Parse: S2:Error: Record size");
         return(-5);
      }
      else
      {
         // Address
         ui32Temp  = ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE0_OFFSET]) << 16;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE1_OFFSET]) << 8;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_DATA_BYTE0_OFFSET]);

         // Byte series
         ui8ByteCount -= S19_DATA_BYTE1_OFFSET;
         if (MAX_BUFFER_SIZE < (ui8ByteCount >> 1))
         {
            i32Log("parsers::i32S19Parse: Error data too long at %x", ui32Temp);
         }
         else
         {
            vConvertHexStringToByteBuffer(&sRec[S19_DATA_BYTE1_OFFSET], rui8DataBuffer, (ui8ByteCount >> 1));
         }
         // Create block
         if (i32MemoryAdd(pxMemory, ui32Temp, (ui8ByteCount >> 1), rui8DataBuffer))
         {
            i32Log("parsers::i32S19Parse: Problem creating block at %x", ui32Temp);
         }
      }
      break;

   // Data
   case S19_HEADER_S3:
      if (ui8ByteCount <= (S19_DATA_BYTE2_OFFSET))
      {
         i32Log("parsers::i32S19Parse: S3:Error: Record size");
         return(-5);
      }
      else
      {
         // Address
         ui32Temp  = ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE0_OFFSET]) << 24;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE1_OFFSET]) << 16;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_DATA_BYTE0_OFFSET]) << 8;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_DATA_BYTE1_OFFSET]);

         // Byte series
         ui8ByteCount -= S19_DATA_BYTE2_OFFSET;
         if (MAX_BUFFER_SIZE < (ui8ByteCount >> 1))
         {
            i32Log("parsers::i32S19Parse: Error data too long at %x", ui32Temp);
         }
         else
         {
            vConvertHexStringToByteBuffer(&sRec[S19_DATA_BYTE2_OFFSET], pui8Buffer, (ui8ByteCount >> 1));
         }
         // Create block
         if (i32MemoryAdd(pxMemory, ui32Temp, (ui8ByteCount >> 1), rui8DataBuffer))
         {
            i32Log("parsers::i32S19Parse: Problem creating block at %x", ui32Temp);
         }
      }
      break;

   // Reserved
   case S19_HEADER_S4:
      break;

   // Count
   case S19_HEADER_S5:
      if (ui8ByteCount <= (S19_ADDRESS_BYTE1_OFFSET))
      {
         i32Log("parsers::i32S19Parse: S5:Error: Record size");
      }
      else
      {
         ui32Temp  = ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE0_OFFSET]) << 8;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE1_OFFSET]);
         i32Log("parsers::i32S19Parse: Count:%d", ui32Temp);
      }
      break;

   // Count
   case S19_HEADER_S6:
      if (ui8ByteCount <= (S19_DATA_BYTE0_OFFSET))
      {
         i32Log("parsers::i32S19Parse: S6:Error: Record size");
      }
      else
      {
         ui32Temp  = ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE0_OFFSET]) << 16;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE1_OFFSET]) << 8;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_DATA_BYTE0_OFFSET]);
         i32Log("parsers::i32S19Parse: S6:Count:%d", ui32Temp);
      }
      break;

   // 32-bit Start Address
   case S19_HEADER_S7:
      if (ui8ByteCount <= (S19_DATA_BYTE1_OFFSET))
      {
         i32Log("parsers::i32S19Parse: S7:Error: Record size");
      }
      else
      {
         ui32Temp  = ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE0_OFFSET]) << 24;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE1_OFFSET]) << 16;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_DATA_BYTE0_OFFSET]) << 8;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_DATA_BYTE1_OFFSET]);
      }
      break;

   // Start Address
   case S19_HEADER_S8:
      if (ui8ByteCount <= (S19_DATA_BYTE0_OFFSET))
      {
         i32Log("parsers::i32S19Parse: S8:Error: Record size");
      }
      else
      {
         ui32Temp  = ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE0_OFFSET]) << 16;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE1_OFFSET]) << 8;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_DATA_BYTE0_OFFSET]);
      }
      break;

   // Start Address
   case S19_HEADER_S9:
      if (ui8ByteCount < (S19_DATA_BYTE0_OFFSET))
      {
         i32Log("parsers::i32S19Parse: S9:Error: Record size");
      }
      else
      {
         ui32Temp  = ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE0_OFFSET]) << 16;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE1_OFFSET]) << 8;
      }
      break;
   }

   return(0);
}
