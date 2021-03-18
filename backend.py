# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 15:50:57 2021

@author: mWinter
"""
import os
import time
from utils import loadHID, getAtomNumber, estimateTemperatureLongDipoletrap
from scipy import ndimage
import numpy as np
import traceback
import sys

DATA_DIR = '.'
PIXELSIZEATATOMS = 16e-6/4.7
INITIAL_CLOUD_SIZE = 10e-6

class ProcessingFilesBackEnd(object):
    """
    Backend Class
    Independent of GUI
    """
    
    def __init__(self):        
        self.plot_data = {   'AN':   {'data':    [],
                                     'ylabel':  'AN',
                                     'type':    '1D'},
                            'T':    {'data':    [],
                                     'ylabel': 'T',
                                     'type':    '1D'},
                            'OD':   {'data':    [],
                                     'type':    '2D'}
                        }

    def do_processing(self, directories, filelists, atomroi, refroi, AN_func = getAtomNumber, T_func = estimateTemperatureLongDipoletrap, rotation_angle = 0):
        """
        method loops through directories, and looks for new files which have not been added to filelists
        
        - directories: list of strings
        - filelists: list of dicts, where each element (a dict) corresponds to the directory with the same index in directories
        - atomroi: tuple of ints (x, y, w, h)
        - refroi: tuple of ints (x, y, w, h)
        - AN_func(imgarray, atomspergray, atomroi, refroi): function for estimating the atom number; returns float
        - T_func(img_array, time_of_flight, pixel_size_at_atoms, atomroi, initial_cloud_size): function for estimating temperature; returns tuple T (float), data (fitdata) 
        
        returns:
            Bool: new_file_detected
        """#TODO rewrite T_func description
        
        for i, directory in enumerate(directories):
            new_fileList = dict([(j, os.path.getmtime(os.path.join(directory, j))) \
                            for j in os.listdir(directory) if j.endswith('.hid')])
            time.sleep(0.1) # make sure all files are written
            new_file_detected = False
            for f in new_fileList.keys():
                if (f in filelists[i].keys()):
                    if (new_fileList[f] == filelists[i][f]):
                        continue
                try:
                    if not (f.endswith('sig.hid') or f.endswith('ref.hid') or f.endswith('noise.hid')):
                        parameters, raw = loadHID(os.path.join(directory,f))
                        raw = ndimage.rotate(raw, rotation_angle)
                        OD_array = (raw.astype(np.float32) - 500) / 1688.27
                        AN = AN_func(raw, 2.04e-3*(PIXELSIZEATATOMS*1e6)**2, atomroi,refroi=refroi)
                        time_of_flight = float(parameters['ABSORPTIONPICEXPOSUREDELAY'])
                        if time_of_flight >= 0.5 and AN > 2e3: # it only makes sense to estimate the temperature after at least 0.5 ms time of flight
                            T, data = T_func(raw, time_of_flight*1e-3, PIXELSIZEATATOMS, atomroi, INITIAL_CLOUD_SIZE)
                        else:
                            T = np.nan
                        self.plot_data['AN']['data'].append(AN)
                        self.plot_data['T']['data'].append(T)
                        self.plot_data['OD']['data'] = [OD_array]
                        print("processed file ", f)
                        print("Atomnumber: %.2e" % AN)
                        print("Temperature: %.0f nK" % (T*1e9))
                        new_file_detected = True
                except:
                    traceback.print_exception(*sys.exc_info())
                    print("processing file ", f, " failed")
            filelists[i] = new_fileList
            if new_file_detected:
                return True
        
        return False
