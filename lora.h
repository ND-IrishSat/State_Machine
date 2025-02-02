#ifndef lora_h
#define lora_h

// Class board
// #define LORA_NSS  10
// #define LORA_DIO1 9
// #define LORA_BUSY 15
// #define LORA_TX   11  // SPI1
// #define LORA_RX   12  // SPI1
// #define LORA_SCK  14  // SPI1

// IRIS Board
#define LORA_DIO1 24
#define LORA_BUSY 25
#define LORA_SCK 26
#define LORA_RX 27 // could be TX or RX, not sure need to check
#define LORA_TX 28 // ^^
#define LORA_NSS 29

#define LORA_FREQ_IN_HZ (909*1000*1000) // 903 MHz
#define LORA_POWER_IN_DBM 22 // 22 max


int lora_init(); // Initialize lora
int lora_transmit(char *, int); // transmit data


#endif // lora_h