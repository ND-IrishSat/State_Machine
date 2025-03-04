// https://google.github.io/styleguide/cppguide.html#Names_and_Order_of_Includes
// Related header, C system headers, C++ standard library headers, other libraries' headers, your project's headers.
// Seperate section by spaces. Alphabetical within sections.

#include <stdio.h>
#include <stdlin.h>
#include "sm.h"             // our project's headers

int main()
{
    state_machine_t sm_context;
    sm_init(&sm_context); // initialize the GPS driver here

    char keyboard_input;
    
    while (1) {
        input = getchar();
        
        (*sm_context.next_state_func)( & sm_context);
    }
}

