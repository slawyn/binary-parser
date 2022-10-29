#ifndef CONFIG_H
#define CONFIG_H

#include "misc/log.h"

#ifdef LOG_DEBUG
#define LogDebug(...)    i32Log(__VA_ARGS__)
#else
#define LogDebug(...)
#endif

#define LogNormal(...)    i32Log(__VA_ARGS__)
#define LogError(...)     i32Log(__VA_ARGS__)

/* Identifiers to use in .c files*/
#ifndef STATIC
#define STATIC    static
#endif

#ifndef PROTOTYPE
#define PROTOTYPE    static
#endif


#endif
