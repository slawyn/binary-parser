#ifndef FILE_H
#define FILE_H

#include "types.h"

/* Public types */
typedef enum
{
   UNKNOWN = 0x00,
   S19     = 0x01,
   HEX     = 0x02
} Filetype_e;

/* Public prototypes */
extern int32_t i32FileLoad(char *sFileFullPath, Memory_t *pxMemory);

#endif
