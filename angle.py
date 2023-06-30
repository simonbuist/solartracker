import numpy as np
import datetime as d
import geocoder as g
from sun import sunPosition

# https://www.nrel.gov/docs/fy13osti/58891.pdf
def optimalRotationInternal(axisTilt, axisAzimuth, sunElevation, sunAzimuth, limit):
    axisTilt = np.radians(axisTilt)
    axisAzimuth = np.radians(axisAzimuth)
    
    sunZenith = np.radians(90 - sunElevation)
    
    sunAzimuthRadians = np.radians(sunAzimuth)
        
    arg = np.sin(sunZenith)*np.sin(sunAzimuthRadians-axisAzimuth)/ \
            (np.sin(sunZenith)*np.cos(sunAzimuthRadians-axisAzimuth)*np.sin(axisTilt) \
             + np.cos(sunZenith)*np.cos(axisTilt))
    
    phi = np.where((arg < 0) & ((sunAzimuthRadians-axisAzimuth) > 0) , 180, 
            np.where((arg > 0) & ((sunAzimuthRadians-axisAzimuth) < 0), -180,0))
    
    
    R = np.degrees(np.arctan(arg)) + phi
    
    R[R>limit] = limit
    R[R<-limit] = -limit
    
    return R

def surfaceTilt(axisRotation, axisTilt):
    axisTilt = np.radians(axisTilt)
    Rrad = np.radians(axisRotation)
    zenith = np.arccos(np.cos(Rrad)*np.cos(axisTilt))
    return np.degrees(zenith)

# must calculate surfaceTilt first
def surfaceAzimuth(axisRotation, surfaceTilt, axisAzimuth):
    axisRotationRadians = np.radians(axisRotation)
    surfaceTiltRadians = np.radians(surfaceTilt)
    axisAzimuth = np.radians(axisAzimuth)
    
    surfaceAzimuth = axisAzimuth + np.arcsin(np.sin(axisRotationRadians)/np.sin(surfaceTiltRadians))
    return np.degrees(surfaceAzimuth)

def incidenceAngle(axisRotation, axisTilt, axisAzimuth, sunElevation, sunAzimuth): 
    axisRotation = np.radians(axisRotation)
    axisTilt = np.radians(axisTilt)
    axisAzimuth = np.radians(axisAzimuth)
    sunZenith = np.radians(90-sunElevation)
    sunAzimuth = np.radians(sunAzimuth)

    # find then the sun is above the horizon
    aboveHorizon = (sunElevation > 0)
    
    arg = np.cos(axisRotation)*(np.sin(sunZenith)*np.cos(sunAzimuth-axisAzimuth)*np.sin(axisTilt) \
                    +np.cos(sunZenith)*np.cos(axisTilt)) + \
                    np.sin(axisRotation)*np.sin(sunZenith)*np.sin(sunAzimuth-axisAzimuth)
    
    # the angle of incidence at all times
    angle = np.degrees(np.arccos(arg))

    # solar cells will not collect power while the sun is below the horizon
    adjusted = np.where(aboveHorizon, angle, 90)

    return adjusted


def optimalRotation(axisTilt, sunPosition, rotationMax):
    axisAzimuth = 180
    sunAzimuth = sunPosition[:, 0]
    sunTrueElevation = sunPosition[:, 1]
    sunElevation = np.empty((1440,))
    for i in range(1440):
        if (sunTrueElevation[i] > 0):
            sunElevation[i] = sunTrueElevation[i]
        else:
            sunElevation[i] = 0
    rotation = optimalRotationInternal(axisTilt, axisAzimuth, sunElevation, sunAzimuth, rotationMax)

    return rotation


def optimalTilt(sunPosition, tiltMax, rotationMax):
    sunAzimuth = sunPosition[:, 0]
    sunTrueElevation = sunPosition[:, 1]

    axisAzimuth = 180
    sunElevation = np.empty((1440,))
    for i in range(1440):
        if (sunTrueElevation[i] > 0):
            sunElevation[i] = sunTrueElevation[i]
        else:
            sunElevation[i] = 0

    # find the best angle to (to 10^1 precision)
    averageIncidence = {}
    for axisTilt in np.linspace(0, tiltMax, 10):
        incidence = incidenceAngle(optimalRotationInternal(axisTilt, axisAzimuth, sunElevation, sunAzimuth, rotationMax), axisTilt, axisAzimuth, sunElevation, sunAzimuth)
        averageIncidence[np.average(incidence)] = axisTilt

    # find the best angle to (to 10^-1 precision)
    fit = sorted(averageIncidence.keys())
    for axisTilt in np.linspace(averageIncidence[fit[0]] - 5, averageIncidence[fit[0]] + 5, 101):
        incidence = incidenceAngle(optimalRotationInternal(axisTilt, axisAzimuth, sunElevation, sunAzimuth, rotationMax), axisTilt, axisAzimuth, sunElevation, sunAzimuth)
        averageIncidence[np.average(incidence)] = axisTilt

    fit = sorted(averageIncidence.keys())

    return round(averageIncidence[fit[0]], 1)


def optimalAngleAnalytic(sunPosition):
    return


