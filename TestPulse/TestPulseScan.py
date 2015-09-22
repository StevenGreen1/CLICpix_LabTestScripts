#!/usr/bin/python
from ccdaq import *
import time
from sets import Set
import logging.config


def clicpix_radsource_test_pulse():
    # Set number and thresholds
    SETNumber = 16
    sets =        [9,      10,      11,      12,      13,      14,     15,      16]
    thresholds =  [914.55, 1092.57, 1105.83, 1017.87, 1012.36, 938.13, 1052.02, 980]
    thresholdForSample = thresholds[sets.index(SETNumber)]

    # Test pulse variables
    # Number of frames to take
    number_of_frames = 100
#    number_of_frames = 10
    # Number of test pulses
    tp_pulses = 1  
    # Amplitude of pulse
    tp_amplitudes_list = [round((x+1)*0.002,3) for x in range(90)]
    # Shutter time of CLICpix
    tp_shutter_time = 600e-6
    # Spacing of masked pixels. (2 is spacing between unmasked pixels.  So 2 covers 1 in 4 pixels.)
    mask_spacing = 4

    # Logging info
    logging.config.fileConfig('logging.conf')
    cc=ccdaq()
    cc.check_bias()
    logging.info( "Chipboard ID : %s"%cc.chipid)
    logging.info( "Temperature  : %.2f [deg C]"% cc.temperature_get())

    # Setup of CLICpix settings
    cc.clicpix.loadConfig(os.path.join(cc.path,"equalization","last","clicpix.cpc"))

    print os.path.join(cc.path,"equalization","last","clicpix.cpc")

    cc.clicpix.write_register(clicpix.REG_GCR,  0x00) # set negative polarity 0x00 
    cc.check_bias()
    cc.testpulses.set_source(5)
    cc.timing.set_shutter_time(tp_shutter_time)
    cc.testpulses.set_period(tp_shutter_time/tp_pulses)
    cc.clicpix.write_register(clicpix.REG_IKRUM, 25) #discharge current on pixel (ikrum)
    cc.clicpix.setAcqClk(9) # acquisition clock frequency (200/(value+1)) MHz
    cc.clicpix.extthreshold(thresholdForSample) 
    ROWS = 64
    COLUMNS = 64 
 
    try:
        for tp_amplitude in tp_amplitudes_list:
            cc.voltage_set(clicpix.VTEST,tp_amplitude)
            # Set the mask for the CLICpix.  Spacing variable tells you information about what pixels are covered up in the mask.
            for seq in range(mask_spacing*mask_spacing):
                storage_directory = "/storage/pixel/data/TestPulse/SET" + str(SETNumber) + "/AllResultsRaw"
                fbase=storage_directory #os.path.join(storage_directory,time_dir())
                mkdir(fbase)
                if mask_spacing>1: 
                    # There is a mask to apply to the sample
                    cc.clicpix.cnfpixel_set_softmask(1)
                    cc.clicpix.cnfpixel_set_tp_enable(0)
                    for py in range(ROWS):
                        for px in range(COLUMNS):
                            if px%mask_spacing==seq%mask_spacing and py%mask_spacing==seq/mask_spacing:
                                #print seq,px,py
                                cc.clicpix.cnfpixel_set_softmask(0,px,py)
                                cc.clicpix.cnfpixel_set_tp_enable(1,px,py)
                else: 
                    # No mask and set the parameters globally
                    cc.clicpix.cnfpixel_set_softmask(0)
                    cc.clicpix.cnfpixel_set_tp_enable(1)

                # Configure the matrix to apply the mask settings.
                cc.clicpix.configure_matrix(log=False)
  
                frame_no=0
                intframe=CLICpixFrame()
                noiseframe=CLICpixFrame()
                noisefrms=0
                start=time.time()
                cc.timing.display()
                for mf in range(number_of_frames):
                    timenow=time.time()
                    cc.timing.trg()
                    frame=cc.clicpix.get_frame()
                    _sum=np.sum(frame.cnt)
                    time.sleep(0.001)
                    frame_no+=1
                    if _sum>0:
                        plotSuffix = 'SET' + str(SETNumber) + '_Seq' + str(seq) + '_VoltagePulse' + str(int(tp_amplitude * 1000)) + 'mV_TestPulse'
                        frameFileName = plotSuffix + "_%04d.txt"%(frame_no)
                        fn = os.path.join(fbase,frameFileName)
                        frame.save_tot(fn)
                        dt=timenow-start
                        print "[%6.2f][%03d] %5d -> %s (maxpix:%d)"%(dt,frame_no,_sum,fn,np.max(frame.cnt))# frame.nonZero()
                        with open(fn, 'r') as original: data = original.read()
                        headerString = "HV-CMOS CLICpix\n"
                        headerString += "SET: %s\n"%(SETNumber)
                        headerString += "ChipID: %s\n"%(cc.chipid)
                        headerString += "Test_Pulse_Amplitude(mV): %s\n"%(tp_amplitude)
                        headerString += "Mask_Spacing: %s\n"%(mask_spacing)
                        headerString += "Sequence: %s\n"%(seq)
#                        headerString += "Frame_Number: %s\n"%(frame_no)
                        headerString += "EqualizationFile: %s\n"%(os.path.join(cc.path,"equalization","last","clicpix.cpc"))
                        with open(fn, 'w') as modified: modified.write(headerString + data)
                        intframe.cnt+=frame.cnt
                        plotSuffix = 'SET' + str(SETNumber) + '_Seq' + str(seq) + '_VoltagePulse' + str(int(tp_amplitude * 1000)) + 'mV_TestPulse'
                        filename = os.path.join(fbase,"chipid_%s_%s.txt"%(cc.chipid, plotSuffix))
                        intframe.save(filename)
                    else:
                        print "[%03d] %5d "%(frame_no,_sum)
                        filename = os.path.join(fbase,"noise.txt")
                        noiseframe.cnt+=frame.cnt
                        noiseframe.save(filename)
                        noisefrms+=1
                        f=open(filename,"a")
                        f.write("#%d\n"%noisefrms)
                        f.close()
                with open(filename, 'r') as original: data = original.read()
                headerString = "HV-CMOS CLICpix\n"
                headerString += "SET: %s\n"%(SETNumber)
                headerString += "ChipID: %s\n"%(cc.chipid)
                headerString += "Test_Pulse_Amplitude(mV): %s\n"%(tp_amplitude)
                headerString += "Mask_Spacing: %s\n"%(mask_spacing)
                headerString += "Sequence: %s\n"%(seq)
                headerString += "EqualizationFile: %s\n"%(os.path.join(cc.path,"equalization","last","clicpix.cpc"))
                with open(filename, 'w') as modified: modified.write(headerString + data)
        logging.info("Done")
    except KeyboardInterrupt:
        print "Exiting ..."

if __name__ == '__main__':
  clicpix_radsource_test_pulse()

