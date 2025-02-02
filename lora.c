#include "lora.h"

#include "stdio.h"
#include "string.h"

#include "pico/stdlib.h"
#include "hardware\spi.h"

#include "sx126x_hal_context.h"
#include "sx126x.h"


//LoRa context is global so it can be accessed in an interrupt
// not volatile since it won't be changed in an interrupt
static const lora_spi_context_t lora_context = {
    .spihw = spi1,
    .nss_pin = LORA_NSS,
    .busy_pin = LORA_BUSY};


void on_lora_irq(uint gpio, uint32_t events){
    // acknowledge the IRQ
    sx126x_irq_mask_t irqs;
    sx126x_get_and_clear_irq_status( &lora_context, &irqs);
    // update state machine
    // can't have both at same time, either it received or transmitted data or timed out
    if (irqs & SX126X_IRQ_RX_DONE ) {
        //printf("Interrupt: RX done\n");
        printf("------ BEGIN RX ------\n");
        // Process data received
        static uint8_t seconds_id_read;
        static double lat_read;
        static double long_read;

        // Declare a variable to store buffer start point and size
        static sx126x_rx_buffer_status_t rx_buffer_status;

        sx126x_get_rx_buffer_status(&lora_context, &rx_buffer_status); // get buffer status

        static uint8_t temp[256]; // temp buffer to store received data in

        sx126x_read_buffer( &lora_context,
                                rx_buffer_status.buffer_start_pointer, // start reading here
                                temp,                         // put data here
                                17); // read this many bytes (could set rx_buffer_status.pld_len_in_bytes)


        // for (int i=0; i < 17; i++) {
        //     printf("%x", temp[i]);
        // }
        // printf("\n");

        // Pull data from binary buffer
        memcpy(&seconds_id_read, &temp[0], 1);
        memcpy(&lat_read, &temp[1], 8);
        memcpy(&long_read, &temp[9], 8);

        printf("RX: ID: %d, Lat: %f, Long: %f\n", seconds_id_read, lat_read, long_read);


        printf("------ END RX ------\n\n");

        sx126x_set_rx( &lora_context, 0); // set lora back to rx mode
    }
    if (irqs & SX126X_IRQ_TX_DONE) {
        printf("Interrupt: TX done\n");
        sx126x_set_rx( &lora_context, 0); // set lora back to rx mode
    }
    if (irqs & SX126X_IRQ_TIMEOUT ) {
        printf("Interrupt: RX timeout\n");
    }
}

void init_radio(const uint32_t lorafreq_hz,
                const int8_t power_dbm,
                sx126x_mod_params_lora_t * lora_mod_params) {
    sx126x_set_pkt_type(&lora_context, SX126X_PKT_TYPE_LORA);
    sx126x_set_rf_freq(&lora_context, lorafreq_hz);
    
    // Set the Power Amplifier parameters
    // Taken from the datasheet, optimal for sx1262 at 22 dBm
    const sx126x_pa_cfg_params_t pa_params = {
        .pa_duty_cycle = 0x04,
        .hp_max = 0x07,
        .device_sel = 0x00,
        .pa_lut =0x01,
    };
    sx126x_set_pa_cfg(&lora_context, &pa_params);
    sx126x_set_tx_params(&lora_context, power_dbm, SX126X_RAMP_200_US);

    sx126x_set_lora_mod_params(&lora_context, lora_mod_params);
    // Our module uses a radio frequency switch to switch between RX and TX
    sx126x_set_dio2_as_rf_sw_ctrl( &lora_context, true );
    // enable RX boost (10% higher current, maybe better performance)
    // not sure if it's worth it
    uint8_t boost_rx = 0x96;
    sx126x_write_register( &lora_context, 0x08AC, &boost_rx, 1);
}

void init_hardware() {
    // set up LoRa
    spi_init(spi1, 100 * 1000); // set up SPI at 100,000 kHz clock. Defaults Motorola CPOL=0, CPHA=0
    gpio_set_function(LORA_TX, GPIO_FUNC_SPI);
    gpio_set_function(LORA_RX, GPIO_FUNC_SPI);
    gpio_set_function(LORA_SCK, GPIO_FUNC_SPI);
    
    // Chip select is active-low, so we'll initialise it to a driven-high state
    gpio_init(LORA_NSS);
    gpio_set_dir(LORA_NSS, GPIO_OUT);
    gpio_put(LORA_NSS, 1);


    sx126x_mod_params_lora_t lora_mod_params = {
        .sf = SX126X_LORA_SF7, // spreading factor
        .bw = SX126X_LORA_BW_125, // bandwidth
        .cr = SX126X_LORA_CR_4_5, // coding rate
        .ldro = 0 // low data rate optimization
    };
    init_radio(LORA_FREQ_IN_HZ,     // freq in HZ
               LORA_POWER_IN_DBM,   // power in dBm
               &lora_mod_params);   //  modulation parameters

    // next, set up an IRQ for when a packet is received
    sx126x_set_dio_irq_params( &lora_context,
                               SX126X_IRQ_RX_DONE | SX126X_IRQ_TX_DONE | SX126X_IRQ_TIMEOUT,
                               SX126X_IRQ_RX_DONE | SX126X_IRQ_TX_DONE | SX126X_IRQ_TIMEOUT, // DIO1 will go high when IRQ_RX_DONE is triggered
                               SX126X_IRQ_NONE,    // DIO2 will not go high for any interrupt
                               SX126X_IRQ_NONE);   // DIO3 will not go high for any interrupt

    gpio_init(LORA_DIO1); // sets the pin to GPIO function and sets it to input by default
    gpio_set_irq_enabled_with_callback( LORA_DIO1,          // set up this pin as interrupt pin
                                        GPIO_IRQ_EDGE_RISE, // on rising edge, triger interrupt
                                        true,               // enable it immediately 
                                        &on_lora_irq);        // run this function when irq happens

    sx126x_pkt_params_lora_t lora_pkt_params = {
        .preamble_len_in_symb = 12, // default is 12
        .header_type          = SX126X_LORA_PKT_EXPLICIT, // maybe use implicit to save bytes
        .pld_len_in_bytes     = 255, // 255 for rx, otherwise actual payload length
        .crc_is_on            = true, // in case anyone wants to check
        .invert_iq_is_on      = false
    };
    sx126x_set_lora_pkt_params(&lora_context, &lora_pkt_params);

    sx126x_set_rx( &lora_context, 10000); // 10 second timeout
}


int lora_init() {
    init_hardware();
    return 0;
}

int lora_transmit(char * buffer, int num) {
    sx126x_pkt_params_lora_t lora_pkt_params = {
    .preamble_len_in_symb = 12, // default is 12
    .header_type          = SX126X_LORA_PKT_EXPLICIT, // maybe use implicit to save bytes
    .pld_len_in_bytes     = 255, // 255 for rx, otherwise actual payload length
    .crc_is_on            = true, // in case anyone wants to check
    .invert_iq_is_on      = false
    };

    // for (int i=0; i < 17; i++) {
    //         printf("%x", buffer[i]);
    //     }
    //     printf(" \n\n");

    sx126x_set_lora_pkt_params(&lora_context, &lora_pkt_params);
    sx126x_write_buffer(&lora_context, 0, buffer, num);
    // tx it!
    sx126x_set_tx(&lora_context, 0);
    return 0;
}
