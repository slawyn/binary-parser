#include <stdlib.h>
#include "types.h"
#include "misc/memory.h"
#include "misc/parsers.h"
#include "misc/helpers.h"



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
      i32Log("Hex::Error: Not a Hex record %s", sRec);
      return(-1);
   }
   ui8ByteCount  = ui32ConvertHexStringToByte(&sRec[HEX_BYTE_COUNT_IDX]) * 2;
   ui16Address   = ui32ConvertHexStringToWord(&sRec[HEX_ADDRESS_IDX]);
   ui8RecordType = ui32ConvertHexStringToByte(&sRec[HEX_RECTYPE_IDX]);

   // Check type
   if (ui8RecordType > HEX_RT_START_LIN_ADR)
   {
      i32Log("Hex::Not a know record type %x", ui8RecordType);
      return(-1);
   }

   // Check Data length
   if ((xSize - HEX_DATA_BYTE0_IDX) < (ui8ByteCount + HEX_CHECKSUM_SZ))
   {
      i32Log("Hex::Error: Data is shorter than byte count %d %s", (ui8ByteCount) >> 1, sRec);
      return(-1);
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
      i32Log("Hex::Error: Checksum calculated=%x expected=%x count=%d", ui8Checksum, ui32Temp, ui8ByteCount);
      return(-2);
   }

   // Parse Hex-Record
   sRec = &sRec[HEX_DATA_BYTE0_IDX];
   switch (ui8RecordType)
   {
   case HEX_RT_DATA:
      pui8Buffer = malloc(ui8ByteCount);
      vConvertHexStringToByteBuffer(&sRec[0], pui8Buffer, (ui8ByteCount >> 1));
      i32MemoryblockInit(pxMemory, ui16Address, (ui8ByteCount >> 1), pui8Buffer);
      break;

   case HEX_RT_EOF:
      i32Log("Hex::End Of File");
      break;

   case HEX_RT_EXT_SEG_ADR:
      if ((ui8ByteCount) <= (HEX_DATA_ADDR_2BYTE_SZ))
      {
         i32Log("Hex::02:Error: Record size");
         return(-2);
      }
      pxMemory->ui32BaseAddress = ui32ConvertHexStringToWord(&sRec[0]);
      break;

   case HEX_RT_START_SEG_ADR:
      if ((ui8ByteCount) <= (HEX_DATA_ADDR_4BYTE_SZ))
      {
         i32Log("Hex::03:Error: Record size");
         return(-2);
      }
      // ui32BaseAddress = ui32ConvertHexStringToDword(&sRec[0]);
      i32Log("Hex::03:Warning: Unimplemented!");
      return(-3);

      break;

   case HEX_RT_EXT_LIN_ADR:
      if ((ui8ByteCount) <= (HEX_DATA_ADDR_2BYTE_SZ))
      {
         i32Log("Hex::04:Error: Record size");
         return(-2);
      }
      pxMemory->ui32BaseAddress = ui32ConvertHexStringToWord(&sRec[0]);
      break;

   case HEX_RT_START_LIN_ADR:
      if ((ui8ByteCount) <= (HEX_DATA_ADDR_4BYTE_SZ))
      {
         i32Log("Hex::05:Warning: Record size");
         return(-2);
      }

      i32Log("Hex::05:Error: Unimplemented!");
      return(-3);

      // ui32BaseAddress = ui32ConvertHexStringToDword(&sRec[0]);
      break;

   default:
      i32Log("Hex::Unimplemented[%x] %s", ui8RecordType, sRec);
      break;
   }


   return(0);
}

/***************************************************************
 * @param sRec
 ******************************************************************************/
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
      i32Log("S19::Error: Not a S19 record %s", sRec);
      return(-1);
   }
   // Check if the type is known
   //--------------------
   cRecordType = sRec[S19_TYPE_IDX];
   if (cRecordType > S19_HEADER_S9 || cRecordType < S19_HEADER_S0)
   {
      i32Log("S19::Error: Not a known S19 type of record %c %s", cRecordType, sRec);
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
      i32Log("S19::Error: Line is shorter than byte count %d %s", ui8ByteCount, sRec);
      return(-1);
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
      i32Log("S19::Error: Checksum calculated=%x expected=%x bytecount=%d", ui8Checksum, ui32Temp, (ui8ByteCount >> 1));
      return(-2);
   }

   // Trim and Parse S-Record
   sRec[ui8ByteCount] = '\0';
   switch (cRecordType)
   {
   // Header
   case S19_HEADER_S0:
      if ((ui8ByteCount) <= (S19_DATA_BYTE0_OFFSET))
      {
         i32Log("S19::S0:Error: Record size");
         return(-2);
      }

      i32Log("S19::Header:%s", &sRec[S19_DATA_BYTE0_OFFSET]);
      break;

   // Data
   case S19_HEADER_S1:
      if (ui8ByteCount <= (S19_DATA_BYTE0_OFFSET))
      {
         i32Log("S19::S1:Error: Record size");
         return(-2);
      }
      else
      {
         // Address
         ui32Temp  = ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE0_OFFSET]) << 8;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE1_OFFSET]);

         // Byte series
         ui8ByteCount -= (S19_DATA_BYTE0_OFFSET);

         pui8Buffer = malloc(xSize);
         vConvertHexStringToByteBuffer(&sRec[S19_DATA_BYTE0_OFFSET], pui8Buffer, (ui8ByteCount >> 1));

         // Create block
         i32MemoryblockInit(pxMemory, ui32Temp, (ui8ByteCount >> 1), pui8Buffer);
      }
      break;

   // Data
   case S19_HEADER_S2:
      if (ui8ByteCount <= (S19_DATA_BYTE1_OFFSET))
      {
         i32Log("S19::S2:Error: Record size");
         return(-2);
      }
      else
      {
         // Address
         ui32Temp  = ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE0_OFFSET]) << 16;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE1_OFFSET]) << 8;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_DATA_BYTE0_OFFSET]);

         // Byte series
         ui8ByteCount -= S19_DATA_BYTE1_OFFSET;
         pui8Buffer    = malloc(xSize);
         vConvertHexStringToByteBuffer(&sRec[S19_DATA_BYTE1_OFFSET], pui8Buffer, (ui8ByteCount >> 1));

         // Create block
         i32MemoryblockInit(pxMemory, ui32Temp, (ui8ByteCount >> 1), pui8Buffer);
      }
      break;

   // Data
   case S19_HEADER_S3:
      if (ui8ByteCount <= (S19_DATA_BYTE2_OFFSET))
      {
         i32Log("S19::S3:Error: Record size");
         return(-2);
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
         pui8Buffer    = malloc(xSize);
         vConvertHexStringToByteBuffer(&sRec[S19_DATA_BYTE2_OFFSET], pui8Buffer, (ui8ByteCount >> 1));

         // Create block
         i32MemoryblockInit(pxMemory, ui32Temp, (ui8ByteCount >> 1), pui8Buffer);
      }
      break;

   // Reserved
   case S19_HEADER_S4:
      break;

   // Count
   case S19_HEADER_S5:
      if (ui8ByteCount <= (S19_ADDRESS_BYTE1_OFFSET))
      {
         i32Log("S19::S5:Error: Record size");
      }
      else
      {
         ui32Temp  = ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE0_OFFSET]) << 8;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE1_OFFSET]);
         i32Log("S19::Count:%d", ui32Temp);
      }
      break;

   // Count
   case S19_HEADER_S6:
      if (ui8ByteCount <= (S19_DATA_BYTE0_OFFSET))
      {
         i32Log("S19::S6:Error: Record size");
      }
      else
      {
         ui32Temp  = ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE0_OFFSET]) << 16;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE1_OFFSET]) << 8;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_DATA_BYTE0_OFFSET]);
         i32Log("S19::S6:Count:%d", ui32Temp);
      }
      break;

   // 32-bit Start Address
   case S19_HEADER_S7:
      if (ui8ByteCount <= (S19_DATA_BYTE1_OFFSET))
      {
         i32Log("S19::S7:Error: Record size");
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
         i32Log("S19::S8:Error: Record size");
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
         i32Log("S19::S9:Error: Record size");
      }
      else
      {
         ui32Temp  = ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE0_OFFSET]) << 16;
         ui32Temp |= ui32ConvertHexStringToByte(&sRec[S19_ADDRESS_BYTE1_OFFSET]) << 8;
      }
      break;
   }

   return(-1);
}