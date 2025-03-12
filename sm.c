#include "sm.h"             // related header

#include <stdio.h>          // C system headers
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

state_func_t sm_idle, sm_detumble, sm_launching, sm_deployment, sm_hibernate, sm_sun_pointing, sm_downlink, sm_research_pointing, sm_comms_pointing, sm_process_gps, sm_transmit_data;


void sm_init( state_machine_t * const sm_context){
    // Should it intialize the state machine's context to launching first, indtead??
    // Or are we assuming that we've already done all of that and now we're just chilling in space?

    // initializing the state machine's context
    sm_context->next_state_func = &sm_idle;
    sm_context->c[0] = '\0'; // just put a null character in c

    // we'll need to initialize the GPS "Driver"
    // the driver will be functions to access our GPS data
    // intialize will turn on the interrupts, set up a queue (ring buffer)
    // the driver will also have function to see if data is available and pop data from the buffer
}


// Example definition of state functions
int sm_idle(state_machine_t * const current_state) {
    bool in_sun = sun_visible();
    bool power_critical = critical_power_check();
    bool below_half = below_half_power();
    bool researching = doing_research();
    bool comms_station_pointing = pointing_comms();
    bool ground_station_visible_soon = gs_visible_soon();
    bool ground_station_visible = gs_visible();
    bool uplinking = is_uplinking();
    bool downlinking = is_downlinking();

    if (power_critical) {
        current_state->next_state_func = &sm_hibernate;
        return 0;
    }
    else{
        if (below_half) {
        if(in_sun){
            current_state->next_state_func = &sm_sun_pointing;
        }
        }
            if (ground_station_visible_soon){
                if(researching)
                {
                    current_state->next_state_func = &sm_research_pointing;
                }
                else {
                    current_state->next_state_func = &sm_comms_pointing;
                }
            
            if (ground_station_visible){
                    if (uplinking) {
                        //INSERT UPLINKING CODE

                    }
                if (downlinking){
                    // Handle downlink activity
                }
            }
            else {
                return 0;
            }
            
        }
    
     }    
    

    

    

    else {
        best_effort_wfe_or_timeout(make_timeout_time_us(10 * 1000 * 1000)); // 10 seconds sleep
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

bool critical_power_check(){
    if (battery_power < 5) {
        return true;
    }
}

bool below_half_power(){
    if (battery_power < 50) {
        return true;
    }
}

bool sun_visible(){
    return sun_vis
}

bool doing_research(){
    return research
}

bool pointing_comms(){
    return pointing_to_comms
}

bool is_uplinking(){
    return uplinking
}

bool is_downlinking(){
    return downlinking
}

bool gs_visible_soon(){
    return gs_vis_soon
}

bool gs_visible(){
    return gs_vis_now
}