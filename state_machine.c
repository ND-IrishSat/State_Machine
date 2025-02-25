// https://google.github.io/styleguide/cppguide.html#Names_and_Order_of_Includes
// Related header, C system headers, C++ standard library headers, other libraries' headers, your project's headers.
// Seperate section by spaces. Alphabetical within sections.

#include "sm.h"             // our project's headers


// this program uses the state machine to read in from the GPS and display it, constantly.
// Essentially does the same thing as uart_relay example
// it uses a gps driver (gps.c and gps.h) which in turn uses a ring buffer (buffer.c and buffer.h)

int main()
{
    state_machine_t sm_context;
    sm_init(&sm_context); // initialize the GPS driver here
    
    while (1) {
        (*sm_context.next_state_func)( & sm_context);
    }
}

