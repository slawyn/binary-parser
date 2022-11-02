#ifndef PARSERS_H
#define PARSERS_H

#include "misc/memory.h"


typedef int32_t (*Parser_j)(char *, size_t, Memory_t *);

/* Public prototypes */
extern int32_t i32S19Parse(char *sRec, size_t xSize, Memory_t *pxMemory);
extern int32_t i32HexParse(char *sRec, size_t xSize, Memory_t *pxMemory);

#endif
