/* "structures.h" defines the look-up tables and KeyExpansion function
 * used in encrypt.cpp and decrypt.cpp
 */
#ifndef STRUCTURES_H
#define STRUCTURES_H

// Declare lookup tables as extern
extern unsigned char s[256];
extern unsigned char mul2[256];
extern unsigned char mul3[256];
extern unsigned char rcon[256];
extern unsigned char inv_s[256];
extern unsigned char mul9[256];
extern unsigned char mul11[256];
extern unsigned char mul13[256];
extern unsigned char mul14[256];

// Declare functions as extern
extern void KeyExpansionCore(unsigned char* in, unsigned char i);
extern void KeyExpansion(unsigned char* inputKey, unsigned char* expandedKeys);

#endif /* STRUCTURES_H */
