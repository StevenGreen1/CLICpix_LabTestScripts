#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import re
import numpy as np
from scipy.optimize import curve_fit
#from math import exp
import matplotlib.pyplot as plt

#setNumber = sys.argv[1]

folder_path = 'NoCLICpixSample'

def gaus(x,a,x0,sigma):
    return a*np.exp(-(x - x0)**2/(2*sigma**2))

# Find all .dat files in the given directory
from glob import glob
search = [y for x in os.walk(folder_path) for y in glob(os.path.join(x[0], '*frame*.dat'))]
#totFileSearch = [y for x in os.walk(folder_path) for y in glob(os.path.join(x[0], '*clkdiv9_ikrum25.dat'))]

resultsString = 'Results for NoCLICpix Sample\n'
resultsString += 'NoCLICpix\tPixel\tFrameNumber\tPulseHeight\tPulseHeightFromFit\tTroughStart\tTroughTime\t10%TimeStart\t10%TimeEnd\t90%TimeStart\t90%TimeEnd\n'

voltage = []
time = []

count = 0
tot = 0
totPlusx = 0
totPlusxPlusy = 0
totPlusy = 0
totMinusxPlusy = 0 
totMinusx = 0

scopeAmplitude = 0
frameCount = 0

# Record the tots
from collections import defaultdict
totDict = defaultdict(dict)
frameCountDict = defaultdict(dict)

#for totFileName in sorted(totFileSearch):
#    regex = re.compile("SET(.*?)/Pixel(.*?)/(.*?)")
#    q = regex.search(totFileName)
#
#    if q is not None:
#        pixelNumber = q.group(2)
#        totFile = open(totFileName, "r")
#
#        for line in totFile:
#            line = line.replace('+1x+1y_Pixel', 'gap2')
#            line = line.replace('-1x+1y_Pixel', 'gap4')
#            line = line.replace('+1x_Pixel', 'gap1')
#            line = line.replace('+1y_Pixel', 'gap3')
#            line = line.replace('-1x_Pixel', 'gap5')
#            line = line.replace('\n', '')
#            regex = re.compile("(\d\.\d+) (\d+) (\d+) Target_Pixel (\d+) (\d+) gap1 (\d+) (\d+) gap2 (\d+) (\d+) gap3 (\d+) (\d+) gap4 (\d+) (\d+) gap5 Event_Number (\d+)")
#            r = regex.search(line.replace('\n', ''))
#            if r is not None:
#                scopeAmplitude = r.group(1)
#                tot = r.group(2)
#                totPlusx = r.group(4)
#                totPlusxPlusy = r.group(6)
#                totPlusy = r.group(8)
#                totMinusxPlusy = r.group(10)
#                totMinusx = r.group(12)

#                frameCount = r.group(3)
#                eventNumber = r.group(14)
#                totDict[(int(pixelNumber),int(eventNumber),'target')] = tot 
#                totDict[(int(pixelNumber),int(eventNumber),'targetPlusx')] = totPlusx 
#                totDict[(int(pixelNumber),int(eventNumber),'targetPlusxPlusy')] = totPlusxPlusy
#                totDict[(int(pixelNumber),int(eventNumber),'targetPlusy')] = totPlusy
#                totDict[(int(pixelNumber),int(eventNumber),'targetMinusxPlusy')] = totMinusxPlusy
#                totDict[(int(pixelNumber),int(eventNumber),'targetMinusx')] = totMinusx
#                frameCountDict[(int(pixelNumber),int(eventNumber))] = frameCount

#for key, value in totDict.iteritems():
#    print key
#    print value

#sys.exit()

# Record Pluse Heights
for dataFileName in sorted(search):
    dataFile = open(dataFileName, 'r')

    regex = re.compile("NoCLICpixSample/Pixel(.*?)/(.*?)/frame(.*?).dat")
    q = regex.search(dataFileName)

    if q is not None:
        pixelNumber = q.group(1)
        eventNumber = int(q.group(3))

#        if eventNumber < 9990:
#            continue

        # Find the position of the trough
        runningVoltageTotal = 0
        runningVoltageTotalPreTrough = 0
        fractionDipForTroughStep = 0.01
        plateauVoltageFraction = 0.9
        numberTroughSteps = 0
        cutoffNumberTroughSteps = 1000
        numberOfStepsForAverage = 500
        endTroughTruncationSteps = 500
        startTroughFound = False
        endTroughFound = False

        troughVoltage = 100
        troughTime = 0
        startTroughTime = 0
        endTroughTime = 0
        meanVoltagePreTrough = 0
        riseTime = 0
        plateauVoltage = 0

        voltage = []
        time = []

        for line in dataFile:
            line = line.strip()
            columns = line.split()
            voltage.append(float(columns[1]))
            time.append(float(columns[0]))

        for i in xrange(1,len(time)):
            # Trough finding
            if (troughVoltage > voltage[i]):
                troughVoltage = voltage[i]
                troughTime = time[i]

            # Averaging to find baseline
            runningVoltageTotal = runningVoltageTotal + voltage[i]

            if (i >= cutoffNumberTroughSteps):
                runningVoltageTotalPreTrough = runningVoltageTotalPreTrough + voltage[i - cutoffNumberTroughSteps]

            # Find start of trough/peak
            if (i > numberOfStepsForAverage  and startTroughFound == False):
                runningAverage = runningVoltageTotal / i
                if (abs(voltage[i]/runningAverage - 1) > fractionDipForTroughStep):
                    numberTroughSteps = numberTroughSteps + 1
                    if (numberTroughSteps == cutoffNumberTroughSteps):
                        startTroughTime = time[i - cutoffNumberTroughSteps]
                        meanVoltagePreTrough = runningVoltageTotalPreTrough / (i - cutoffNumberTroughSteps)
                        startTroughFound = True
                else:
                    numberTroughSteps = 0

            # Find end of trough/peak
            if (endTroughFound == False and startTroughFound == True and (voltage[i] > meanVoltagePreTrough)):
                endTroughTime = time[i - endTroughTruncationSteps]
                endTroughFound = True

        riseTime = troughTime - startTroughTime
        troughVoltageChange = meanVoltagePreTrough - troughVoltage
        plateauVoltage = meanVoltagePreTrough - (troughVoltageChange * plateauVoltageFraction)

        plateauStartTime = 0
        plateauEndTime = 0
        plateauStartFound = False
        plateauEndFound = False

        for i in xrange(1,len(time)):
            if (voltage[i] < plateauVoltage and plateauStartFound == False and plateauEndFound == False):
                plateauStartTime = time[i] 
                plateauStartFound = True
            if (voltage[i] > plateauVoltage and plateauStartFound == True and plateauEndFound == False):
                for j in voltage[i+1:len(voltage)]:
                    if (j < plateauVoltage):
                        plateauEndFound = False 
                        break
                    else:
                        plateauEndTime = time[i]
                        plateauEndFound = True

        lowPlateauStartTime = 0
        lowPlateauEndTime = 0
        lowPlateauStartFound = False
        lowPlateauEndFound = False

        lowPlateauVoltageFraction = 0.1
        lowPlateauVoltage = meanVoltagePreTrough - (troughVoltageChange * lowPlateauVoltageFraction)

        for i in xrange(1,len(time)):
            if (voltage[i] < lowPlateauVoltage and lowPlateauStartFound == False and lowPlateauEndFound == False):
                lowPlateauStartTime = time[i]
                lowPlateauStartFound = True
            if (voltage[i] > lowPlateauVoltage and lowPlateauStartFound == True and lowPlateauEndFound == False):
                for j in voltage[i+1:len(voltage)]:
                    if (j < lowPlateauVoltage):
                        lowPlateauEndFound = False
                        break
                    else:
                        lowPlateauEndTime = time[i]
                        lowPlateauEndFound = True

        voltage = [ meanVoltagePreTrough - x for x in voltage ]

        voltageReduced = []
        timeReduced = []

        for idx, currentTime in enumerate(time):
            if (currentTime > plateauStartTime) and (currentTime < plateauEndTime):
                voltageReduced.append(voltage[idx])
                timeReduced.append(time[idx])

        try:
            count += 1
            if voltageReduced and timeReduced:
                popt, pcov = curve_fit(gaus, timeReduced, voltageReduced, p0 = [troughVoltageChange, troughTime, riseTime], maxfev=10000)

                troughTime = popt[1]
                troughVoltageChangeFromFit = popt[0]

#                plt.clf()
#                plt.plot(time,voltage,'r+:',label='data',alpha=0.2)
#                plt.plot(timeReduced,voltageReduced,'b+:',label='reduced data')
#                plt.plot(time,gaus(time,*popt),'g:',label='fit')
#                plt.axvline(plateauStartTime)
#                plt.axvline(plateauEndTime)
#                plt.axvline(lowPlateauStartTime)
#                plt.axvline(lowPlateauEndTime)
#                plt.legend()
#                plt.show()
#                plt.savefig('SET' + setNumber + '_Frame' + str(eventNumber) + '.png')

                resultsString += 'NoCLICpix\t' + str(pixelNumber) + '\t' + str(eventNumber) + '\t' + str(troughVoltageChange) + '\t' + str(troughVoltageChangeFromFit) + '\t' + str(startTroughTime) + '\t' + str(troughTime) + '\t' + str(lowPlateauStartTime) + '\t' + str(lowPlateauEndTime) + '\t' + str(plateauStartTime) + '\t' + str(plateauEndTime) + '\n'


#                print resultsString
#                plt.show()
#                print count

                if (count % 1000 == 0):
                    print 'For NoCLICpix Sample (Current Pixel ' + str(pixelNumber) + ') processed ' + str(count) + ' .dat files.'

                if (count % 5000 == 0):
                    resultsFileName = 'PixelCalibration_NoCLICpixSample_Detailed_v2.dat'
                    resultsFile = open(resultsFileName, "a")
                    resultsFile.write(resultsString)
                    resultsFile.close()
                    resultsString = ''
#                if (count > 100):
#                    break

        except RuntimeError:
            count += 1
            print("Error - curve_fit failed")

resultsFileName = 'PixelCalibration_NoCLICpixSample_Detailed_v2.dat' 
resultsFile = open(resultsFileName, "a")
resultsFile.write(resultsString)
resultsFile.close()

#===============================================
