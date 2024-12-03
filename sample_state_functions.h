// sample_state_functions.h

#include "i2c_utils.h"
#include <stdio.h>
#include <string.h>


void idle(){
    // idle
    printf("State: Idle\n");
}

void deploy(){

}

void detumbling(){
    printf("State: Detumbling\n");
    // Need:
    // Sensors
    // Magnotorquers
    // Flight Computer
}

void deploySolar(){
    printf("Deploying Solar Panels\n");
    if (state_of_charge < 5){
        current_state = sleep; // Critical battery condition
    }
}

void idleWithSun(){
    // Need:
    // IMU
    // Magnetorquers
    // Flight Computer
    // Solar Panel DONE ONCE
    // Antenna Deployment DONE ONCE

}
void idleWithoutSun(){
    // Need:
    // IMU
    // Magnetorquers
    // Flight Computer
    // Heat CONDITIONALLY
}
void payload(){
    // Need:
    // IMU
    // Magnetorquers
    // Payload
    // Flight Computer
    // Motors CONDITIONALLY
}
void uplinkDownlink(){
    // Need:
    // IMU
    // Magnetorquers
    // Flight Computer
    // Motors
    // Sidekiq Z2
}
void lowChargeSunPointing(){
    if (state_of_charge < 5){
        current_state = sleep; // Critical battery condition
    }
    // Need:
    // IMU
    // Magnetorquers
    // Flight Computer
    // Motors
}
   
void sleep(){
    // Need:
    //honk shoo
}
