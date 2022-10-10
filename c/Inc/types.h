#ifndef TYPES_H

typedef long long            int64_t;
typedef unsigned long long   uint64_t;

typedef unsigned int         uint32_t;
typedef int                  int32_t;

typedef unsigned short       uint16_t;
typedef short                int16_t;

typedef unsigned char        uint8_t;
typedef char                 int8_t;

typedef enum
{
   UNKNOWN = 0x00, S19 = 0x01, HEX = 0x02
} Filetype_e;

#define TRUE     1
#define FALSE    0

#define SIZEOF(x)    sizeof(x) / sizeof(x[0])

#endif
