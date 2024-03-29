#ifndef DUMP_H
#define DUMP_H

#include "types.h"

/* Public types */
typedef struct
{
   uint32_t ui32BaseAddress;
   uint32_t ui32Offset;
   uint32_t ui32Size;
   uint8_t *pui8Data;
} Dump_t;

typedef enum
{
   eDumpStatusOk    = 0,
   eDumpStatusError = -1
} DumpStatus_e;

/* Public prototypes */
extern int32_t i32DumpAddBuffer(Dump_t *pxDump, uint32_t ui32Size, const uint8_t *pui8Data);
extern Dump_t *pxDumpCreate(uint32_t ui32BaseAddress, uint32_t ui32Size);
extern int32_t i32DumpDestroy(Dump_t *pxDump);
extern int32_t i32DumpCompare(Dump_t *pxOriginalDump, Dump_t *pxSecondaryDump);


#endif
