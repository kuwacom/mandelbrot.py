from asyncio import events
import time
import datetime
from tkinter import Canvas
from turtle import onclick
import numpy as np
import cv2
import matplotlib.pyplot as plt
from multiprocessing import Value, Array, Process, RawArray, Queue, Manager
from numba import jit

cpuThread = 20

# ディスプレイ用のサイズ
displayHeight = 1000
displayWidth = 1000

# # 表示用のサイズ
# showHeight = 1000
# shiwWidth = 1000

#計算用のサイズ
processHeight = 1000
processWidth = 1000

# zoom = 5*10**-3 # 描く領域の一辺の長さ

# manX = 0
# manY = 0

# print(mandelbrot.shape)

def mandelbrotProcess(threadNum, processStartHeight, processIntervalHeight, processEndHeight, zoom, manX, manY, mandelbrotRAM):
    # mandelbrot = mandelbrotRAM.get()
    # time.sleep(threadNum*0.1)
    mandelbrot = np.zeros((processIntervalHeight, processWidth, 3), np.uint8)
    for i in range(processWidth): # x（実部）方向のループ
        x = i * zoom / processWidth - zoom / 2 # 定数Cの実部]
        for j in range(processStartHeight,processEndHeight,1): # y（虚部）方向のループ
            y = j * zoom / processHeight - zoom / 2 # 定数Cの虚部
            a = 0 # くり返し計算に使う複素数zの実部
            b = 0 # くり返し計算に使う複素数zの虚部
            for k in range(100): # 上限を50回とするくり返し計算
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

    # mandelbrotRAM[threadNum] = mandelbrot

def processProgress(mandelbrotRAM):
    while(1):
        showMandelbrot = cv2.resize(np.concatenate(mandelbrotRAM.values()), (displayWidth, displayHeight))
        cv2.imshow("Loading Now...", np.flipud(showMandelbrot))
        cv2.waitKey(1)
        time.sleep(0.05)
 
# main()
# cv2.imwrite('mandelbrot5.jpg', np.flipud(mandelbrot))# マンデルブロ集合画像の保存

# cv2.imshow("Image", np.flipud(mandelbrot))

if __name__ == '__main__':
    
    # mandelbrotRAM.put(np.zeros((processHeight, processWidth, 3), np.uint8))
    # mandelbrotRAM = np.zeros((processHeight, processWidth, 3), np.uint8)
    def main(zoom, manX, manY):
        processIntervalHeight = processHeight/cpuThread
        mandelbrotRAM = Manager().dict()
        pros = {}
        for threadNum in range(cpuThread):
            # サブプロセスを作成します
            print(processIntervalHeight*threadNum)
            print(processIntervalHeight*(threadNum+1)-1)
            pros[threadNum] = Process(target=mandelbrotProcess, args=(threadNum, int(processIntervalHeight*threadNum),int(processIntervalHeight),int(processIntervalHeight*(threadNum+1)+1), zoom, manX, manY, mandelbrotRAM))
            # 開始します
            pros[threadNum].start()
            print("Process started.")
            time.sleep(0.1)
        pP = Process(target=processProgress, args=(mandelbrotRAM,))
        pP.start()
        # サブプロセス終了まで待ちます
        for threadNum in pros:
            pros[threadNum].join()
            print("DONE process: " + str(threadNum))
        pP.terminate()
        print("DONE.")
        return mandelbrotRAM

    zoom = 4*10**0
    manX = 0
    manY = 0

    mandelbrotRAM = main(zoom, manX, manY)
    time.sleep(1)
    # cv2.imshow("DONE", np.flipud(cv2.resize(np.concatenate(mandelbrotRAM.values()), (displayWidth, displayHeight))))
    mandelbrot = np.concatenate(mandelbrotRAM.values())
    showMandelbrot = cv2.resize(mandelbrot, (displayWidth, displayHeight))

    def onclick(event):
        # print(event)
        if str(event.button) == "MouseButton.RIGHT":
            global manX, manY
            print("X: "+str(event.xdata))
            print("Y: "+str(event.ydata))
            manX = event.xdata
            manY = event.ydata
            mandelbrotRAM = main(zoom, manX, manY)
            # cv2.imshow("DONE", np.flipud(cv2.resize(np.concatenate(mandelbrotRAM.values()), (displayWidth, displayHeight))))
            # cv2.waitKey(1)
            a = 0
            b = 0
            xMin = 0 * zoom / processWidth - zoom / 2
            xMax = processWidth * zoom / processWidth - zoom / 2
            yMin = 0 * zoom / processHeight - zoom / 2
            yMax = processHeight * zoom / processHeight - zoom / 2
            _a = a * a - b * b + xMin + manX # z^2+Cの計算（実部）
            __a = a * a - b * b + xMax + manX
            _b = 2 * a * b + yMin + manY # z^2+Cの計算（虚部）
            __b = 2 * a * b + yMax + manY
            mandelbrot = np.concatenate(mandelbrotRAM.values())
            showMandelbrot = cv2.resize(mandelbrot, (displayWidth, displayHeight))
            cv2.imwrite('output/mandelbrot'+datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')+'.jpg', np.flipud(mandelbrot))
            plt.imshow(np.flipud(mandelbrot), extent=[_a, __a, _b, __b])
            plt.show()

    def onkey(event):
        global zoom
        if event.key == "+":
            zoom = zoom * 0.1
            mandelbrotRAM = main(zoom, manX, manY)
            # cv2.imshow("DONE", np.flipud(cv2.resize(np.concatenate(mandelbrotRAM.values()), (displayWidth, displayHeight))))
            # cv2.waitKey(1)
            a = 0
            b = 0
            xMin = 0 * zoom / processWidth - zoom / 2
            xMax = processWidth * zoom / processWidth - zoom / 2
            yMin = 0 * zoom / processHeight - zoom / 2
            yMax = processHeight * zoom / processHeight - zoom / 2
            _a = a * a - b * b + xMin + manX # z^2+Cの計算（実部）
            __a = a * a - b * b + xMax + manX
            _b = 2 * a * b + yMin + manY # z^2+Cの計算（虚部）
            __b = 2 * a * b + yMax + manY
            mandelbrot = np.concatenate(mandelbrotRAM.values())
            showMandelbrot = cv2.resize(mandelbrot, (displayWidth, displayHeight))
            cv2.imwrite('output/mandelbrot'+datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')+'.jpg', np.flipud(mandelbrot))
            plt.imshow(np.flipud(mandelbrot), extent=[_a, __a, _b, __b])
            plt.show()
        elif event.key == "-":
            zoom = zoom * 1.9
            mandelbrotRAM = main(zoom, manX, manY)
            # cv2.imshow("DONE", np.flipud(cv2.resize(np.concatenate(mandelbrotRAM.values()), (displayWidth, displayHeight))))
            # cv2.waitKey(1)
            a = 0
            b = 0
            xMin = 0 * zoom / processWidth - zoom / 2
            xMax = processWidth * zoom / processWidth - zoom / 2
            yMin = 0 * zoom / processHeight - zoom / 2
            yMax = processHeight * zoom / processHeight - zoom / 2
            _a = a * a - b * b + xMin + manX # z^2+Cの計算（実部）
            __a = a * a - b * b + xMax + manX
            _b = 2 * a * b + yMin + manY # z^2+Cの計算（虚部）
            __b = 2 * a * b + yMax + manY
            mandelbrot = np.concatenate(mandelbrotRAM.values())
            showMandelbrot = cv2.resize(mandelbrot, (displayWidth, displayHeight))
            cv2.imwrite('output/mandelbrot'+datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')+'.jpg', np.flipud(mandelbrot))
            plt.imshow(np.flipud(mandelbrot), extent=[_a, __a, _b, __b])
            plt.show()

    a = 0 # くり返し計算に使う複素数zの実部
    b = 0 # くり返し計算に使う複素数zの虚部
    xMin = 0 * zoom / processWidth - zoom / 2
    xMax = processWidth * zoom / processWidth - zoom / 2
    yMin = 0 * zoom / processHeight - zoom / 2
    yMax = processHeight * zoom / processHeight - zoom / 2
    _a = a * a - b * b + xMin + manX # z^2+Cの計算（実部）
    __a = a * a - b * b + xMax + manX
    _b = 2 * a * b + yMin + manY # z^2+Cの計算（虚部）
    __b = 2 * a * b + yMax + manY
    cv2.imwrite('output/mandelbrot'+datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')+'.jpg', np.flipud(mandelbrot))# マンデルブロ集合画像の保存
    fig = plt.figure()
    fig.canvas.mpl_connect('button_press_event', onclick)
    fig.canvas.mpl_connect('key_press_event', onkey)
    plt.imshow(np.flipud(mandelbrot), extent=[_a, __a, _b, __b])
    plt.show()