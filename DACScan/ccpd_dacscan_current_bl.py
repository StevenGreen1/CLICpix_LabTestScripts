#!/usr/bin/python
from ccdaq import *
from utils import *
from libdevice import dso9254a
import logging.config
import matplotlib.pyplot as plt

def clicpix_dac_scan():
    logging.config.fileConfig('logging.conf')
    cc=ccdaq(CLICpix=False)
#    scope=dso9254a.dso('192.168.222.2')
    fbase=os.path.join(cc.path,"scope",time_dir())
    mkdir(fbase)
    print "Chipboard ID:",cc.get_id()
    print "Temperature ", cc.temperature_get()

#    dac_list=("BLBIAS",    "VNNEW",   "BLRES",    "NU",
#           "VNCLIC",    "VN",      "VNFB",     "VNFOLL",
#           "VNLOAD",    "VNDAC",   "VPUP",     "VPCOMP",
#           "VNCOMPLD2", "VNCOMP",  "VNCOMPLD", "VNCOUT1",
#           "VNCOUT2",   "VNCOUT3", "VNBUFFER", "VPFOLL",
#           "VNBIAS",    "SOUT")
# Scan VPFOLL too!

    setNumber = str(sys.argv[1])
    dac = []
    meanVoltageList = []
    meanCurrentList = []

    try:
        cc.ccpd.dac_defaults()
        cc.ccpd.set_dacs()
        cc.voltage_set(ccpd.TP,0.5)
        cc.voltage_set(ccpd.BL,0.0)
        time.sleep(0.5)

        dac_name = 'dac_scan'

        currentList = []
        voltageList = []
        blList = []

        for chn in range(8):
            activeCurrentList = []
            activeVoltageList = []
            activeBLList = []

            for bl in np.arange(0,0.6,0.1):
                cc.voltage_set(ccpd.BL,bl)
                runningCurrent = 0
                runningVoltage = 0
                count = 0

                for pixel in [3]: #,7,11,15,19,23,27,31,35,39,43,47,51,55,59]:
                    cc.ccpd.sendConfig(mux_chn=pixel)
                    
                    current = 1000.0*cc.volreg_measure_current(chn) 
                    runningCurrent += current

                    voltage = cc.volreg_measure_voltage(chn)
                    runningVoltage += voltage

                    count += 1

                meanVoltage = runningVoltage / count
                meanCurrent = runningCurrent / count

                activeCurrentList.append(meanCurrent)
                activeVoltageList.append(meanVoltage)
                
                activeBLList.append(bl)

            currentList.append(activeCurrentList)
            voltageList.append(activeVoltageList)
            blList.append(activeBLList)

        printString = 'BLDAC0 : Current0 : Voltage0 : BLDAC1 : Current1 : Voltage1 : BLDAC2 : Current2 : Voltage2 : BLDAC3 : Current3 : Voltage3 : BLDAC4 : Current4 : Voltage4 : BLDAC5 : Current5 : Voltage5 : BLDAC6 : Current6 : Voltage6 : BLDAC7 : Current7 : Voltage7 \n'

        for idx, i in enumerate(blList[0]):
            printString += str(blList[0][idx]) + ' ' + str(currentList[0][idx]) + ' ' + str(voltageList[0][idx]) + ' ' 
            printString += str(blList[1][idx]) + ' ' + str(currentList[1][idx]) + ' ' + str(voltageList[1][idx]) + ' '
            printString += str(blList[2][idx]) + ' ' + str(currentList[2][idx]) + ' ' + str(voltageList[2][idx]) + ' '
            printString += str(blList[3][idx]) + ' ' + str(currentList[3][idx]) + ' ' + str(voltageList[3][idx]) + ' '
            printString += str(blList[4][idx]) + ' ' + str(currentList[4][idx]) + ' ' + str(voltageList[4][idx]) + ' '
            printString += str(blList[5][idx]) + ' ' + str(currentList[5][idx]) + ' ' + str(voltageList[5][idx]) + ' '
            printString += str(blList[6][idx]) + ' ' + str(currentList[6][idx]) + ' ' + str(voltageList[6][idx]) + ' '
            printString += str(blList[7][idx]) + ' ' + str(currentList[7][idx]) + ' ' + str(voltageList[7][idx]) + '\n'

        results_file = open('BLDacScan_Voltage_Current_SET' + setNumber + '.txt', "w")
        results_file.write(printString)
        results_file.close()

#        fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6), (ax7, ax8)) = plt.subplots(4, 2, sharex=True, sharey=False)
#        fig.set_size_inches(16, 12)
#        ax1.scatter(blList[0], currentList[0])
#        ax1.set_title('Power Supply 0 Current SET ' + setNumber)
#        ax1.set_ylabel('Current [mV]')
#        ax1.ticklabel_format(useOffset=False)
#        ax2.scatter(blList[1], currentList[1])
#        ax2.set_title('Power Supply 1 Current SET ' + setNumber)
#        ax2.ticklabel_format(useOffset=False)
#        ax2.set_ylabel('Current [mA]')
#        ax3.scatter(blList[2], currentList[2])
#        ax3.set_title('Power Supply 2 Current SET ' + setNumber)
#        ax3.ticklabel_format(useOffset=False)
#        ax3.set_ylabel('Current [mA]')
#        ax4.scatter(blList[3], currentList[3])
#        ax4.set_title('Power Supply 3 Current SET ' + setNumber)
#        ax4.ticklabel_format(useOffset=False)
#        ax4.set_ylabel('Current [mA]')
#        ax5.scatter(blList[4], currentList[4])
#        ax5.set_title('Power Supply 4 Current SET ' + setNumber)
#        ax5.ticklabel_format(useOffset=False)
#        ax5.set_ylabel('Current [mA]')
#        ax6.scatter(blList[5], currentList[5])
#        ax6.set_title('Power Supply 5 Current SET ' + setNumber)
#        ax6.ticklabel_format(useOffset=False)
#        ax6.set_ylabel('Current [mA]')
#        ax7.scatter(blList[6], currentList[6])
#        ax7.set_title('Power Supply 6 Current SET ' + setNumber)
#        ax7.ticklabel_format(useOffset=False)
#        ax7.set_xlabel('DAC [BL]')
#        ax7.set_ylabel('Current [mA]')
#        ax8.scatter(blList[7], currentList[7])
#        ax8.set_title('Power Supply 7 Current SET ' + setNumber)
#        ax8.ticklabel_format(useOffset=False)
#        ax8.set_ylabel('Current [mA')
#        ax8.set_xlabel('DAC [BL]')
#        plt.savefig('bldac_scan_powersupplycurrents_SET' + setNumber + '.png')
#        plt.clf()

#        fig2, ((ax21, ax22), (ax23, ax24), (ax25, ax26), (ax27, ax28)) = plt.subplots(4, 2, sharex=True, sharey=False)
#        fig2.set_size_inches(16, 12)
#        ax21.scatter(blList[0], voltageList[0])
#        ax21.set_title('Power Supply 0 Voltage SET ' + setNumber)
#        ax21.set_ylabel('Voltage [V]')
#        ax21.ticklabel_format(useOffset=False)
#        ax22.scatter(blList[1], voltageList[1])
#        ax22.set_title('Power Supply 1 Voltage SET ' + setNumber)
#        ax22.ticklabel_format(useOffset=False)
#        ax22.set_ylabel('Voltage [V]')
#        ax23.scatter(blList[2], voltageList[2])
#        ax23.set_title('Power Supply 2 Voltage SET ' + setNumber)
#        ax23.ticklabel_format(useOffset=False)
#        ax23.set_ylabel('Voltage [V]')
#        ax24.scatter(blList[3], voltageList[3])
#        ax24.set_title('Power Supply 3 Voltage SET ' + setNumber)
#        ax24.ticklabel_format(useOffset=False)
#        ax24.set_ylabel('Voltage [V]')
#        ax25.scatter(blList[4], voltageList[4])
#        ax25.set_title('Power Supply 4 Voltage SET ' + setNumber)
#        ax25.ticklabel_format(useOffset=False)
#        ax25.set_ylabel('Voltage [V]')
#        ax26.scatter(blList[5], voltageList[5])
#        ax26.set_title('Power Supply 5 Voltage SET ' + setNumber)
#        ax26.ticklabel_format(useOffset=False)
#        ax26.set_ylabel('Voltage [V]')
#        ax27.scatter(blList[6], voltageList[6])
#        ax27.set_title('Power Supply 6 Voltage SET ' + setNumber)
#        ax27.ticklabel_format(useOffset=False)
#        ax27.set_xlabel('DAC [BL]')
#        ax27.set_ylabel('Voltage [V]')
#        ax28.scatter(blList[7], voltageList[7])
#        ax28.set_title('Power Supply 7 Voltage SET ' + setNumber)
#        ax28.ticklabel_format(useOffset=False)
#        ax28.set_ylabel('Voltage [V]')
#        ax28.set_xlabel('DAC [BL]')
#        plt.savefig('bldac_scan_powersupplyvoltages_SET' + setNumber + '.png')

    except KeyboardInterrupt:
        print "Exiting ..."

if __name__ == '__main__':
  clicpix_dac_scan()

