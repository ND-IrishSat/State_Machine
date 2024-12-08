
#include <stdbool.h>
#include <stdio.h>
#include "sample_state_functions.h"
#include "i2c_utils.h"

typedef void (*stateFuncPtr)(void);

// Define all events
typedef enum transit_event{ 
    EVT_NO_EVENT,
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


// Define all states
void idle(void);
void detumbling(void);
void deploySolar(void);
void lowChargeSunPointing(void);
void uplinkDownlink(void);
void payload(void);
void hibernate(void);

// Define a row of STM
typedef struct fc_stm {
    stateFuncPtr curr_state;
    transit_event trig_event;
    stateFuncPtr next_state;
} fc_stm_row;

static transit_event eCurrentEvent = EVT_NO_EVENT;
static stateFuncPtr stCurrentState = idle;
// Used to flag first entry to a state
static bool bIsStateFirstEntry = false;
// Used to flag an imminent exit from the state
static bool bIsStateAboutToExit = false;

fc_stm_row fc_stm[] = {
    {idle, LAUNCH_COMPLETE_EVT, detumbling},
    {detumbling, DETUMBLING_COMPLETE_EVT, deploySolar},
    {deploySolar, DEPLOYMENT_COMPLETE_EVT, lowChargeSunPointing},
    
    // low charge state transitions
    {lowChargeSunPointing, CRIT_BATTERY_EVT, hibernate},
    {lowChargeSunPointing, LOW_CHARGE_EVT, lowChargeSunPointing},
    {lowChargeSunPointing, ABOVE_COMMS_EVT, uplinkDownlink},
    {lowChargeSunPointing, NOT_ABOVE_COMMS_EVT, lowChargeSunPointing},
    {lowChargeSunPointing, DOING_RESEARCH_EVT, payload},
    {lowChargeSunPointing, NOT_DOING_RESEARCH_EVT, lowChargeSunPointing},

    // Down/Up link operations
    {uplinkDownlink, DOING_RESEARCH_EVT, payload},
    {uplinkDownlink, NOT_DOING_RESEARCH_EVT, lowChargeSunPointing},

    // Payload operations
    {payload, DOING_RESEARCH_EVT, payload},
    {payload, NOT_DOING_RESEARCH_EVT, lowChargeSunPointing},

    // Hibernate transitions
    {hibernate, LOW_CHARGE_EVT, lowChargeSunPointing},
    {hibernate, CRIT_BATTERY_EVT, hibernate}
};

// variables for state machine
int state_of_charge = 100;
int battery_temp = 0;
bool above_comms;
bool doing_research;
stateFuncPtr current_state = idle;


void StateMachineHandler()
{
    int idx = 0;
    if(EVT_NO_EVENT != eCurrentEvent)
    {
        for(;idx < sizeof(fc_stm)/sizeof(fc_stm); idx++)
        {
            if( (fc_stm[idx].curr_state == stCurrentState) &&
                (fc_stm[idx].trig_event == eCurrentEvent))
            {
                /// Clear event 
                eCurrentEvent = EVT_NO_EVENT;
                /// Notify the state that exit is imminent;
                bIsStateAboutToExit = true;
                stCurrentState();
                // Move to new state
                stCurrentState = stStm[idx].next_state;
                // Flag that this is the first entry to the state
                bIsStateFirstEntry = true
            }
        }
    }

    if(NULL != stCurrentState)
    {
        /// Run the state
        stCurrentState();
        /// Unflag first entry
        bIsStateFirstEntry = false;
    }
};

int main()
{
    while(true)
    {
        StateMachineHadnler();
    }
};
