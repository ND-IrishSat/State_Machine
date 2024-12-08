#ifndef I2C_UTILS_H
#define I2C_UTILS_H

// Includes necessary headers
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>

// Defines the device address
#define DEVICE_ADDRESS 0x6B

// Function declarations
int read_register_data(int reg_addr, int length, unsigned char *data);
float get_voltage();

#endif // I2C_UTILS_H
