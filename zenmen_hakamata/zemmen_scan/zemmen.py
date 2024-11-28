from modules.zemmen_sum import zsum
from modules.zemmen_psf_eef import psf_eef
from sys import argv
import os

#=============================================================================
# ・各操作の実行は True/False の実行で制御可能 -> True で実行、False でスキップ
# ・第一引数に tif ファイルが入っているディレクトリ, 第二引数に fits ファイルを
#   出力するディレクトリを指定すること
# ・このスクリプトと同じディレクトリの modules/ に zemmen_psf_eef.py, zemmen_sum.py, 
#   convert_tiff2fits.py を入れておくこと
#=============================================================================

tif2fits_conv = False    # tif -> fits 変換の実行 (True or False)
imageadd = False         # イメージ合算の実行 (True or False)
effcalc = True           # 有効面積の計算 (True or False)
psf_run = False           # PSF解析の実行 (True or False)
eef_run = True           # EEF解析の実行 (True or False)

def main():
    if len(argv) == 2:
        fits_file_dir = argv[1]
        outdir = "None"
        print("Warning : No outdir is read")
    elif len(argv) == 3:
        fits_file_dir = argv[1]
        outdir = argv[2]
        os.system(f"mkdir {outdir}")
    else:
        fits_file_dir = "None"
        outdir = "None"
        print("Warning : No TIF file is read")

    zsum(fits_file_dir,tif2fits_conv,effcalc,imageadd,outdir)
    psf_eef(psf_run,eef_run)
    print()

if __name__ == "__main__":
    main()