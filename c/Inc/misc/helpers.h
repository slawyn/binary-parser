#ifndef HELPERS_H
#define HELPERS_H

/* Public Dependencies */
#include "types.h"
#include "misc/memory.h"
#include "misc/dump.h"

/* Public Prototypes */
extern int32_t i32Log(const char *format, ...);
extern uint32_t ui32ConvertHexStringToByte(char *sHexNibbles);
extern uint32_t ui32ConvertHexStringToWord(char *sHexNibbles);
extern uint32_t ui32ConvertHexStringToDword(char *sHexNibbles);
extern void vConvertHexStringToByteBuffer(char *sHexNibbles, uint8_t *pui8Buffer, uint8_t ui8Size);
extern Dump_t * pxConvertMemoryToDump(Memory_t *pxMemory, uint8_t ui8FreeByte);

#endif
