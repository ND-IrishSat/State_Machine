#ifndef sm_h
#define sm_h

typedef struct state_machine state_machine_t;
typedef int state_func_t(state_machine_t * const);

struct state_machine {
    state_func_t * next_state_func;
    char c[256]; // data to pass between states
};

void sm_init(state_machine_t * const);

int sm_idle(state_machine_t * const);

int sm_detumble(state_machine_t * const);

int sm_launching(state_machine_t * const);

int sm_deployment(state_machine_t * const);

int sm_hibernate(state_machine_t * const);

int sm_sun_pointing(state_machine_t * const);

int sm_downlink(state_machine_t * const);

int sm_research_pointing(state_machine_t * const);

int sm_comms_pointing(state_machine_t * const);

int sm_process_gps(state_machine_t * const);

int sm_transmit_data(state_machine_t * const);

bool critical_power_check(state_machine_t * const);

bool below_half_power(state_machine_t * const);

bool sun_visible(state_machine_t * const);

bool doing_research(state_machine_t * const);

#endif