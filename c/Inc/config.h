#ifndef CONFIG_H
#define CONFIG_H

#ifdef LOG_DEBUG
#define LogDebug    i32Log
#else
#define LogDebug
#endif

#define LogNormal    i32Log
#define LogError     i32Log

#endif
