from modules.convert_tiff2fits import convert
import glob
import astropy.io.fits as iofits 
import astropy.wcs
import astropy.io.fits as fits
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil

def zsum(fits_file_dir,tif2fits_conv,effcalc,imageadd,outdir):

    tifdir = fits_file_dir

    if tif2fits_conv:
        files = glob.glob(tifdir+"/*.tif")
        for i in range(len(files)):
            convert(files[i])
            shutil.move(files[i].replace(".tif",".fits"), outdir+"/"+files[i].split("/")[-1].replace(".tif",".fits"))
            
    if imageadd:
        #------- 反射光データファイルのリスト化 ------------------
        tifdir = outdir
        drk_raw = glob.glob(tifdir+"/*_dark.fits")
        print(drk_raw)
        drk = []
        num = len(drk_raw)
        d_num = np.arange(1,num+1)
        for i in range(len(d_num)):
            #for j in range(len(drk_raw)):
                #if int(drk_raw[j].split("/")[-1].split("_")[-2]) == int(d_num[i]):
                drk.append(drk_raw[i])
        ref1 = []
        ref2 = []
        for i in range(len(drk)):
            ref1.append(drk[i].replace("_dark","_001"))
            ref2.append(drk[i].replace("_dark","_002"))
        print(len(drk_raw),len(drk))
        #------- ダイレクト光データファイルのリスト化 --------------

        drct_dark1 = glob.glob(tifdir+"/dark*_001.fits")
        drct_dark2 = glob.glob(tifdir+"/dark*_002.fits")

        drct1 = []
        drct2 = []
        num_drct = len(drct_dark1)
        for i in range(len(drct_dark1)):
            drct1.append(drct_dark1[i].replace("dark_","drct_"))
            drct2.append(drct_dark2[i].replace("dark_","drct_"))
        
        #------- 反射光イメージの足し合わせ -----------------------


        image = []
        for i in range(2048):
            arr = []
            for j in range(2048):
                arr.append(float(0))
            image.append(arr)

        def add(image,refl1, refl2, dark):
            data1 = iofits.open(refl1)[0].data
            data2 = iofits.open(refl2)[0].data
            Dark = iofits.open(dark)[0].data
            for i in range(len(image)):
                for j in range(len(image[i])):
                    image[i][j] = image[i][j]+(((float(data1[i][j])+float(data2[i][j]))/2)-float(Dark[i][j]))/num

        def totcts(image):
            suma = 0
            for i in range(len(image)):
                suma = suma+sum(image[i])
            return(suma)

            
        loop = len(drk)
        #loop = 30
        for i in range(loop):
            add(image, ref1[i], ref2[i], drk[i])
            fitsf = ref1[i].split("/")[-1]
            if 10 <= int(fitsf.split("_")[-2]) < 100:
                zero0 = "0"
            elif int(fitsf.split("_")[-2]) < 10:
                zero0 = "00"
            else:
                zero0 = ""
            print(f'No.{zero0}{int(fitsf.split("_")[-2])} total:{round(totcts(image),2)} ({i+1}/{loop})')
        print()

        hdu = fits.PrimaryHDU(image)
        hdulist = fits.HDUList([hdu])
        hdulist.writeto('zenmen_image.fits',overwrite=True)
        plt.imshow(image)

        #---------- ダイレクト光イメージの足し合わせ ---------------


        drct_image = []
        for i in range(2048):
            arr = []
            for j in range(2048):
                arr.append(float(0))
            drct_image.append(arr)

        def add_drct(image, refl1, refl2, dark1, dark2):
            data1 = iofits.open(refl1)[0].data
            data2 = iofits.open(refl2)[0].data
            Dark1 = iofits.open(dark1)[0].data
            Dark2 = iofits.open(dark2)[0].data
            for i in range(len(image)):
                for j in range(len(image[i])):
                    image[i][j] = image[i][j]+(((float(data1[i][j])-float(Dark1[i][j])+float(data2[i][j])-float(Dark2[i][j]))/2))/num_drct


        loop_drct = len(drct1)
        #loop = 30
        for i in range(loop_drct):
            add_drct(drct_image, drct1[i], drct2[i], drct_dark1[i], drct_dark2[i])
            print(f'direct : ({i+1}/{loop_drct})')

        hdu = fits.PrimaryHDU(drct_image)
        hdulist = fits.HDUList([hdu])
        hdulist.writeto('zenmen_direct_image.fits',overwrite=True)
        plt.imshow(drct_image)

        #----------- 有効面積の計算 ------------------------
    if effcalc:
        ref_im = iofits.open('zenmen_image.fits')[0].data
        drct_im = iofits.open('zenmen_direct_image.fits')[0].data

        refall, dirall = 0, 0
        for i in range(len(ref_im)):
            refall = refall+sum(ref_im[i])
        for i in range(len(drct_im)):
            dirall = dirall+sum(drct_im[i])

        all_sur = len(glob.glob(outdir+"/*_dark.fits"))  #全面面積 [cm^2]
        effarea = round(all_sur*refall/dirall,2)
        print()
        print(f"effective area : {effarea} cm^2")


