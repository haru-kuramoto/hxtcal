from modules.convert_tiff2fits import convert
import glob
import astropy.io.fits as iofits 
import astropy.wcs
import matplotlib.pyplot as plt
from matplotlib import pyplot
import numpy as np

def psf_eef(psf_run,eef_run):
    tifdir = "zenmen_image.fits"
    cenX,cenY = 1024,1024
    offsetX,offsetY = 0,0

    im = iofits.open(tifdir)
    hdu = im[0]
    header = hdu.header
    data = hdu.data

    #----------------- PSF --------------------------------------
    if psf_run:
        dr = 20 #pix

        all_flux = []
        for i in range(len(data)):
                for j in range(len(data[i])):
                    all_flux.append(data[i][j])
        all_flux = sum(all_flux)

        pix = []
        psf = []
        cenX_column, cenY_column = cenY+offsetY-1, cenX+offsetX-1

        print("\n--------------------------------")
        print("PSF analysis start.")

        for n in range(int(1024/dr)-1):
            
            image = []
            for i in range(2048):
                arr = []
                for j in range(2048):
                    arr.append(0)
                image.append(arr)
                
            pix.append(dr*(n+(1/2)))
            flux = 0
            pixnum = 0
            for i in range(len(data)):
                for j in range(len(data[i])):
                    if dr*n <= ((i-cenX_column)**2+(j-cenY_column)**2)**0.5 < dr*(n+1):
                        flux += data[i][j]
                        pixnum += 1
                        image[i][j] = image[i][j]+data[i][j]
            psf.append((flux/all_flux)/pixnum)
            print(f"\r"+str(n+1)+"/"+str(int(1024/dr)-1),end="")

        plt.figure(figsize=(8,6))
        plt.xlim(0,1024)
        plt.title("PSF")
        plt.yscale("log")
        plt.xlabel("pixel")
        plt.ylabel("normalized flux [/pix]")
        plt.plot(pix, psf, c="red", marker="None")
        plt.savefig("zemmen_psf.png")
        plt.close()

    #------------- EEF ----------------------------

    if eef_run:
        dr = 20

        all_flux = []
        for i in range(len(data)):
                for j in range(len(data[i])):
                    all_flux.append(data[i][j])
        all_flux = sum(all_flux)

        pix = []
        eef = []
        cenX_column, cenY_column = cenY+offsetY-1, cenX+offsetX-1

        print("\n--------------------------------")
        print("EEF analysis start.")

        for n in range(int(1024/dr)):
            
            image = []
            for i in range(2048):
                arr = []
                for j in range(2048):
                    arr.append(0)
                image.append(arr)
                
            pix.append(dr*n)
            flux = 0
            pixnum = 0
            for i in range(len(data)):
                for j in range(len(data[i])):
                    if ((i-cenX_column)**2+(j-cenY_column)**2)**0.5 <= dr*n:
                        flux += data[i][j]
                        pixnum += 1
                        image[i][j] = image[i][j]+data[i][j]
            eef.append(flux/all_flux)
            print(f"\r"+str(n+1)+"/"+str(int(1024/dr)),end="")


        flg = 0
        for i in range(len(eef)):
            if eef[i] >= 0.5 and flg == 0:
                flg = 1
                hpdmin = pix[i-1]
                eefmin = eef[i-1]
                hpdmax = pix[i]
                eefmax = eef[i]
        hpd = ((hpdmax-hpdmin)/(eefmax-eefmin))*(0.5-eefmin)+hpdmin
        print(f"\nHPD : {round(hpd*2)} pix = {round(60*180*np.arctan(hpd*2*15.33e-6/12.761))/np.pi} arcmin")

        plt.figure(figsize=(8,6))
        plt.xlim(0,1024)
        plt.ylim(0,1.05)
        plt.title("EEF")
        plt.xlabel("pixel")
        plt.ylabel("normalized flux [/pix]")
        plt.plot(pix, eef, c="red", marker="None")
        plt.plot([0,hpd],[0.5,0.5],linestyle="dashed",c="black")
        plt.plot([hpd,hpd],[0,0.5],linestyle="dashed",c="black")
        plt.savefig("zemmen_eef.png")
        plt.close()
