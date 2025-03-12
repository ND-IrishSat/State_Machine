// https://google.github.io/styleguide/cppguide.html#Names_and_Order_of_Includes
// Related header, C system headers, C++ standard library headers, other libraries' headers, your project's headers.
// Seperate section by spaces. Alphabetical within sections.

#include <stdio.h>
#include <stdlin.h>
#include <stdbool.h>
#include "sm.h"             // our project's headers

// Sensor Data Globals
int battery_power = 100;
// change the rest to doubles that represent the actual sensors
bool sun_vis = false;
bool research = false;
bool pointing_to_comms = false;
bool uplinking = false;
bool downlinking = false;
bool gs_vis_soon = false;
bool gs_vis_now = false;

void toggle_variable(char input);

int main()
{
    state_machine_t sm_context;
    sm_init(&sm_context); // Initialize the FSM

    char input;
    
    while (1) {
        printf("\nToggle a variable:\n");
        printf("c - Critical Power: %d\n", power_critical);
        printf("h - Below Half Power: %d\n", half_power);
        printf("s - Sun Visible: %d\n", sun);
        printf("r - Doing Research: %d\n", research);
        printf("p - Pointing to Comms: %d\n", pointing_to_comms);
        printf("u - Uplinking: %d\n", uplinking);
        printf("d - Downlinking: %d\n", downlinking);
        printf("v - GS Visible Soon: %d\n", gs_soon);
        printf("g - GS Visible: %d\n", gs_now);
        printf("q - Quit\n");
        printf("Enter choice: ");
        
        input = getchar();
        while (getchar() != '\n'); // Clear input buffer

        if (input == 'q') {
            printf("Exiting...\n");
            return 0;
        }

        toggle_variable(input);

        // Run the state machine based on updated conditions
        (*sm_context.next_state_func)(&sm_context);
    }

    return 0;
}

void toggle_variable(char input) {
    switch (input) {
        case 'b': scanf(%d, battery_power); break;
        case 's': sun = !sun; break;
        case 'r': research = !research; break;
        case 'p': pointing_to_comms = !pointing_to_comms; break;
        case 'u': uplinking = !uplinking; break;
        case 'd': downlinking = !downlinking; break;
        case 'v': gs_soon = !gs_soon; break;
        case 'g': gs_now = !gs_now; break;
        default: printf("Invalid input.\n"); return;
    }
    printf("Variable toggled!\n");
}
