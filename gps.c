#include "gps.h" // include its own header

#include "hardware/irq.h"  // for interrupt functions
#include "hardware/uart.h" // for uart functions
#include "pico/stdlib.h"

#include "buffer.h" // our own custom buffer!

// first, create our buffer where data from interrupts will land
// volatile file-static "global". This way interrupts can use it!
static buffer_256_t gps_buffer;


// RX interrupt handler
void on_uart_rx() {
    while (uart_is_readable(uart0)) {
        char ch = uart_getc(uart0);
        buffer_push( &gps_buffer, ch);
    }
}


void gps_init(){
    // set up our ring buffer (you could make your own .c and .h files for this too)
    buffer_init(&gps_buffer); // gps_buffer is file-static, so we can use it!
    
    
    // set up the uart. Same as uart_relay project
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART); // define these macros somewhere. I put it in the header file
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
    
    // initialize uart0 at 9600 baud (with other settings default "8-bit no parity")
    uart_init(uart0, 9600);
    //uart_set_fifo_enabled(uart0, true); // use internal buffer, optional

    // Set up a RX interrupt
    // We need to set up the handler first
    irq_set_exclusive_handler(UART0_IRQ, on_uart_rx);

    // Tell this core to look for uart0 IRQs
    irq_set_enabled(UART0_IRQ, true);

    // Tell UART0 to start sending interrupts - RX only
    uart_set_irq_enables(uart0, true, false);
}

int gps_read(char * c_ptr) {
    return buffer_pop(&gps_buffer, c_ptr); // returns 0 if an error
} // read a single character from buffer. put in in the memory address given as an argument. return 1 for error, 0 for not an error

int gps_avail(){
    return !(buffer_empty(&gps_buffer)); // return 1 if it's not empty
} // return 1 if data is available to read, 0 if buffer is full.