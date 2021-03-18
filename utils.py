# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 11:04:01 2021

@author: mWinter
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.constants import physical_constants as const
import scipy.ndimage as ndimage
import sys
import traceback
def loadHID(fname):
    ''' load a HID image with name 'fname' and return a tuple (dict, np.ndarray)
    containing (header, data). '''
    f=open(fname, 'r')#, encoding='utf-8', errors='replace') # first open in normal read mode to extract header info
    header={} # a dictionary for the parameters
    for i in range(20):
        s=f.readline()
        s = s.strip("\n")
        if s[:3]=="@@@":
            break
        else:
            try:
                key, value = s.split("=")
                header[key]=float(value)
            except:
                pass
    f.close()
    width = int(header['WIDTH'])
    height = int(header['HEIGHT'])
    f=open(fname, 'rb') # now open in binary mode
    f.seek(0, os.SEEK_END) # go to the file end
    f.seek(f.tell()-height*width*2) # go number of pixels back (one pixel has 2 bytes) 
    raw=np.fromfile(f,dtype=np.uint16) # read the binary image data as 16 bit integers
    f.close()
    #return header, np.reshape(raw*header['ZSCALEFAC']+header['ZOFFSET'], (height, width))
    return header, np.reshape(raw, (height, width))

def twoDGauss(data, x0, y0, s, A, offs):
    x, y = data
    gauss = A*np.exp(-((x-x0)**2 + (y-y0)**2)/(2*s**2))+ offs
    return np.ravel(gauss)

def findAtoms(imgarray):
    data = np.asarray(imgarray)
    blurred = ndimage.gaussian_filter(data, sigma=5, order=0) # blur the image so the maximum is clearly visible
    ymax, xmax = np.unravel_index(np.argmax(blurred), np.shape(blurred))
    blurred_zeroed = (blurred - np.median(blurred)).clip(min=0)
    blurred_norm = blurred_zeroed / np.max(blurred_zeroed)
    imh, imw =  np.shape(data)
    # the following 2 lines don't work well for small widths, because image noise in the sides is weighted too strongly
#    sigma_x = int(np.sqrt(np.sum((np.arange(imw)-xmax)**2 * blurred_norm))) # calculate the second moment of the "distribution" blurred_norm
#    sigma_y = int(np.sqrt(np.sum((np.repeat(np.reshape(np.arange(imh),(imh,1)),imw,axis=1)-ymax)**2 * blurred_norm))) # calculate the second moment of the "distribution" blurred_norm
    sigma_x = np.abs(np.argmin(np.abs(blurred_norm[ymax, :] - 0.5)) - xmax) / np.sqrt(2*np.log(2)) # use the half width half maximum
    sigma_y = np.abs(np.argmin(np.abs(blurred_norm[:, xmax] - 0.5)) - ymax) / np.sqrt(2*np.log(2))    
    sigma_gabriel = None # do not need this one here
    x, y, w, h = [xmax - 3*sigma_x, ymax - 3*sigma_y, 6*sigma_x, 6*sigma_y] # use a 3-sigma area around the maximum
    x, y = np.clip([x,y], a_min=0, a_max=np.inf) # make sure that x,y,w and h lie within the image
    w = np.clip(w, a_min=0, a_max=imw-x)
    h = np.clip(h, a_min=0, a_max=imh-y)
    return int(x), int(y), int(w), int(h)

def fit2DGauss(img):
    x, y, w, h = findAtoms(img)
    data = img[y:y+h, x:x+w]
    h, w = np.shape(data)
    ymax, xmax = np.unravel_index(np.argmax(data), np.shape(data))
    A = data[ymax, xmax]
    offs = np.median(data)
    # try 2D fits
    X = np.arange(w)
    Y = np.arange(h)
    X, Y = np.meshgrid(X, Y)
    popt, pcov = curve_fit(twoDGauss, (X,Y), np.ravel(data), p0=[xmax, ymax, 50, A, offs])
    return popt, np.sqrt(np.diag(pcov))
    return popt, np.sqrt(np.diag(pcov))

def estimateTemperature(img_array, time_of_flight, pixel_size=4.022e-6):
    m = 87 * const['atomic mass constant'][0]
    kB = const['Boltzmann constant'][0]
    try:
        popt, perr = fit2DGauss(img_array)
    except:
        traceback.print_exception(*sys.exc_info())
        return 0
    sigma = popt[2]*pixel_size
    T = sigma**2 / time_of_flight**2 * m/kB
    return T

def estimateTemperatureLongDipoletrap(img_array, time_of_flight, pixel_size_at_atoms, atomroi, initial_cloud_size):
    m = 87 * const['atomic mass constant'][0]
    kB = const['Boltzmann constant'][0]
    x, y, w, h = atomroi
    data_int = np.mean(img_array[y:y+h, x:x+w], axis=1)
    try:
    	fit_func = lambda x, A, x0, s, o: A*np.exp(-(x-x0)**2/(2*s**2)) + o
    	popt, pcov = curve_fit(fit_func, np.arange(len(data_int)), data_int, [np.max(data_int), np.argmax(data_int), 3, 500])
    	fit_array = np.linspace(0, len(data_int), 200)
    	#plt.figure("fit")
    	#plt.plot(np.arange(len(data_int)), data_int, 'b.')
    	#plt.plot(fit_array, fit_func(fit_array, *popt), 'k-')
    	#plt.show()
    except:
        traceback.print_exception(*sys.exc_info())
        return 0
    sigma = popt[2]*pixel_size_at_atoms
    print(sigma)
    T = sigma**2 / time_of_flight**2 * m/kB - initial_cloud_size**2
    return T, (data_int, fit_array, fit_func(fit_array, *popt))
    
def getAtomNumber(imgarray, atomspergray, atomroi=None, refroi=None, borderwidth=3):
    ''' Calculate the atomnumber of an image given as a 2D numpy array with 
    gray values by integrating a region atomroi = [x, y, width, height] and
    multiplying by the given atomspergray value. Optionally, a reference roi 
    can be provided for determining an offset to subtract. If not given, the
    atomroi border (using width 'borderwidth')+ is used to estimate the offset. '''
    data = np.asarray(imgarray, dtype=np.int64)
    try:
        x, y, w, h = atomroi
        atoms = data[y:y+h, x:x+w]
    except:
        try:
            x, y, w, h = findAtoms(data)
            atoms = data[y:y+h, x:x+w]
        except:
            return 0
    number = np.sum(atoms)
    h, w = np.shape(atoms)
    try:
        xr, yr, wr, hr = refroi
        offset = np.sum(data[yr:yr+hr, xr:xr+wr]) * (w*h)/float(wr*hr) # scale to size of atomroi
    except: # use roi border as reference
        bw = min(borderwidth, w)
        bh = min(borderwidth, h)
        offset = ( np.sum(atoms[:, 0:bw]) + np.sum(atoms[:, -bw:]) \
                    + np.sum(atoms[0:bh, :]) + np.sum(atoms[-bh:, :]) ) \
                    * (w*h)/(2.*(bw*h + bh*w))
#    print atomspergray/4.0**2
    return (number-offset)*atomspergray
#    return (number-offset)*2.037e-3*4.0**2