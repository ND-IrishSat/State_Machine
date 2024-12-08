#include<stdio.h>
#include "i2c_utils.h"

typedef void (*stateFuncPtr)(void);

typedef enum transit_event{ 
    NO_EVT,
    LAUNCH_COMPLETE_EVT,
    DETUMBLING_COMPLETE_EVT,
    DEPLOYMENT_COMPLETE_EVT,
    CRIT_BATTERY_EVT,
    LOW_CHARGE_EVT,
    ABOVE_COMMS_EVT,
    NOT_ABOVE_COMMS_EVT,
    DOING_RESEARCH_EVT,
    NOT_DOING_RESEARCH_EVT
} transit_event;


void detumbling(void);
void payload(void);
void deploy(void);
void low_charge_sun_pointing(void);
void hibernate(void);
void payload(void);
void uplink_downlink(void);

typedef struct fc_stm {
    stateFuncPtr curr_state;
    transit_event trig_event;
    stateFuncPtr next_state;

} fc_stm;

void launching(void){

}

void detumbling(){
    // Need:
    // Sensors
    // Magnotorquers
    // Flight Computer
}

void deploy(){

}

void low_charge_sun_pointing(){
    // Need:
    // IMU
    // Magnetorquers
    // Flight Computer
    // Motors
}


void hibernate(){
    // Need:
    //honk shoo
}

void payload(){
    // Need:
    // IMU
    // Magnetorquers
    // Payload
    // Flight Computer
    // Motors CONDITIONALLY
}
void uplink_downlink(){
    // Need:
    // IMU
    // Magnetorquers
    // Flight Computer
    // Motors
    // Sidekiq Z2
}

static transit_event curr_evt = NO_EVT

fc_stm state_matrix = {
    {launching, LAUNCH_COMPLETE_EVT, detumbling},

};