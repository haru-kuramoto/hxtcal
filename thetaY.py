#! /usr/bin/env python3

import sys
import os.path

from PIL import Image, ImageOps
import numpy as np
import astropy.io.fits as fits
import matplotlib.pyplot as plt
import scipy.optimize as spo

import convert_tiff2fits
#import subtract_dark_projx_fits


pix_centerX=980
#width=45
pix_centerY=1019
widthY=100

#No need (2021/06/12)
#pix_maxX=2048
#pix_maxY=1488
#
#pix_square=200

pulseY0=99      #change?
delta_pulseY=80  #chanfe?

def func(x, a, b) :
    return a + b*x


def vertex(p1, p2) :
    return (p2[0]-p1[0])/(p1[1]-p2[1])

def thetaY(fitsfile) :
    f = fits.open(fitsfile)
    data_array = f[0].data
    
    #plt.imshow(data_array)
    #plt.show()
    
    #masked_data = data_array[:, pix_centerX:pix_centerX+100]
    #masked_data = data_array[pix_centerY: pix_centerY+500, pix_centerX+5:pix_centerX+50]  #correction
    masked_data = data_array[pix_centerY-100: pix_centerY+100, pix_centerX-25:pix_centerX+25]  #correction
    
    #plt.imshow(masked_data)
    #plt.show()
    
    return np.sum(masked_data)
   


if __name__ == '__main__':

    x=y=np.array([])
    
    for i in range(21) :
        tiffile = "ty_00%d.tif" %(i+1)
        filefits1 = tiffile.replace('tif', 'fits')
        convert_tiff2fits.convert(tiffile)
        
        x=np.append(x, float(i)*delta_pulseY+pulseY0-delta_pulseY*10.0)
        y=np.append(y, thetaY(filefits1))

#1回目
#    param1, cov1 = spo.curve_fit(func, x[:5], y[:5])
#    param2, cov2 = spo.curve_fit(func, x[-6:-1], y[-6:-1])
    #param1, cov1 = spo.curve_fit(func, x[2:8], y[2:8])
    #param2, cov2 = spo.curve_fit(func, x[-6:-1], y[-6:-1])
    # seg2 thetaY scan
    param1, cov1 = spo.curve_fit(func, x[5:10], y[5:10])
#    param2, cov2 = spo.curve_fit(func, x[10:15], y[10:15])
    param2, cov2 = spo.curve_fit(func, x[11:16], y[11:16])

    print("left  : %f + %f*x" %(param1[0], param2[1]))
    print("right : %f + %f*x" %(param1[0], param2[1]))

    vt = vertex(param1, param2)
    print("vertex : x = %f" %vt)
    
    plt.plot(x, y)
    plt.plot(x, func(x, param1[0], param1[1]))
    plt.plot(x, func(x, param2[0], param2[1]))
    #plt.text(0.5, 0.5, "x = %6.4f" %vt, size=20)
    plt.text(vt+100., func(vt, param1[0], param1[1]), "x = %6.4f" %vt, size=16)
    plt.grid()
    plt.show()
    
    
