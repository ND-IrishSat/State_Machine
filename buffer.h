#ifndef buffer_h
#define buffer_h

typedef struct { // didn't give it a name. That's ok!
    volatile char data[256]; // a max 256 bytes in the buffer
    volatile char * volatile w_ptr;
    volatile char * r_ptr; // r_ptr should change the value
    volatile int data_available; // available to read. starts at 0. 
} buffer_256_t;
// the interrupt routine will change data[], the write pointer, and data available.
// therefore data is volatile. w_ptr is volatile, data available is volatile.
// and the things w_ptr and r_ptr point to are also volatile

void buffer_init(buffer_256_t *);

int buffer_empty(buffer_256_t *);

int buffer_push(buffer_256_t *, char);

int buffer_pop(buffer_256_t *, char *);

#endif