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

    dac = []
    meanVoltage = []

    try:
        cc.ccpd.dac_defaults()
        cc.ccpd.set_dacs()
        cc.voltage_set(ccpd.TP,0.5)
        cc.voltage_set(ccpd.BL,0.0)
        time.sleep(0.5)

        dac_name = 'dac_scan'

        current1 = []

        for bl in np.arange(0,0.6,0.005):
            cc.voltage_set(ccpd.BL,bl)

            runningVoltage = 0
            count = 0

            for pixel in [3]: #,7,11,15,19,23,27,31,35,39,43,47,51,55,59]:
                cc.ccpd.sendConfig(mux_chn=pixel)
                
#                for code in range(64):
#                    cc.ccpd.dacs['VPFOLL']=code
#                    cc.ccpd.set_dacs()
#                for acq in range(1):
#                    fn=os.path.join(fbase,"chn%02d_%03d.dat"%(pixel,acq))
#                    print " ->",fn
#                    scope.storeSingleChnToFile(1,fn)
#                    with open(fn) as f:
#                        for line in f:
#                            data = line.split()
#                            currentTime = float(data[0])
#                            currentVoltage = float(data[1]) * 1000
#                            runningVoltage += currentVoltage

                #for chn in range(8):
                for chn in [2]:
                    l= "%d %.4f [V] %6.2f [mA] "%(chn,cc.volreg_measure_voltage(chn), 1000.0*cc.volreg_measure_current(chn))
                    current1.append(1000.0*cc.volreg_measure_current(chn))
                    print l

#                    count += 1
            dac.append(bl)
#            meanVoltage.append(runningVoltage / count)

        fig = plt.figure()
#        plt.plot(dac,meanVoltage)
        plt.plot(dac,current1)
#        fig.suptitle('DAC Scan For SET14')
        plt.xlabel('DAC (BL)')
        plt.ylabel('Current 1 [mA]')
        plt.show()
#        plt.savefig('bldac_scan_SET14.png')

    except KeyboardInterrupt:
        print "Exiting ..."

if __name__ == '__main__':
  clicpix_dac_scan()

