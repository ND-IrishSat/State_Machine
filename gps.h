#ifndef gps_h
#define gps_h

// #define UART_TX_PIN 16 // ND BOARD
// #define UART_RX_PIN 17 // ND BOARD

#define UART_TX_PIN 13 // ND BOARD
#define UART_RX_PIN 12 // ND BOARD


void gps_init(); // set up interrupts and buffer

int gps_avail(); // return 1 if data is available to read, 0 if buffer is full.

int gps_read(char *); // read a single character from buffer. put it in the memory address given as an argument. return 1 for error, 0 for not an error

#endif