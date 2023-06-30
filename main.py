import serial as s
import datetime as d
import math as m
import geocoder as g
import numpy as np
from sun import sunPosition
from angle import optimalRotation, optimalTilt

def indexFromTime(datetime):
    return datetime.hour * 60 + datetime.minute

adjustmentInterval = 30
rotationMax = 50 
tiltMax = 90
portOutName = "COM7"
comm_rate = 115200

timeNowUTC = d.datetime.utcnow()
timeNow = d.datetime.now()
location = g.ip("me")

# get array of sun position for each minute of the current day
time_zone = timeNowUTC.hour - timeNow.now().hour
hrs = np.arange(0+time_zone,24+time_zone)
mins = np.arange(0,60)
sunPos = np.array([sunPosition(timeNowUTC.year, timeNowUTC.month, timeNowUTC.day, hr, mn, 0, location.lat, location.lng) 
                    for hr,mn in zip(np.repeat(hrs,60),np.tile(mins,24))])

# get optimal tilt for the day
tilt = optimalTilt(sunPos, tiltMax, rotationMax)
print(f"Set the panel to tilt {tilt}")


rotation = optimalRotation(tilt, sunPos, rotationMax)

# timeIndex = timeNow.hour * 60 + timeNow.minute
timeIndex = 11 * 60 + timeNow.minute
positions = [rotation[timeIndex]]
while positions[-1] != rotationMax or timeIndex < 12 * 60:
    timeIndex += adjustmentInterval
    positions.append(round(rotation[timeIndex], 1))

steps = [round(pos * 5.66) for pos in positions] # 5.66 steps per degree

print(steps)

ser = s.Serial(portOutName, comm_rate)

print("connected")

# ser.write(bytes('check', 'utf-8'))

# commCheck = ""
# while commCheck != "ready":
#     commCheck = ser.readline().decode('utf-8')[:-1]
#     # print(f"-{ser.readline().decode('utf-8')[:-1]}-")

ser.write(f"{adjustmentInterval}.".encode('utf-8'))
ser.write(f"{len(positions)}.".encode('utf-8'))
for step in steps:
    ser.write(f"{step}.".encode('utf-8'))