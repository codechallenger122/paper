from glob import glob
from time import time
import datetime
import math
dcellWidth = 5  # divided cell의 width
dcellHeight = 1  # divided cell의 height 
regionDcellXea = 30   # 30 x 5(dcellWidth)  = 150개 col grid ; Region에 있는 dcell의 총 col 개수
regionDcellYea = 10   # 10 x 1(dcellHeight) =  10개 row grid ; region에 있는 dcell의 총 row 개수
capaFactor = 1
# 0. Function Define
def calcNumOfDivCell(height, width):
    divRow = int(height/unitHeight)

    divRawCol = int(width/unitWidth)
    divRawColValue = divRawCol // dcellWidth
    divRawColRest  = divRawCol % dcellWidth
    if divRawColRest == 0:
        divCol = divRawColValue
    else:
        divCol = divRawColValue + 1
    return divCol*divRow

def calcNumOfDivCell2(height, width):
    divRow = int(height/unitHeight)

    divRawCol = int(width/unitWidth)
    divRawColValue = divRawCol // dcellWidth
    divRawColRest  = divRawCol % dcellWidth
    if divRawColRest == 0:
        divCol = divRawColValue
    else:
        divCol = divRawColValue + 1
    return str(divCol), str(divRow)

def writePrint(strarg, logFile):
    logFile.write(strarg + "\n")
    print(strarg)
def bisect(a, x, lo=0, hi=None):
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    if lo == len(a): return lo-1
    return lo
def FindNearRegion(idx, regionUcellXea, regionUcellYea, numOfRegionRow, numOfRegionCol):
    xCoord = globCellX[idx]; yCoord = globCellY[idx];width = globCellW[idx];height = globCellH[idx]    
    xTrans = (xCoord+width/2)/(unitWidth*regionUcellXea); yTrans = (yCoord+height/2)/(unitHeight*regionUcellYea)
    xNearCenter = xList[bisect(xList, xTrans)]-0.5
    yNearCenter = yList[bisect(yList, yTrans)]-0.5
    outList = []

    for dx in [-7,-6,-5,-4, -3,-2, -1, 0, 1, 2, 3, 4,5,6,7]:
        for dy in [-7,-6,-5,-4, -3, -2, -1, 0, 1, 2, 3, 4,5,6,7]:
            newX = int(xNearCenter+dx)
            newY = int(yNearCenter+dy)
            if newX < 0 or newY < 0 : continue
            elif newX >= numOfRegionCol or newY >= numOfRegionRow: continue
            delta = round(abs(newX - xTrans) + abs(newY - yTrans), 3)
            outList.append([newY, newX, delta])
    outList.sort(key = lambda x : x[2])
    return outList
def pushCellToRegion(idx, regionUcellXea, regionUcellYea, numOfRegionRow, numOfRegionCol):
    nearRegion = FindNearRegion(idx, regionUcellXea, regionUcellYea, numOfRegionRow, numOfRegionCol)
    xLL = globCellX[idx]
    yLL = globCellY[idx]
    height = globCellH[idx]
    width = globCellW[idx]
    fLogStep2.write("="*50+"\n")
    fLogStep2.write(" Cell ("+str(idx)+") with (x', y') = ("+str(xLL)+", "+str(yLL)+") with (w, h) = ("+str(width)+","+str(height)+") is picked\n")

    divRow = int(height/unitHeight)
    divRawCol = int(width/unitWidth)
    cellCapaRaw = divRow * divRawCol

    divRawColValue = divRawCol // dcellWidth
    divRawColRest  = divRawCol % dcellWidth
    if divRawColRest == 0:
        divCol = divRawColValue
    else:
        divCol = divRawColValue + 1

    cellCapa = divRow * divCol * dcellWidth
    divCellList = []
    fLogStep2.write("("+str(divRow)+ "x"+str(divRawCol)+") size Cell is divided to ("+str(divRow) + "x" + str(divCol)+")\n")
    fLogStep2.write("cell Capa is diverted from " + str(cellCapaRaw) + " to " + str(cellCapa)+"\n")
    for i in range(divCol):
        for j in range(divRow):
            divCellList.append([xLL+dcellWidth*i*unitWidth, yLL+j*unitHeight, idx, j, i, divRow, divCol])

    for region in nearRegion:
        i = region[0]
        j = region[1]
        #displacement = region[2]
        if regionCap[i][j] >= cellCapa:
            regionCap[i][j] = regionCap[i][j] - cellCapa
            regionCell[i][j].extend(divCellList)
            fLogStep2.write(" Assigned to Region ("+str(i)+", "+str(j)+")\n")
            return
    fLogStep3.write("###  Cell ("+ str(idx) + ")" + " 의 x좌표, y좌표 = ("+str(xLL)+","+ str(yLL)+") is full\n")
    fullCellList.append(idx)

# 1. Global variable Define
# at Step 0.
#pwd = "C:\/Users\/HPK\/Desktop\/study\/"
pwd = "C:\/Users\/김화평\/Desktop\/pyProject\/"
logFileStep1 = pwd + "step1.log"
logFileStep2 = pwd + "step2.log"
logFileStep3 = pwd + "step3.log"
sortedCellFile = pwd + "sortedcell.log"

cellDivRegionAssignFile = pwd + "cellAssignedToRegion.txt"

fLogStep1 = open(logFileStep1, "w")
fLogStep2 = open(logFileStep2, "w")
fLogStep3 = open(logFileStep3, "w")
foutput = open(cellDivRegionAssignFile, "w")
fSortedCell = open(sortedCellFile, "w")

nodeFilename = pwd + "node.txt" ## input
globCellName = []; globCellX = []; globCellY = []; globCellW = []; globCellH = []
legCellX = []; legCellY = []
xMax = float("-inf"); yMax = float("-inf")
sortedCellList = []
numOfCell = 0 ## original cell 개수.

# at Step 1.
unitHeight = 0.768; unitWidth = 0.064        ## input
blockHeight = 245.76; blockWidth  = 252.8    ## input

numOfRow = math.ceil(blockHeight/unitHeight)
numOfCol = math.ceil(blockWidth/unitWidth)

regionUcellYea = regionDcellYea * dcellHeight
regionUcellXea = regionDcellXea * dcellWidth

numOfRegionRow = int(numOfRow/regionUcellYea)
lastRegionUcellYea = regionUcellYea + numOfRow%regionUcellYea
numOfRegionCol = int(numOfCol/regionUcellXea)
lastRegionUcellXea = regionUcellXea + numOfCol%regionUcellXea

writePrint("="*100, fLogStep1)
writePrint("unitHeight = "+ str(unitHeight), fLogStep1)
writePrint("unitWidth  = "+ str(unitWidth),  fLogStep1)
writePrint("blockHeight = "+ str(blockHeight), fLogStep1)
writePrint("blockWidth  = "+ str(blockWidth),  fLogStep1)
writePrint("Total Unit Row 개수 = "+ str(numOfRow)+ " by blockHeight/unitHeight", fLogStep1)
writePrint("Total Unit Col 개수 = "+ str(numOfCol)+ " by blockWidth/unitWidth"  , fLogStep1)
writePrint("="*100, fLogStep1)
writePrint("Region Height = "+ str(regionUcellYea)+ " by regionDcellYea * dcellHeight", fLogStep1)
writePrint("Region Width  = "+ str(regionUcellXea) + " by regionDcellXea * dcellWidth" , fLogStep1)
writePrint("Region row 개수 = "+ str(numOfRegionRow)+ " by numOfRow/regionUcellYea", fLogStep1)
writePrint("Region col 개수 = "+ str(numOfRegionCol) + " by numOfCol/regionUcellXea" , fLogStep1)

# at Step 2.
xList = []; yList = []
for y in range(0,numOfRegionRow): yList.append(y+0.5)
for x in range(0,numOfRegionCol): xList.append(x+0.5)
fullCellList = []
""" ===================================================================================================== """

#2. Procedure
"""  Step 0. 
1. file 읽기. 
2. cell sorting 하기. 
3. cell data 정리하기. 
"""
with open(nodeFilename, "r") as f:
    while True:
        line = f.readline()
        if not line:break
        args = line.split(":")
        if len(args) != 5:
            print("format is weired.. it should have 5 elements")
            print(line)
        else:
            name = args[0]
            xLL = float(args[1])
            yLL = float(args[2])
            width = float(args[3])
            height = float(args[4].split()[0])

            sortedCellList.append([name,xLL,yLL,width,height])
            
numOfCell = len(sortedCellList)
writePrint("="*100,fLogStep1)
writePrint("현재 입력된 cell의 개수는 "+ str(numOfCell)+"개 입니다.",fLogStep1)

sortedCellList.sort(key = lambda x : x[1])

numOfDivCell = 0
idx = 0
for cell in sortedCellList:
    globCellName.append(cell[0])
    globCellX.append(cell[1])
    globCellY.append(cell[2])
    globCellW.append(cell[3])
    globCellH.append(cell[4])
    numOfDivCell = numOfDivCell + calcNumOfDivCell(cell[4], cell[3])
    ColA, RowA = calcNumOfDivCell2(cell[4],cell[3])
    fSortedCell.write("{:>8}".format(idx) + "번 Cell : " + 
                      "X좌표 = {:<10}".format(cell[1]) +
                      "Y좌표 = {:<10}".format(cell[2]) +
                      "너비  = {:<10}".format(cell[3]) +
                      "높이  = {:<10}".format(cell[4]) +        
                      "너비개수 = {:<10}".format(ColA) +
                      "높이개수 = {:<10}".format(RowA) +
                      "\n")
    idx+=1
fSortedCell.close()
print("divided cell 개수는 ", numOfDivCell)

"""  step 1. 
1. Block을 region으로 divide. region을 dictionary로 구현 할 것임. 
   : regionCell[i][j] = [cell1, cell2, ... ]
   : regionCap[i][j] = capacity # integer
"""
regionCap = {}
regionCell = {}
for i in range(0, numOfRegionRow):
    regionCap[i] = {}
    regionCell[i] = {}
    if i != numOfRegionRow-1: capY = regionUcellYea
    else: capY = lastRegionUcellYea    
    for j in range(0, numOfRegionCol):
        if j != numOfRegionCol-1: capX = regionUcellXea
        else: capX = lastRegionUcellXea
        regionCap[i][j] = capX*capY*capaFactor
        regionCell[i][j] = []
        fLogStep2.write(" region Capacity = regionCap[" + str(i) + "][" + str(j) + "] = " + str(regionCap[i][j])+ "\n")
        
"""
Step 2. cell들을 x좌표 기준으로 sorting 한다. <-- step 0
        x좌표를 non-decreasing order로 traverse하면서 cell이 가장 가까운 region으로 할당.
        해당 region의 capacity가 꽉 찬 경우, 다음 가까운 region으로 이동.
        단, cell이 region으로 이동시에는 divide되어 이동되며, divide된 cell들은 같은 region으로 이동한다.
"""

print("numOfCell is ", numOfCell)

for idx in range(numOfCell):
    if idx == int(numOfCell/10): print("10 percent done")
    elif idx == int(numOfCell/3): print("33 percent done")
    elif idx == int(numOfCell/2): print("50 percent done")
    elif idx == int(numOfCell/1.3): print("70 percent done")
    pushCellToRegion(idx, regionUcellXea, regionUcellYea, numOfRegionRow, numOfRegionCol)

print("full cell ", len(fullCellList), "개 exists")
"""
for i in regionCap.keys():
    for j in regionCap[i].keys():
        print("current Cap of i,j == ", i, ", ", j, " is ", 5*len(regionCell[i][j]),"/", regionCap[i][j])
        """
idx = 0
for i in range(0, numOfRegionRow):
    for j in range(0, numOfRegionCol):
        idx=idx+1
        foutput.write("Region,"+ str(i) + ","+str(j)+","+str(len(regionCell[i][j]))+"\n")
        for x,y,type,rowNumb,colNumb,rowFull,colFull in regionCell[i][j]:
            foutput.write(str(x)+ "," +str(y)+ "," +str(type)+ "," +
            str(rowNumb+1) + "," + str(colNumb+1) + "," + str(rowFull) + "," + str(colFull) + "\n")
            #  x좌표, y좌표, cell ID, row(현재cell), col(현재cell), rowMax, colMax
            #  row(현재cell), col(현재cell), rowMax, colMax 는 1부터 센다.
