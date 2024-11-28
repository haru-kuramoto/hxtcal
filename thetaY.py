import sys, os, glob
from PIL import Image, ImageOps
import numpy as np
import astropy.io.fits as fits
import matplotlib.pyplot as plt
import scipy.optimize as spo
from PIL import Image

pix_centerX=1120
pix_centerY=1024

indir = sys.argv[1]

pulseY0=-14      #change?
delta_pulseY=80  #change?

def func(x, a, b) :
    return a + b*x

def vertex(p1, p2) :
    return (p2[0]-p1[0])/(p1[1]-p2[1])

def thetaY(tiffile) :
    image = Image.open(tiffile)
    data_array = np.asarray(image).astype(np.float64)
    masked_data = data_array[pix_centerY-200: pix_centerY+200, pix_centerX-25:pix_centerX+25]
    shape = masked_data.shape
    return np.sum(masked_data)/(shape[0]*shape[1])

def main(indir):
    files = glob.glob(indir + "/*.tif")
    file_numlist = []
    for f in files:
        num_str = f.split("/")[-1].split("_")[-1].replace(".tif", "")
        file_numlist.append(int(num_str))
    file_numlist, files = zip(*sorted(zip(file_numlist, files)))
    plot_x = []
    plot_y = []
    for i,file in enumerate(files):
        x = float(i)*delta_pulseY+pulseY0-delta_pulseY*10.0
        y = thetaY(file)
        plot_x.append(x)
        plot_y.append(y)
    plot_x = np.array(plot_x)
    plot_y = np.array(plot_y)
    param1, cov1 = spo.curve_fit(func, plot_x[5:10], plot_y[5:10])
#    param2, cov2 = spo.curve_fit(func, x[10:15], y[10:15])
    param2, cov2 = spo.curve_fit(func, plot_x[11:16], plot_y[11:16])

    print("left  : %f + %f*x" %(param1[0], param2[1]))
    print("right : %f + %f*x" %(param1[0], param2[1]))

    vt = vertex(param1, param2)
    print("vertex : x = %f" %vt)
    
    plt.scatter(plot_x, plot_y)
    plt.plot(plot_x, func(plot_x, param1[0], param1[1]))
    plt.plot(plot_x, func(plot_x, param2[0], param2[1]))
    #plt.text(0.5, 0.5, "x = %6.4f" %vt, size=20)
    plt.text(vt+100., func(vt, param1[0], param1[1]), "x = %6.4f" %vt, size=16)
    plt.grid() 
    plt.xlabel("Ty [pulse]")
    plt.ylabel("Intensity per pix")
    plt.show()


if __name__ == '__main__':
    main(indir)    
    
