import time
import datetime
import numpy as np
import cv2
import matplotlib.pyplot as plt
from multiprocessing import Value, Array, Process, RawArray, Queue, Manager

cpuThread = 10

# ディスプレイ用のサイズ
displayHeight = 1000
displayWidth = 1000

# # 表示用のサイズ
# showHeight = 1000
# shiwWidth = 1000

#計算用のサイズ
processHeight = 500
processWidth = 500

# size = 5*10**-3 # 描く領域の一辺の長さ

manX = -1.8888799999999999937
manY = 0.0000000000003405
# manX = 0
# manY = 0

# print(mandelbrot.shape)


def main(threadNum, processStartHeight, processIntervalHeight, processEndHeight, size, mandelbrotRAM):
    # mandelbrot = mandelbrotRAM.get()
    mandelbrot = np.zeros((processIntervalHeight, processWidth, 3), np.uint8)
    for i in range(processWidth): # x（実部）方向のループ
        x = i * size / processWidth - size / 2 # 定数Cの実部]
        for j in range(processStartHeight,processEndHeight,1): # y（虚部）方向のループ
            y = j * size / processHeight - size / 2 # 定数Cの虚部
            a = 0 # くり返し計算に使う複素数zの実部
            b = 0 # くり返し計算に使う複素数zの虚部
            for k in range(80): # 上限を50回とするくり返し計算
                _a = a * a - b * b + x + manX # z^2+Cの計算（実部）
                _b = 2 * a * b + y + manY # z^2+Cの計算（虚部）
                a = _a # zの値を更新（実部）
                b = _b # zの値を更新（虚部）
                mandelbrot[processStartHeight-j, i] = [255,80,80]
                # mandelbrot[j, i] = [round(40+k/5),0,round(40+k/5)]
                # mandelbrot[j, i] = [round(40+k/5),0,k*5]
                if (a**2 + b**2 > 4): # もし絶対値が2を（絶対値の2乗が4を）超えていたら
                    mandelbrot[processStartHeight-j, i] = [k*5,0,0] # (i,j)の位置のピクセルを「マンデルブロ集合でない色」で塗りつぶして
                    break # 次の点の計算へ
        mandelbrotRAM[threadNum] = np.flipud(mandelbrot)
        if (threadNum == cpuThread-1) & (i % 10 == 0):
            showMandelbrot = cv2.resize(np.concatenate(mandelbrotRAM.values()), (displayWidth, displayHeight))
            cv2.imshow("Loading Now...", np.flipud(showMandelbrot))
            cv2.waitKey(1)

    # mandelbrotRAM[threadNum] = mandelbrot
 
# main()
# cv2.imwrite('mandelbrot5.jpg', np.flipud(mandelbrot))# マンデルブロ集合画像の保存

# cv2.imshow("Image", np.flipud(mandelbrot))

if __name__ == '__main__':
    size = 0.0
    for sizeNum in np.arange(0,-15,-0.1):
        print("ZOOM: 4*10**"+str(sizeNum))
        size = 4*10**sizeNum
        mandelbrotRAM = Manager().dict()
        # mandelbrotRAM.put(np.zeros((processHeight, processWidth, 3), np.uint8))
        # mandelbrotRAM = np.zeros((processHeight, processWidth, 3), np.uint8)
        processIntervalHeight = processHeight/cpuThread
        for threadNum in range(cpuThread):
            # サブプロセスを作成します
            print(processIntervalHeight*threadNum)
            print(processIntervalHeight*(threadNum+1)-1)
            p = Process(target=main, args=(threadNum, int(processIntervalHeight*threadNum),int(processIntervalHeight),int(processIntervalHeight*(threadNum+1)+1), size, mandelbrotRAM))
            # 開始します
            p.start()
            print("Process started.")
            time.sleep(0.03)
        # サブプロセス終了まで待ちます
        p.join()
        print("Process joined.")
        cv2.imwrite('output/mandelbrot'+datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')+'.jpg', np.flipud(np.concatenate(mandelbrotRAM.values())))

    time.sleep(1)
    cv2.imshow("DONE", np.flipud(cv2.resize(np.concatenate(mandelbrotRAM.values()), (displayWidth, displayHeight))))
    cv2.waitKey(1)
    mandelbrot = np.concatenate(mandelbrotRAM.values())
    showMandelbrot = cv2.resize(mandelbrot, (displayWidth, displayHeight))

    a = 0 # くり返し計算に使う複素数zの実部
    b = 0 # くり返し計算に使う複素数zの虚部
    xMin = 0 * size / processWidth - size / 2
    xMax = processWidth * size / processWidth - size / 2
    yMin = 0 * size / processHeight - size / 2
    yMax = processHeight * size / processHeight - size / 2
    _a = a * a - b * b + xMin + manX # z^2+Cの計算（実部）
    __a = a * a - b * b + xMax + manX
    _b = 2 * a * b + yMin + manY # z^2+Cの計算（虚部）
    __b = 2 * a * b + yMax + manY
    cv2.imwrite('output/mandelbrot'+datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')+'.jpg', np.flipud(mandelbrot))# マンデルブロ集合画像の保存
    plt.imshow(np.flipud(mandelbrot), extent=[_a, __a, _b, __b])
    plt.show()