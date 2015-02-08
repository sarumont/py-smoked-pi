import sys
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855

from pybald.temperature import c_to_f

config = {
        "SPI": False,
        "SPI_PORT": 0,
        "SPI_DEVICE": 0,
        "CLK": 25,
        "CS": 24,
        "DO": 18,
        "SSR": 17
        }

if __name__ == "__main__":
    print("Hello, world %d %d %d" % (config["CLK"], config["CS"], config["DO"]))
    if config["SPI"]:
        sensor = MAX31855.MAX31855(spi=SPI.SpiDev(config["SPI_PORT"], config["SPI_DEVICE"]))
    else:
        sensor = MAX31855.MAX31855(config["CLK"], config["CS"], config["DO"])

    while True:
            temp = sensor.readTempC()
            internal = sensor.readInternalC()
            print 'Thermocouple Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp, c_to_f(temp))
            print '    Internal Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(internal, c_to_f(internal))
            time.sleep(1.0)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
