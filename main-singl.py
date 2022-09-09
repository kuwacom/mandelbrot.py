import time
import numpy as np
import cv2
import matplotlib.pyplot as plt
from numba import jit

# ディスプレイ用のサイズ
displayHeight = 1000
displayWidth = 1000

# 表示用のサイズ
showHeight = 1000
shiwWidth = 1000

#計算用のサイズ
processHeight = 1000
processWidth = 1000

# size = 5*10**-3 # 描く領域の一辺の長さ
size = 1*10**-2
manX = -0.5577
manY = -0.6099
# manX = 0.5
# manY = 0
mandelbrot = np.zeros((processHeight, processWidth, 3), np.uint8)
print(mandelbrot.shape)
# @jit
def main():
    for i in range(processWidth): # x（実部）方向のループ
        x = i * size / processWidth - size / 2 # 定数Cの実部
        for j in range(processHeight): # y（虚部）方向のループ
            y = j * size / processHeight - size / 2 # 定数Cの虚部
            a = 0 # くり返し計算に使う複素数zの実部
            b = 0 # くり返し計算に使う複素数zの虚部
            for k in range(51): # 上限を50回とするくり返し計算
                _a = a * a - b * b + x + manX # z^2+Cの計算（実部）
                _b = 2 * a * b + y + manY # z^2+Cの計算（虚部）
                a = _a # zの値を更新（実部）
                b = _b # zの値を更新（虚部）
                mandelbrot[j, i] = [255,80,80]
                # mandelbrot[j, i] = [round(40+k/5),0,round(40+k/5)]
                # mandelbrot[j, i] = [round(40+k/5),0,k*5]
                if (a**2 + b**2 > 4): # もし絶対値が2を（絶対値の2乗が4を）超えていたら
                    mandelbrot[j, i] = [k*5,0,0] # (i,j)の位置のピクセルを「マンデルブロ集合でない色」で塗りつぶして
                    break # 次の点の計算へ
        showMandelbrot = cv2.resize(mandelbrot, (displayWidth, displayHeight))
        # cv2.imshow("Image", showMandelbrot)
        cv2.imshow("Image", np.flipud(showMandelbrot))
        cv2.waitKey(1)
 
main()
# cv2.imwrite('mandelbrot5.jpg', np.flipud(mandelbrot))# マンデルブロ集合画像の保存

# cv2.imshow("Image", np.flipud(mandelbrot))
xMin = 0 * size / processWidth - size / 2
xMax = processWidth * size / processWidth - size / 2
yMin = 0 * size / processHeight - size / 2
yMax = processHeight * size / processHeight - size / 2
plt.imshow(np.flipud(mandelbrot), extent=[xMin, xMax, yMin, yMax])
plt.show()
cv2.waitKey()