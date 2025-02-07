#include "sm.h"             // related header

#include <stdio.h>          // C system headers
#include <stdlib.h>
#include <string.h>

state_func_t sm_idle, sm_detumble, sm_launching, sm_deployment, sm_hibernate, sm_sun_pointing, sm_downlink, sm_research_pointing, sm_comms_pointing, sm_process_gps, sm_transmit_data;


void sm_init( state_machine_t * const sm_context){
    // initializing the state machine's context
    sm_context->next_state_func = &sm_idle;
    sm_context->c[0] = '\0'; // just put a null character in c

    // we'll need to initialize the GPS "Driver"
    // the driver will be functions to access our GPS data
    // intialize will turn on the interrupts, set up a queue (ring buffer)
    // the driver will also have function to see if data is available and pop data from the buffer
}


// Example definition of state functions
int sm_idle(state_machine_t * const current_state){
    //absolute_time_t timeout_time; // the maximum we'll sleep before double checking, in microsecs 
   if(critical_power_check()) {
        current_state->next_state_func = &sm_process_gps;
        return 0;
    }
    if()


    else{
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

int sm_detumble(state_machine_t * const current_state){

}

int sm_launching(state_machine_t * const current_state){

}

int sm_deployment(state_machine_t * const current_state){

}

int sm_hibernate(state_machine_t * const current_state){

}

int sm_sun_pointing(state_machine_t * const current_state){

}

int sm_downlink(state_machine_t * const current_state){

}

int sm_research_pointing(state_machine_t * const current_state){

}

int sm_comms_pointing(state_machine_t * const current_state){

}

int sm_process_gps(state_machine_t * const current_state){

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