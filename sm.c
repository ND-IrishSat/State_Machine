#include "sm.h"             // related header

#include <stdio.h>          // C system headers
#include <stdlib.h>
#include <string.h>
#include <i2c_utils.h>

#include "pico/stdlib.h"    // other libraries' headers

state_func_t sm_idle, sm_process_gps, sm_transmit_data;


void sm_init( state_machine_t * const sm_context){
    // initializing the state machine's context
    sm_context->next_state_func = &sm_idle;
    sm_context->c[0] = '\0'; // just put a null character in c

    // we'll need to initialize the GPS "Driver"
    // the driver will be functions to access our GPS data
    // intialize will turn on the interrupts, set up a queue (ring buffer)
    // the driver will also have function to see if data is available and pop data from the buffer
    gps_init();
    lora_init();
}


// Example definition of state functions
int sm_idle(state_machine_t * const current_state){
    //absolute_time_t timeout_time; // the maximum we'll sleep before double checking, in microsecs
   
    else {
        // sleep a little bit!
        // 9600 baud = 9600 characters / sec. 256 characters fill up in
        // 256/9600 seconds = 27 ms. So check more frequently
        //sleep_ms(10); // every 10 ms wake up. If too long, error will happen!

        // sleep_ms is "busy wait" -- the MCU is still running at full speed and power
        // a better way is to use "wake from event" (wfe), it goes to a lower-power state until event happens
        // Events = interrupts or some signal we code up
        // absolute_time_t timeout_time = make_timeout_time_us(1000*1000); 
        best_effort_wfe_or_timeout( make_timeout_time_us(10*1000*1000) ); // 10 seconds!?!? wfe is powerful!
        return 0;
    }
}

int sm_process_gps(state_machine_t * const current_state){
    static char tempBuffer[128]; // pointer to buffer to store gps data in
    static char * tempPointer = &tempBuffer[0]; // pointer to buffer
    static int counter = 0; // counter to transmit every 10 seconds
    // Define variables to store gps data
    static double lat, longitude;
    static char eastwest, northsouth; 
    static uint8_t hours, minutes; 
    static uint8_t seconds;
    static const uint8_t seconds_id = 35; // transmit id

    static int fieldNum = 0; // tracks which field we are currently processing 
    
    current_state->next_state_func = &sm_idle; 

    
                    if (seconds % 5 == 0) {
                        current_state->next_state_func = &sm_transmit_data; // this is a trivial function, but move on to transmit
                    } else {
                        current_state->next_state_func = &sm_idle;
                    }

                    return 0;;

        
 } 

int sm_transmit_data(state_machine_t * const current_state){
    //printf("%s\n",current_state->c);
    current_state->next_state_func = &sm_idle;
    return 0;
}