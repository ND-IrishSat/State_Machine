#include "i2c_utils.h"

int i2c_fd;

int read_register_data(int reg_addr, int length, unsigned char *data) {
    i2c_fd = open("/dev/i2c-1", O_RDWR);
    if (i2c_fd < 0) {
        perror("Failed to open the i2c bus.\n");
        return -11;
    }

    if (ioctl(i2c_fd, I2C_SLAVE, DEVICE_ADDRESS) < 0) {
        perror("Failed to acquire bus access and/or talk to slave.\n");
        return -1;
    }

    // Write the register address
    if (write(i2c_fd, &reg_addr, 1) != 1) {
        perror("Failed to write to the i2c bus.\n");
        return -1;
    }

    // Read data
    if (read(i2c_fd, data, length) != length) {
        perror("Failed to read from the i2c bus.\n");
        return -1;
    }
    close(i2c_fd);
    return 0;
}

float get_voltage() {
    unsigned char data[2] = {0};

    if (read_register_data(0x3B, 2, data) != 0) {
        return -1.0; // Error value
    }

    int raw_value = (data[0] << 8) | data[1];
    return raw_value * 0.001f; // Convert to volts (mV to V)
}
