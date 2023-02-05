import numpy as np
import matplotlib.pyplot as plt
plt.axis([0,125,0,125]) # xMin, xMax, yMin, yMax

originalFile = "C:\/Users\/김화평\/Desktop\/place_fft_1.txt"
modifiedFile = "C:\/Users\/김화평\/Desktop\/out_fft_1.txt"

drawArgumentOrg = dict()
drawArgumentMod = dict()

def writeData(fileName, saveData):
    with open(fileName, "r") as f:
        while True:
            line = f.readline()
            if not line: break
            idx, instName, xLeg, yLeg, xGlob, yGlob, width, height = line.split(":")
            if idx not in saveData.keys(): 
                x1, x2 = float(xGlob), float(xLeg)
                y1, y2 = float(yGlob), float(yLeg)
                # if x1 >150 : continue
                # if x2 >150 : continue
                # if y1 >150 : continue
                # if y2 >150 : continue
                saveData[int(idx)] = [[x1, x2], [y1, y2]]
            else:
                # idx 는 고유 넘버라 중복되면 안된다.
                print("duplicate idx error.")

writeData(originalFile, drawArgumentOrg)
writeData(modifiedFile, drawArgumentMod)

def plotData(dictName):
    for key in dictName.keys():
        argLeft, argRight = dictName[key]
        plt.plot(argLeft, argRight, color='red', linewidth=0.5) # xMin, xMax, yMin, yMax  # xGlob, xLeg, yGlob, yLeg
    plt.show()

#plotData(drawArgumentOrg)
plotData(drawArgumentMod)

