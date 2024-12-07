// sample_state_functions.h

#include <stdio.h>
#include <string.h>

void trigger_event(transit_event event){
    eCurrentEvent = event;
}

void idle(){
    // idle
    printf("State: Idle\n");
}

void detumbling(){
    if(bIsStateFirstEntry)
    {
        /// Do stuff for first entry(state initialization stuff)
        printf("State: Detumbling\n");
        trigger_event(DETUMBLING_COMPLETE_EVT);   // Critical battery condition
    }

    if(bIsStateAboutToExit)
    {
        /// Handle exit(i.e free up resources)
        printf("Exiting Detumbling.");
    }

    // Need:
    // Sensors
    // Magnotorquers
    // Flight Computer
}

void deploySolar(){
    if(bIsStateFirstEntry)
    {
        /// Do stuff for first entry(state initialization stuff)
        printf("State: Deploying Solar Panels\n");
        trigger_event(DEPLOYMENT_COMPLETE_EVT);   // Critical battery condition
    }

    if(bIsStateAboutToExit)
    {
        /// Handle exit(i.e free up resources)
        printf("Exiting Deploy Solar");
    }
}

void lowChargeSunPointing(){
    if(bIsStateFirstEntry)
    {
        /// Do stuff for first entry(state initialization stuff)
        printf("State: Low Charge Sun Pointing\n");
        if (state_of_charge < 5){
            trigger_event(CRIT_BATTERY_EVT);   // Critical battery condition
        } 
        else if (battery_temp < 0){
            // heat up
            battery_temp = 1;
        } 
        else if (state_of_charge < 30) {
            trigger_event(LOW_CHARGE_EVT);
        } 
        else if (above_comms){
            trigger_event(ABOVE_COMMS_EVT);
        }
        else if (doing_research){
            trigger_event(DOING_RESEARCH_EVT);
        }
    }

    if(bIsStateAboutToExit)
    {
        /// Handle exit(i.e free up resources)
        printf("Exiting Low Charge Sun Pointing.");
    }

    // Need:
    // IMU
    // Magnetorquers
    // Flight Computer
    // Motors
}

void payload(){
    if(bIsStateFirstEntry)
    {
        /// Do stuff for first entry(state initialization stuff)
        printf("State: Payload\n");
        if (doing_research) {
            trigger_event(DOING_RESEARCH_EVT);
        }
        else {
            trigger_event(NOT_DOING_RESEARCH_EVT);
        }
    }

    if(bIsStateAboutToExit)
    {
        /// Handle exit(i.e free up resources)
        printf("Exiting Payload");
    }

    // Need:
    // IMU
    // Magnetorquers
    // Payload
    // Flight Computer
    // Motors CONDITIONALLY
}

void uplinkDownlink(){
    if(bIsStateFirstEntry)
    {
        // Do stuff for first entry(state initialization stuff)
        printf("State: Down/Up link\n");
        if (doing_research) {
            trigger_event(DOING_RESEARCH_EVT);
        }
        else {
            trigger_event(LOW_CHARGE_EVT);
        }
    }

    if(bIsStateAboutToExit)
    {
        /// Handle exit(i.e free up resources)
        printf("Exiting Down/Up link");
    }
}
   
void hibernate(){
    // Need:
    //honk shoo

    if (state_of_charge > 5) {
        transit_event(LOW_CHARGE_EVT);
    }
    else {
        transit_event(CRIT_BATTERY_EVT);
    }
}
