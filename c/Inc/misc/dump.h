#ifndef DUMP_H
#define DUMP_H


typedef struct
{
   uint32_t ui32BaseAddress;
   uint32_t ui32Size;
   uint8_t *pui8Data;
} Dump_t;

typedef enum
{
   eDumpStatusOk    = 0,
   eDumpStatusError = -1
} DumpStatus_e;

extern Dump_t *pxDumpCreate(uint32_t ui32BaseAddress, uint32_t ui32Size);
extern int32_t i32DumpDestroy(Dump_t *pxDump);
extern Dump_t *pxDumpGenerateFromMemory(Memory_t *pxMemory, uint8_t ui8FreeByte);
extern int32_t i32DumpCompare(Dump_t *pxOriginalDump, Dump_t *pxSecondaryDump);

#endif
