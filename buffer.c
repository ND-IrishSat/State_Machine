#include "buffer.h"

#include <stdio.h>

void buffer_init(buffer_256_t * buffer){
    buffer->w_ptr = &(buffer->data[0]);
    buffer->r_ptr = &(buffer->data[0]);
    buffer->data_available=0;
}

int buffer_full(buffer_256_t * buffer){
    return (buffer->data_available == 256);
}

int buffer_empty(buffer_256_t * buffer){
    //printf("%d\n", buffer->data_available);
    return (buffer->data_available == 0);
}

int buffer_peak(buffer_256_t * buffer, char * c_ptr){
    if (buffer_empty(buffer)) {
        printf("buffer empty\n");
        return 1; //ERROR
    }
    *c_ptr = *(buffer->r_ptr);
    return 0;
}

int buffer_push(buffer_256_t * buffer, char c){
    if (buffer_full(buffer)) {
        printf("buffer full\n");
        return 1; //ERROR, buffer is full
    }
    //printf("%c",*c);
    *(buffer->w_ptr) = c;
    //printf("%c",*(buffer->w_ptr));
    buffer->w_ptr = buffer->w_ptr+1;
    buffer->data_available++;
    if (buffer->w_ptr - &(buffer->data[0]) >= 256 ){
        buffer->w_ptr = &(buffer->data[0]);
    }
    return 0;
}

int buffer_pop(buffer_256_t * buffer, char * c_ptr){
    if (buffer_empty(buffer)) {
        printf("buffer empty\n");
        return 1; //ERROR, buffer is empty
    }
    *c_ptr = *(buffer->r_ptr);
    //printf("%c",*(buffer->r_ptr));
    buffer->r_ptr = buffer->r_ptr+1;
    buffer->data_available--;
    if (buffer->r_ptr - &(buffer->data[0]) >= 256 ){
        buffer->r_ptr = &(buffer->data[0]);
    }
    return 0;
}