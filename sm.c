#include "sm.h"             // related header

#include <stdio.h>          // C system headers
#include <stdlib.h>
#include <string.h>

#include "pico/stdlib.h"    // other libraries' headers

#include "gps.h"            // our project's headers
#include "lora.h"

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
    if (gps_avail()) {
        current_state->next_state_func = &sm_process_gps;
        return 0;
    }
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


    typedef enum gps_state {    // track if current bytes are data we care about
        SEARCHING, LOAD_BUFFER, PROCESS_BUFFER 
    } gps_state;

    static gps_state state = SEARCHING;

    
    current_state->next_state_func = &sm_idle; 

    switch(state){
        case SEARCHING:
            gps_read(tempPointer); // pops char from gps and puts on to tempBuffer at position of pointer
            if (*tempPointer == '$') { state = LOAD_BUFFER; }
            break;

        case LOAD_BUFFER:
            gps_read(tempPointer); // pops char from gps and puts on to tempBuffer at position of pointer
            if (*tempPointer == ',') {
                state = PROCESS_BUFFER;
                break;
            } else {
               tempPointer++;
               break;
            }

         case PROCESS_BUFFER:
            *tempPointer = '\0'; // replace ',' with null character
            tempPointer = &tempBuffer[0]; // Set pointer to beginning of buffer

            // printf("Field Num: %d\n",fieldNum);
            // printf("tempBuffer: %s\n", tempBuffer);
            
            switch(fieldNum) { // check field number, process differently depending on where you are
                case 0: // Type of transmission
                    if (strcmp("GNGGA",tempBuffer)) {
                        state = SEARCHING;
                        //printf("Wrong string: %s\n\n",tempBuffer);
                        break;
                    } else {
                        state = LOAD_BUFFER;
                        //printf("Correct string: %s\n\n",tempBuffer);
                        fieldNum++;
                        break;
                    }

                case 1: // Time hhmmss.ss
                    // Get hours from tempBuffer
                    unsigned int timeInt = atof(tempBuffer); // converts the string to a float. Stores it in an int (truncating away the decimal)
                    hours = timeInt / 10000;               // 10.3020 truncated = 10
                    minutes = timeInt / 100 - hours * 100; // 103020/100 - 10*100 = 1030 (truncated) - 1000 = 30
                    seconds = timeInt % 100;               // 103020 % 100 = 20
                    // printf("timeInt: %d\n", timeInt);
                    // printf("hours: %d\n",hours);
                    // printf("minutes: %d\n", minutes);
                    // printf("seconds: %d\n\n", seconds);

                    state = LOAD_BUFFER;
                    fieldNum++; // increment field
                    break;

                case 2: // Latitude
                    lat = atof(tempBuffer) / 100.f;
                    //printf("latitude: %f\n\n",lat);
                    state = LOAD_BUFFER;
                    fieldNum++;
                    break;

                case 3: // N or S
                    northsouth = tempBuffer[0];
                    //printf("north or south: %c\n\n",northsouth);
                    state = LOAD_BUFFER;
                    fieldNum++;
                    break;

                case 4: // Longitude
                    longitude = atof(tempBuffer) / 100.f;
                    //printf("longitude: %f\n\n",longitude);
                    state = LOAD_BUFFER;
                    fieldNum++;
                    break;

                case 5: // E or W
                    eastwest = tempBuffer[0];
                    //printf("east or west: %c\n\n",eastwest);
                    state = LOAD_BUFFER;
                    fieldNum++;
                    break;

                case 6: // transmit, we don't care about fields 6+
                    // Reset
                    fieldNum = 0;
                    state = SEARCHING;

                    printf("Hours: %d, Minutes: %d, Seconds: %d, Lat: %f %c, Long: %f %c\n", 
                                hours, minutes, seconds, lat, northsouth, longitude, eastwest);

                    // If south/west, make lat/long negative
                    if (northsouth == 'S') {
                        lat = -lat;
                    } 

                    if (eastwest == 'W') {
                        longitude = -longitude;
                    } 

                    // Pack data into binary for transmit
                    memcpy(&current_state->c[0], &seconds_id, 1);
                    memcpy(&current_state->c[1], &lat, 8);
                    memcpy(&current_state->c[9], &longitude, 8);

                    // Transmit data if it is your turn, otherwise go back to idle
                    //if (seconds == seconds_id) {
                    if (seconds % 5 == 0) {
                        current_state->next_state_func = &sm_transmit_data; // this is a trivial function, but move on to transmit
                    } else {
                        current_state->next_state_func = &sm_idle;
                    }

                    return 0;
                    break;

                default:
                    fieldNum = 0;
                    state = SEARCHING;
                    current_state->next_state_func = &sm_idle;
                    break;

             }
             break;
      } 

    // switch (state) {
    //     case SEARCHING: // no dollar sign
    //         if (gps_read(tempPointer)) { 
    //             printf("ERROR trying gps_read in sm process gps case 0");
    //             return 1;
    //         };
    //         if (*tempPointer == '$') {
    //             state = LOAD_BUFFER;
    //         }
    //         break;

    //     case LOAD_BUFFER: // if we saw dollar sign, check for comma
    //         if (gps_read(tempPointer)) { 
    //             printf("ERROR trying gps_read in sm process gps case 1");
    //             return 1;
    //         };

    //         if (*tempPointer == ',') {
    //             state = 0;
    //             *tempPointer = '\0';
    //             tempPointer = &tempBuffer[0];
    //             if (strcmp(tempPointer, "GPGGA") == 0) {
    //                 //printf("YES!\n");
    //                 //printf("%s\n",tempPointer);
    //                 counter++;
    //                 if (counter % 5 == 0)
    //                 {
    //                     lat = 41.1234;
    //                     longitude = -86.2123;
    //                     //strcpy(current_state->c,"10 secs\n");

    //                     // Pack data into binary for transmit
    //                     memcpy(&current_state->c[0], &seconds_id, 1);
    //                     memcpy(&current_state->c[1], &lat, 8);
    //                     memcpy(&current_state->c[9], &longitude, 8);

    //                     current_state->next_state_func = &sm_transmit_data; 
    //                 }
    //             }
    //             // printf("%s\n",tempPointer);
    //         } 
    //         else {
    //             tempPointer++;
    //         }

    //         break;

    //     default:
    //         printf("NEVER BE HERE");
    //         break;
    // }

    return 0;
}

int sm_transmit_data(state_machine_t * const current_state){
    //printf("%s\n",current_state->c);
    lora_transmit(current_state->c, 17);
    current_state->next_state_func = &sm_idle;
    return 0;
}