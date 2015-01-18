import sys
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855

config = {
        "CLK": 25,
        "CS": 24,
        "DO": 18
        }

# Define a function to convert celsius to fahrenheit.
def c_to_f(c):
        return c * 9.0 / 5.0 + 32.0


if __name__ == "__main__":
    print("Hello, world %d %d %d" % (config["CLK"], config["CS"], config["DO"]))
    sensor = MAX31855.MAX31855(config["CLK"], config["CS"], config["DO"])
    while True:
            temp = sensor.readTempC()
            internal = sensor.readInternalC()
            print 'Thermocouple Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp, c_to_f(temp))
            print '    Internal Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(internal, c_to_f(internal))
            time.sleep(1.0)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
