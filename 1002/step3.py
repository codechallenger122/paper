from time import time
import datetime
import math

# 1. global/legal placement 파일 읽기
device = "mgc_des_perf_1"
pwd1 = "C:\/Users\/김화평\/Desktop\/workSpace\/benchMark\/"
pwd = pwd1 + device + "\/log\/"

globPlaceFile = pwd1 + device + "\/global.txt" ## input
legaPlaceFile = pwd + "\/place_leg.txt"

globXY = {} # globXY[cellName] = [x, y]
legaXY = {} # legaXY[cellName] = [x, y]
  
#2. Procedure
with open(globPlaceFile, "r") as f:
    while True:
        line = f.readline()
        if not line:break
        args = line.split(":")
        if len(args) != 6:
            print("format is weired.. it should have 6 elements")
            print(line)
        else:
            name = args[0]
            xLL = float(args[1])
            yLL = float(args[2])
            globXY[name] = [xLL, yLL] # globXY[string] = [float, float]

with open(legaPlaceFile, "r") as f:
    while True:
        line = f.readline()
        if not line:break
        args = line.split(":")
        if len(args) != 3:
            print("format is weired.. legal placement argument should have 3 elements")
            print(line)
        else:
            name = args[0]
            xLL = float(args[1])
            yLL = float(args[2])
            legaXY[name] = [xLL, yLL] # globXY[string] = [float, float]

def calcDisplacement():
    totalDisplacement = 0
    numOfGlobCell, numOfLegaCell = len(globXY.keys()), len(legaXY.keys())
    if numOfGlobCell != numOfLegaCell: print("some cells are not legalized.\n check it.")
    for cell in legaXY.keys():
        xGlob, yGlob = globXY[cell]
        xLega, yLega = legaXY[cell]
        displacment = abs(xGlob-xLega) + abs(yGlob-yLega)
        totalDisplacement+=displacment
    return totalDisplacement/numOfLegaCell

print(calcDisplacement())

