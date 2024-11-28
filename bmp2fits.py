import numpy as np
import astropy.io.fits as fits
import os,glob,argparse, time
from PIL import Image

"""
BLCで取得したビットマップ(.bmp)をds9で読み込める.fits形式に変換するスクリプト。
fitsに変換する際に、ndarrayとDS9ではy軸の向きが逆なので、上下反転して保存する。
.fitsファイルは ./0fits_data に格納される。0をつけているのはディレクトリの最も上に表示させるため。
usage:
python bmp2fits.py -i /path/to/bmpdir/
"""

def bmp2arr_saveasfits(bmpdir):
	# ファイルを取ってくる
	path_wc = os.path.join(bmpdir, "*.bmp")
	Filelist = glob.glob(path_wc)
	Filelist.sort()
	# 出力先は同じディレクトリ中の fits用ディレクトリ
	outdir = os.path.join(bmpdir, "0fitsimages")
	# もしなかったら新規作成
	if os.path.isdir(outdir) == False:
		os.makedirs(outdir)
	for bmp in Filelist:
		# bmp画像を開く
		img = Image.open(bmp)
		# ビット形式から数値へ変換 
		arr = np.asarray(img).astype(np.float64)
		# ds9の座標系(左下原点)に合わせて上下反転。
		arr4ds9 = np.flipud(arr)
		# fitsとして保存。
		newhdu = fits.PrimaryHDU(arr4ds9)
		outfile = bmp.replace(".bmp", ".fits")
		outpath = os.path.join(outdir, outfile)
		newhdu.writeto(outpath, overwrite=True)

if __name__=="__main__":
	# コマンドライン引数の設定
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--indir", help="Input dir", dest="indir", type=str, nargs=1)
	args = parser.parse_args()
	indir = args.indir[0]
	# メインの処理
	t1 = time.time()
	bmp2arr_saveasfits(indir)
	t2 = time.time()
	dt = t2 - t1
	print(dt)
