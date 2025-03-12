#ifndef sm_h
#define sm_h

typedef struct state_machine state_machine_t;
typedef int state_func_t(state_machine_t * const);

struct state_machine {
    state_func_t * next_state_func;
    char c[256]; // data to pass between states
};

// Sensor Data Globals
extern int battery_power;
// change the rest to doubles that represent the actual sensors
extern bool sun_vis;
extern bool research;
extern bool pointing_to_comms;
extern bool uplinking;
extern bool downlinking;
extern bool gs_vis_soon;
extern bool gs_vis_now;

// States
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

// Transition Functions
bool critical_power_check(int battery_power);
bool below_half_power(int battery_power);
bool sun_visible(bool sun_vis);
bool doing_research(bool research);
bool pointing_comms(bool pointing_to_comms);
bool is_uplinking(bool uplinking);
bool is_downlinking(bool downlinking);
bool gs_visible_soon(bool gs_vis_soon);
bool gs_visible(bool gs_vis_now);

#endif