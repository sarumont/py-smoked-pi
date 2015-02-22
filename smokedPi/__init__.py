import sys
import time

from multiprocessing import Process, Pipe, current_process
#from subprocess import Popen, PIPE, call

import pybald.temperature.PID as PID
from pybald.temperature import c_to_f, f_to_c
import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")


config = {
        "SPI": False,
        "SPI_PORT": 0,
        "SPI_DEVICE": 0,
        "CLK": 25,
        "CS": 24,
        "DO": 18,
        "SSR": 17,
        "cycle_time": 2.0
        }

if __name__ == "__main__":

    temp_in, temp_out = Pipe()
    ptemp = Process(name = "SmokedPi Temperature Poller", target=temp_poller, args=(temp_in))
    ptemp.daemon = True
    ptemp.start()

    heat_in, heat_out = Pipe()
    pheat = Process(name = "SmokedPi Heating Loop", target=heating_loop, args=(cycle_time, duty_cycle, pinNum, child_conn_heat))
    pheat.daemon = True
    pheat.start() 

    pid = PID()
    pid.setPoint(f_to_c(210))
    temp_ma_list = []

    while (True):
        readytemp = False
        while temp_in.poll():
            temp_C, tempSensorNum, elapsed = temp_in.recv()

            if temp_C == -99:
                print "Bad Temp Reading - retry"
                continue

            if (tempUnits == 'F'):
                temp = (9.0/5.0)*temp_C + 32
            else:
                temp = temp_C
                temp_str = "%3.2f" % temp
            readytemp = True
            break

        if readytemp == True:

            #smooth temp data
            temp_ma_list.append(temp)
            temp_ma = 0.0 #moving avg init
            while (len(temp_ma_list) > num_pnts_smooth):
                temp_ma_list.pop(0) #remove oldest elements in list

            for temp_pnt in temp_ma_list:
                temp_ma += temp_pnt
                temp_ma /= len(temp_ma_list)

            print "temp_ma = %.2f" % temp_ma

        if (readyPIDcalc == True):
            duty_cycle = pid.update(temp_ma)
            heat_in.send(duty_cycle)
            readyPIDcalc = False

        #if mode == "boil":
        #if (temp > boil_manage_temp) and (manage_boil_trigger == True): #do once
        #manage_boil_trigger = False
        #duty_cycle = boil_duty_cycle
        #parent_conn_heat.send([cycle_time, duty_cycle])

        print "Current Temp: %3.2f deg, Heat Output: %3.1f%%" % (c_to_f(temp), duty_cycle)
        readytemp == False
        while heat_in.poll(): #Poll Heat Process Pipe
            duty_cycle = heat_in.recv() #non blocking receive from Heat Process
            readyPIDcalc = True

def temp_poller(conn):
    """
    Polling loop to sample temperature and send it to the element loop

    :conn: pipe to communicate the temperature
    """
    p = current_process()
    print 'Starting:', p.name, p.pid
    if config["SPI"]:
        sensor = MAX31855.MAX31855(spi=SPI.SpiDev(config["SPI_PORT"], config["SPI_DEVICE"]))
    else:
        sensor = MAX31855.MAX31855(config["CLK"], config["CS"], config["DO"])

    while (True):
        t = time.time()
        time.sleep(.5) #.1+~.83 = ~1.33 seconds

        temp = sensor.readTempC()
        elapsed = "%.2f" % (time.time() - t)
        conn.send([num, tempSensorNum, elapsed])


def get_cycle_times(cycle_time, duty_cycle):
    """
    Calculates the on and off time for a cycle

    :cycle_time: Total cycle time
    :duty_cycle: Duty cycle (1-100)
    """
    duty = duty_cycle/100.0
    on_time = cycle_time*(duty)
    off_time = cycle_time*(1.0-duty)
    return [on_time, off_time]

def heating_loop(conn):
    #cycle_time, duty_cycle, conn):
    """
    A process to control the heating element to maintain the temperature utilizing PID

    :conn: pipe to communicate the calculated duty cycle
    """
    p = current_process()
    print 'Starting:', p.name, p.pid

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config["SSR"], GPIO.OUT, initial=GPIO.LOW)
    try:
        while (True):
            while (conn.poll()):
                duty_cycle = conn.recv()
                conn.send(duty_cycle)

                if duty_cycle == 0:
                    GPIO.output(config["SSR"], GPIO.LOW)
                    time.sleep(config["cycle_time"])
                elif duty_cycle == 100:
                    GPIO.output(config["SSR"], GPIO.HIGH)
                    time.sleep(config["cycle_time"])
                else:
                    on_time, off_time = get_cycle_times(config["cycle_time"], duty_cycle)
                    GPIO.output(config["SSR"], GPIO.HIGH)
                    time.sleep(on_time)
                    GPIO.output(config["SSR"], GPIO.LOW)
                    time.sleep(off_time)
    finally:
        GPIO.output(config["SSR"], GPIO.LOW)
        GPIO.cleanup(config["SSR"])

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
