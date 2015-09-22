#!/usr/bin/python
from ccdaq import *
import time
from sets import Set
from libdevice import dso9254a

def clicpix_tot_scan():
    SETNumber = 14

    sets =        [9,      10,      11,      12,      13,      14,     15,      16]
    thresholds =  [914.55, 1092.57, 1105.83, 1017.87, 1012.36, 938.13, 1052.02, 980]
    thresholdForSample = thresholds[sets.index(SETNumber)]

    numberOfFramesToTake = 12000 # Rough calc.  90 events in a minute.  1.5 hours per pixel (= 1.5 * 15 = 22.5hrs). 8000 ~= 90 * 1.5 * 60.

    logging_start()
    cc=ccdaq()
    cc.check_bias()
    logging.info( "Chipboard ID : %s"%cc.chipid)
    logging.info( "Temperature  : %.2f [deg C]"% cc.temperature_get())
    set_storage_directory = "/storage/pixel/data/scope/calibration/SET" + str(SETNumber) 
    mkdir(set_storage_directory)

    scope=dso9254a.dso('192.168.222.2')  
    scope.conf(1)
    cc.clicpix.loadConfig(os.path.join(cc.path,"equalization","last","clicpix.cpc"))
    cc.check_bias()
    cc.clicpix.extthreshold(thresholdForSample)
    cc.clicpix.configure_matrix(verify=True)

    cc.timing._timing_ctrl.getNode("shutter_src").write(cc.timing.SHUTTER_SRC_ADV)
    cc.timing._timing_ctrl.getNode("power_src").write(cc.timing.POWER_SRC_ADV)
    cc.timing._timing_power_rise_conf.getNode("invert").write(0)
    cc.timing._timing_power_rise_conf.getNode("input_sel").write(cc.timing.ADV_INPUT_USR_PWR)
    cc.timing._timing_power_rise_delay.write(1)

    cc.timing._timing_shutter_rise_conf.getNode("invert").write(0)
    cc.timing._timing_shutter_rise_conf.getNode("input_sel").write(cc.timing.ADV_INPUT_POWER)
    cc.timing._timing_shutter_rise_delay.write(50000)

    cc.timing._timing_shutter_fall_conf.getNode("invert").write(1)
    cc.timing._timing_shutter_fall_conf.getNode("input_sel").write(cc.timing.ADV_INPUT_USR_PWR)
    cc.timing._timing_shutter_fall_delay.write(10)

    cc.timing._timing_power_fall_conf.getNode("invert").write(1)
    cc.timing._timing_power_fall_conf.getNode("input_sel").write(cc.timing.ADV_INPUT_SHUTTER)
    cc.timing._timing_power_fall_delay.write(1000)
    cc.timing.readout_ready()

    for pixel in [3,7,11,15,19,23,27,31,35,39,43,47,51,55,59]:
        cc.ccpd.sendConfig(mux_chn=pixel)
        pixel_storage_directory = "/storage/pixel/data/scope/calibration/SET" + str(SETNumber) + "/Pixel" + str(pixel)
        fbase=os.path.join(pixel_storage_directory,time_dir())
        mkdir(fbase)
        logging.info( "Data output  : %s"%fbase)

        try:
            start=time.time()
            frame_no=0
            acq=0
            ikrum=25
            clkdiv=9
            cc.clicpix.write_register(clicpix.REG_IKRUM, ikrum)  
            frame_no=0
            fn=os.path.join(fbase,"clkdiv%d_ikrum%d.dat"%(clkdiv,ikrum))
            logging.info( "Output file : %s"%fn)
            f=open(fn,"w")
            cc.clicpix.setAcqClk(clkdiv)
            # set negative polarity            
            cc.clicpix.write_register(clicpix.REG_GCR, 0x00)	
            for hits in range(numberOfFramesToTake):
                timenow=time.time()
                cc.timing._timing_ctrl.getNode("sequence_finished").write(0)
                cc.timing._timing_ctrl.getNode("sequence_finished").write(1)
                cc.timing._timing_ctrl.getNode("sequence_finished").write(0)
                cc.timing._hw.dispatch() 

                cc.timing._timing_ctrl.getNode("user_power_bit").write(0)
                cc.timing._timing_ctrl.getNode("user_power_bit").write(1)
                cc.timing._hw.dispatch()
                scope.single_seq()

                scope.wait_for_triger()
                cc.timing._timing_ctrl.getNode("user_power_bit").write(0)
                cc.timing._hw.dispatch()

                fn=os.path.join(fbase,"ev%03d.dat"%(acq))
                r=scope.get_single(1)
                bl=np.mean(r["data"][0:500])
                scope_amp=bl-min(r["data"])
         
                fn=os.path.join(fbase,"frame%05d.dat"%(frame_no))
                fw=open(fn,"w")
                for x,y in enumerate(r["data"]):
                    t=r["XIN"]*x
                    fw.write("%.4e %.4e\n"%(t,y))
                fw.close()

                frame=cc.clicpix.get_frame()
                _sum=np.sum(frame.tot)
                dt=timenow-start
                px,py=pixel,0
                print "%.3f %d %d Target_Pixel %d %d +1x_Pixel %d %d +1x+1y_Pixel %d %d +1y_Pixel %d %d -1x+1y_Pixel %d %d -1x_Pixel %s"%(scope_amp,frame.tot[px,py],frame.cnt[px,py],frame.tot[px+1,py],frame.cnt[px+1,py],frame.tot[px+1,py+1],frame.cnt[px+1,py+1],frame.tot[px,py+1],frame.cnt[px,py+1],frame.tot[px-1,py+1],frame.cnt[px-1,py+1],frame.tot[px-1,py],frame.cnt[px-1,py],fn)
                f.write("%.3f %d %d Target_Pixel %d %d +1x_Pixel %d %d +1x+1y_Pixel %d %d +1y_Pixel %d %d -1x+1y_Pixel %d %d -1x_Pixel Event_Number %d\n"%(scope_amp,frame.tot[px,py],frame.cnt[px,py],frame.tot[px+1,py],frame.cnt[px+1,py],frame.tot[px+1,py+1],frame.cnt[px+1,py+1],frame.tot[px,py+1],frame.cnt[px,py+1],frame.tot[px-1,py+1],frame.cnt[px-1,py+1],frame.tot[px-1,py],frame.cnt[px-1,py],frame_no ))
                f.flush()
                frame_no+=1
            f.close()
            logging.info("Done")
        except KeyboardInterrupt:
            print "Exiting ..."

if __name__ == '__main__':
    clicpix_tot_scan()

