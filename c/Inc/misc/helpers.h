#ifndef HELPERS_H
#define HELPERS_H

extern int32_t i32Log(const char *format, ...);
extern uint32_t ui32ConvertHexStringToByte(char *sHexNibbles);
extern uint32_t ui32ConvertHexStringToWord(char *sHexNibbles);
extern uint32_t ui32ConvertHexStringToDword(char *sHexNibbles);
extern void vConvertHexStringToByteBuffer(char *sHexNibbles, uint8_t *pui8Buffer, uint8_t ui8Size);

#endif
