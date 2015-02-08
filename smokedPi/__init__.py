import sys
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

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
    if config["SPI"]:
        sensor = MAX31855.MAX31855(spi=SPI.SpiDev(config["SPI_PORT"], config["SPI_DEVICE"]))
    else:
        sensor = MAX31855.MAX31855(config["CLK"], config["CS"], config["DO"])

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(config["SSR"], GPIO.OUT, initial=GPIO.LOW)

    GPIO.output(config["SSR"], GPIO.HIGH)

    while True:
        temp = sensor.readTempC()
        internal = sensor.readInternalC()
        print 'Thermocouple Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp, c_to_f(temp))
        print '    Internal Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(internal, c_to_f(internal))
        time.sleep(1.0)


    GPIO.cleanup(config["SSR"])

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
