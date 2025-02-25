#ifndef sm_h
#define sm_h

typedef struct state_machine state_machine_t;
typedef int state_func_t(state_machine_t * const);

struct state_machine {
    state_func_t * next_state_func;
    char c[256]; // data to pass between states
};

void sm_init( state_machine_t * const);

bool critical_power_check();

bool below_half_power();

bool sun_visible();

bool doing_research();

#endif