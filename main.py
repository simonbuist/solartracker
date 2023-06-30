import serial as s
import datetime as d
import math as m
import geocoder as g
import numpy as np
from sun import sunPosition
from angle import optimalRotation, optimalTilt

# change settings as necessary
adjustmentInterval = 30 # minutes between adjustments
rotationMax = 50 # furthest the surface can rotate on the axis
tiltMax = 90 # how far the axis can be angled from the horizontal
portOutName = "COM7" # bluetooth serial port
comm_rate = 115200 # bluetooth BAUD rate

# time and place
timeNowUTC = d.datetime.utcnow()
timeNow = d.datetime.now()
location = g.ip("me")

# get array of sun position for each minute of the current day
time_zone = timeNowUTC.hour - timeNow.now().hour
hrs = np.arange(0+time_zone,24+time_zone)
mins = np.arange(0,60)
sunPos = np.array([sunPosition(timeNowUTC.year, timeNowUTC.month, timeNowUTC.day, hr, mn, 0, location.lat, location.lng) 
                    for hr,mn in zip(np.repeat(hrs,60),np.tile(mins,24))])

# get optimal tilt for the day and wait until the user has adjusted it
tilt = optimalTilt(sunPos, tiltMax, rotationMax)
input(f"Set the panel to tilt {tilt} and hit \"enter\" when ready")

# get the optimal rotation for each minute of the day based on chosen tilt
rotation = optimalRotation(tilt, sunPos, rotationMax)

# find the first position for the panel
# timeIndex = timeNow.hour * 60 + timeNow.minute
timeIndex = 6 * 60 + timeNow.minute # testing code to set starting time
positions = [rotation[timeIndex]]

# get the position at each interval
while positions[-1] != rotationMax or timeIndex < 12 * 60:
    timeIndex += adjustmentInterval
    positions.append(round(rotation[timeIndex], 1))

# translate degrees of rotation to motor steps
steps = [round(pos * 5.66) for pos in positions] # 5.66 steps per degree

print(steps)

# connect to ESP32 via bluetooth
ser = s.Serial(portOutName, comm_rate)

print("connected")

# send the data to the panel, with each valued delimited by a .
ser.write(f"{adjustmentInterval}.".encode('utf-8'))
ser.write(f"{len(positions)}.".encode('utf-8'))
for step in steps:
    ser.write(f"{step}.".encode('utf-8'))
