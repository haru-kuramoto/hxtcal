#首振り補正値を角度で返す。
#csvファイルを読み込ませる時、.pyのあとスペース開けて csv ファイルのパス。
#> python kubihuri.py Book.csv
# 実行ファイルと同じディレクトリに出力ディレクトリができるはず。
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import sys, os

file = sys.argv[1]

ref_number = 7
#データの読み込み
Num_list = np.loadtxt(file,delimiter=',',usecols=[0],encoding="utf-8_sig")
Circle_x = np.loadtxt(file,delimiter=',', usecols=[1],encoding="utf-8_sig")
Circle_y = np.loadtxt(file,delimiter=',', usecols=[2],encoding="utf-8_sig")
Cross_x = np.loadtxt(file,delimiter=',', usecols=[3],encoding="utf-8_sig")
Cross_y = np.loadtxt(file,delimiter=',', usecols=[4],encoding="utf-8_sig") 
x_pix_error = np.array([0.25 for i in range(len(Num_list))])
y_pix_error = np.array([0.25 for i in range(len(Num_list))])
r_pix_error = np.array([0.25*np.sqrt(2) for i in range(len(Num_list))])
#まずは基準の距離を測る。十字を原点に取る座標系になる。
Dif_x = [cix-crx for cix,crx in zip(Circle_x,Cross_x)]
Dif_y = [ciy-cry for ciy,cry in zip(Circle_y,Cross_y)]
R_list = [np.sqrt(dx**2+dy**2) for dx,dy in zip(Dif_x,Dif_y)]
#フィット関数
def sin(x,A,B,C,D):
    f = A*np.sin(B*x+C)+D
    return f
#フィットパラメータの初期値
init_param = [20,0.1,0,0]
#フィット
popt_x, pcov_x = curve_fit(sin,Num_list,Dif_x, p0=init_param)
popt_y, pcov_y = curve_fit(sin,Num_list,Dif_y,p0=init_param)
popt_r, pcov_r = curve_fit(sin,Num_list,R_list, p0=init_param)
ax = np.arange(0,48.1,0.1)
Fit_x = sin(ax,*popt_x)
Fit_y = sin(ax,*popt_y)
Fit_r = sin(ax,*popt_r)
#プロット
fig = plt.figure(figsize=(16,5))
ax1 = fig.add_subplot(1,2,1)
ax1.errorbar(Num_list,R_list,yerr=r_pix_error,fmt='o',c='b',capsize=2, label="r = sqrt((circlex-crossx)^2+(circley-crossy)^2)", markersize=3)
ax1.hlines(R_list[ref_number],Num_list[0], Num_list[-1], colors='b',linestyles='dashed', label='reference', lw=1)
ax1.errorbar(Num_list,Dif_x,yerr=x_pix_error,fmt='o',c='r',capsize=2, label="circlex-crossx", markersize=3)
ax1.plot(ax,Fit_x,c='r',label='x fit')
ax1.errorbar(Num_list,Dif_y,yerr=y_pix_error,fmt='o',c='g',capsize=2, label="circley-crossy", markersize=3)
ax1.plot(ax,Fit_y,c='g',label='y fit')
ax1.grid()
ax1.legend()
ax1.set_xlabel('Data number')
ax1.set_ylabel('Circle - Cross (pix)')
ax1.set_title('Circle-Cross difference')
# 拡大図
ax2 = fig.add_subplot(1,2,2)
ax2.errorbar(Num_list,R_list,yerr=r_pix_error,fmt='o',c='b',capsize=2, label="r = sqrt((circlex-crossx)^2+(circley-crossy)^2)", markersize=3)
ax2.errorbar(Num_list[ref_number], R_list[ref_number], yerr=r_pix_error[ref_number], fmt='o', c='r', capsize=2, label='reference', markersize=3)
ax2.hlines(R_list[ref_number],Num_list[0], Num_list[-1], colors='b',linestyles='dashed', label='reference', lw=1, alpha=0.5)
ax2.legend()
ax2.grid()
ax2.set_xlabel('Data number')
ax2.set_ylabel('Circle - Cross (pix)')
ax2.set_title('Deplacement in radius direction (basis: bar 4-5 in seg1 (num 8))')
#基準値(フィットしたやつ)からの伸びを計算
Fit_x = sin(Num_list,*popt_x)
Fit_y = sin(Num_list,*popt_y)
Fit_r = sin(Num_list,*popt_r)
# 基準の角度からの伸び(r)を計算
Dif_r = [r-R_list[ref_number] for r in R_list]
# print(Dif_r)
#ベクトルの角度を求める。範囲は -pi~pi
Theta_list = [np.arctan2(dy,dx) for dx,dy in zip(Dif_x,Dif_y)]
# print(Theta_list)
#rの伸縮を検出器のx,y方向に射影
X_dif_r = [dr*np.cos(theta) for dr,theta in zip(Dif_r,Theta_list)]
Y_dif_r = [dr*np.sin(theta) for dr,theta in zip(Dif_r,Theta_list)]
#rをTy,Tzに変換
#各種長さ(mm)
beam_divergence_effect = 1.0634 # 壁に貼る紙を参照
HXT_length = 487.4
pix2mm = 15.484/1000
#arcsecで出力
# 拡散光補正を入れている。検出器上で長さの変位を測定するから、それをHXT中心における変位に変換するために行っている。
Tz_list = [np.rad2deg(np.arctan(xd*pix2mm/beam_divergence_effect/HXT_length))*3600 for xd in X_dif_r]
Ty_list = [np.rad2deg(np.arctan(yd*pix2mm/beam_divergence_effect/HXT_length))*3600 for yd in Y_dif_r]
#角度をパルスに変換 (ここがかなり不安)
asec2pls_tz = 65/10
asec2pls_ty = 104/100
Tz_pls = [tz*asec2pls_tz for tz in Tz_list]
Ty_pls = [ty*asec2pls_ty for ty in Ty_list]
kubihuri_hoseiti = np.vstack((Ty_pls,Tz_pls)).T
#arcminに変換
Tz_amin = [tz/60 for tz in Tz_list]
Ty_amin = [ty/60 for ty in Ty_list]
kubihuri_amin = np.vstack((Ty_amin,Tz_amin)).T
# 出力
outdir = os.path.join("./", "kubifuri_output")
if not os.path.exists(outdir):
    os.makedirs(outdir)
plt.savefig(os.path.join(outdir, "kubifuri.png"), bbox_inches='tight', dpi=300)
#首振り補正値
txt_file = os.path.join(outdir, "kubihuri.txt")
np.set_printoptions(suppress=True)
np.savetxt(txt_file,kubihuri_hoseiti,header=('Ty, Tz (pls)'),fmt='%.3f')
# txt_fit_result = os.path.join(outdir, "fit_result.txt")
# np.savetxt(txt_fit_result,popt_r,header=('# A,B,C,D (function = A*np.sin(B*x+C)+D)'),fmt='%.3f')
# plt.show()
