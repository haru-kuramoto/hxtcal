#! /usr/bin/env python3

import sys
import os.path

from PIL import Image, ImageOps
import numpy as np
import astropy.io.fits as fits

def convert(tiff):
    root, ext = os.path.splitext(tiff)
    #print(root, ext)
    print(tiff)
    filefits = (root + '.fits')
    print(filefits)
    
    img_tiff = Image.open(tiff)
    width, height = img_tiff.size
    print(width,height)

    img_tiff_flip = ImageOps.flip(img_tiff)
    img = np.asarray(img_tiff_flip)
    
    hdu = fits.PrimaryHDU(img)
    hdulist = fits.HDUList([hdu])
    hdulist.writeto(filefits,overwrite=True)
    
    print('Done: convert')

if __name__ == '__main__':
    args = sys.argv
    if len(args) != 2:
        print('Usage: python3 %s ***.tif' %(args[0]))
        exit()
    else:
        pass    
    convert(args[1])

