from dis import dis
import numpy as np
from scipy.optimize import linear_sum_assignment
from time import time
import datetime
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mip import Model, xsum, minimize, BINARY
"""
## 변수 정리 ##
기본적으로 cell-postion matching 이 알고리즘의 핵심.
rowPos,  colPos  = positon 의 row 와 column
rowNumb, colNumb = cell    의 row 와 column
globDivCellXY[cellID][rowNumb][colNumb]        = [x, y] // global placement  당시의 cell,rowNumb,colNumb 의 x,y position
hungDivCellXY[cell][rowNumb][colNumb]          = [x, y] // hungarian alogrithm 이후 cell,rowNumb,colNumb 의 x,y position
getCellRowColFromPos[row][col][rowPos][colPos] = cell, rowNumb, colNumb
priceMtx[row][col][cellId][rowNumb][colNumb] = price
overlapMtx[row][col][pRow][pCol] = [ [cellId, rowNumb, colNumb],
                                     [cellId, rowNumb, colNumb],
                                     [cellId, rowNumb, colNumb],                                   
                                     [cellId, rowNumb, colNumb]
                                   ]
"""
dcellWidth = 5   # divided cell의 width
dcellHeight = 1  # divided ce ll의 height 
regionDcellXea = 30   # 30 x 5(dcellWidth)  = 150개 col grid ; Region에 있는 dcell의 총 col 개수
regionDcellYea = 10   # 10 x 1(dcellHeight) =  10개 row grid ; region에 있는 dcell의 총 row 개수

#pwd = "C:\/Users\/HPK\/Desktop\/study\/"
pwd = "C:\/Users\/김화평\/Desktop\/pyProject\/"
logFile = pwd + "hung.log"
logFileA = pwd + "changeleg.log" # swap & price 계산.
logFileB = pwd + "last.log" # ILP 결과 저장.

fLog = open(logFile, "w")
fLogA = open(logFileA, "w")
fLogB = open(logFileB, "w")

# 1. Global variable Define
# at Step 0.
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

regionXConst = unitWidth * regionUcellXea   # unitWidth  x 150
regionYConst = unitHeight * regionUcellYea # unitHeight x  10

# at Step 2.
xList = []; yList = []
for y in range(0,numOfRegionRow): yList.append(y+0.5)
for x in range(0,numOfRegionCol): xList.append(x+0.5)
fullCellList = []

# at hungary
inRegionRow = int(regionUcellYea/dcellHeight)
inRegionCol = int(regionUcellXea/dcellWidth)
numOfPos = inRegionRow * inRegionCol

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

sortedCellList.sort(key = lambda x : x[1])

for cell in sortedCellList:
    globCellName.append(cell[0])
    globCellX.append(cell[1])
    globCellY.append(cell[2])
    globCellW.append(cell[3])
    globCellH.append(cell[4])

""" ===================================================================================================== """
print("1. numOfRegionRow = ", numOfRegionRow)
print("   numOfRegionCol = ", numOfRegionCol)
print("2. regionUcellYea = ", regionUcellYea)
print("   regionUcellXea  = ", regionUcellXea)
regionCellFile = pwd + "cellAssignedToRegion.txt"

# visualize func
def addPatchToFig(fig, data):
    cellId = str(data[0]) + "\n(" + str(data[3]) + ", " + str(data[4]) + ")\n/(" + str(data[5]) + ", " + str(data[6]) + ")"
    row, col = data[1], data[2]
    left, width = .03*(col), .03
    bottom, height = .1*(row), .1
  
    right = left + width
    top = bottom + height

    #print(cellId, left, right, top, bottom)

    a,b,c = str(hex((data[0]*5)%256))[2:], str(hex((3*data[0]+30)%256))[2:], str(hex((data[0]+60)%256))[2:]
    if len(a) == 1: a = a + "0"
    if len(b) == 1: b = b + "0"
    if len(c) == 1: c = c + "0"
    colorStr = "#"+a+b+c


    p = patches.Rectangle((left, bottom), width, height, fill=True, color=colorStr)
    fig.add_artist(p)
    fig.text(0.5*(left+right), 0.5*(bottom+top), cellId,
         horizontalalignment='center', verticalalignment='center',
         fontsize=10, color='black')
def showDistribute(cellList):
    fig = plt.figure()
    for cell in cellList:
        addPatchToFig(fig, cell)
    plt.show()

# 1. regionCellDict, regionNumbDict 만들기.
regionCellDict = {}
regionNumbDict = {}
# globDivCellXY [cellID][rowNumb][colNumb] = [x,y]

globDivCellXY = {}
with open(regionCellFile, "r") as f:
    """ regionCellFile의 구성.
        1. Region, row, col, cell 개수  -- 한 줄
        2. x좌표(glob), y좌표(glob), cell ID, row(현재cell), col(현재cell), rowMax, colMax -- 여러 줄
           row(현재cell), col(현재cell), rowMax, colMax 는 1부터 센다.  
        반복.         
    """
    while True:
        line = f.readline()
        if not line: break
        args = line.split(",")
        if len(args) == 4: # Region, row, col, cell개수.
            i,j,num = int(args[1]), int(args[2]), int(args[3].split()[0])
            if i not in regionCellDict.keys():
                regionCellDict[i] = {}
                regionNumbDict[i] = {}
            if j not in regionCellDict[i].keys():
                regionCellDict[i][j] = []
                regionNumbDict[i][j] = num
                    
        elif len(args) == 7: # x좌표, y좌표, sorting 된 number = ID, rowNumb, colNumb
            x, y, type, rowNumb, colNumb, rowMax, colMax = float(args[0]), float(args[1]), int(args[2]), int(args[3]), int(args[4]), int(args[5]), int(args[6].split()[0])
            if type not in globDivCellXY.keys(): globDivCellXY[type] = {}
            if rowNumb not in globDivCellXY[type].keys(): globDivCellXY[type][rowNumb] = {}
            if colNumb not in globDivCellXY[type][rowNumb].keys(): globDivCellXY[type][rowNumb][colNumb] = [x,y]

            regionCellDict[i][j].append([x, y, type, rowNumb, colNumb, rowMax, colMax])
            
for row in range(numOfRegionRow):
    for col in range(numOfRegionCol):
        delta = numOfPos - regionNumbDict[row][col] # numOfPos : 하나의 bin의 position 개수 --> 여기선 10 x 30 = 300 개.
                                                    # regionNumbDict[row,col] 은 해당 region에 할당된 cell 개수.
                                                    # 완벽하게 300 개 할당시 -> dummy cell 추가 필요 없다.
        if delta != 0:
            for i in range(delta):
                regionCellDict[row][col].append([-1,-1,-1,-1,-1,-1,-1]) # dummy cell 추가.

# 2. regionPosDict 만들기
regionPosDict = {}
for row in range(numOfRegionRow):
    if row not in regionPosDict.keys():regionPosDict[row] = {}
    for col in range(numOfRegionCol):
        if col not in regionPosDict[row].keys(): regionPosDict[row][col] = []
        orgX = col * regionUcellXea * unitWidth
        orgY = row * regionUcellYea * unitHeight
        for dRow in range(inRegionRow):
            for dCol in range(inRegionCol):
                newX = round(orgX + dCol*dcellWidth*unitWidth, 4)
                newY = round(orgY + dRow*dcellHeight*unitHeight,   4)
                regionPosDict[row][col].append([newX, newY, dRow, dCol])
                # row, col 별로, region에서의 300개 postion의 xLL,yLL 과 row위치,col위치


# Hungarian 돌리기
"""
print(regionNumbDict[5][5])
for i in range(300):
    print("="*30)
    print(regionCellDict[5][5][i])
    idx = regionCellDict[5][5][i][2]
    #print(globCellX[idx], globCellY[idx], globCellH[idx], globCellW[idx])
"""
def makeHungrianGraph(row, col):
    cost = []
    cidx = -1
    for xc, yc, id, rowNumb, colNumb, rowMax, colMax in regionCellDict[row][col]:
        cidx = cidx+1
        ridx = -1
        costList = []
        for xp, yp, dRow, dCol in regionPosDict[row][col]:
            ridx = ridx+1
            if id != -1:displacement = abs(xc-xp) + abs(yc-yp)
            else: displacement = 300 # 큰 값.
            costList.append(round(displacement,4))
        cost.append(costList)
    return np.array(cost)

def runHungary(row, col):
    cellLocationList = []
    cost = makeHungrianGraph(row, col)
    row_ind, col_ind = linear_sum_assignment(cost)
    totalCost = cost[row_ind, col_ind].sum()
    pairs = list(zip(row_ind, col_ind))
    for cellIdx, posIdx in pairs:
        xCell, yCell, cellId, rowNumb, colNumb, rowMax, colMax = regionCellDict[row][col][cellIdx]
        xPos, yPos, rowPos, colPos = regionPosDict[row][col][posIdx]
        cellLocationList.append([cellId, rowPos, colPos, rowNumb, colNumb, rowMax, colMax])
    return cellLocationList, totalCost


hungDivCellXY = {}
getCellRowColFromPos = {}
priceMtx = {}
overlapMtx = {}
cellInfoDict = {}
ILPResultDict = {}
def makeHungCellXY(cellList, row, col):
    """
    row, col 정보로 부터 original 좌표정보 추출 이후, cell 마다, rowNumb, colNumb 에서의 좌표정보 저장.
    hungDivCellXY[cell][rowNumb][colNumb] --> [x, y] 
    """
    xOrg = regionXConst*col
    yOrg = regionYConst*row
    cellId, rowPos, colPos, rowNumb, colNumb= cellList[0], cellList[1], cellList[2], cellList[3], cellList[4]
    xValue = xOrg + colPos*dcellWidth*unitWidth
    yValue = yOrg + rowPos*dcellHeight*unitHeight
    
    if cellId not in  hungDivCellXY.keys(): hungDivCellXY[cellId] = {}
    if rowNumb not in hungDivCellXY[cellId].keys(): hungDivCellXY[cellId][rowNumb] = {}

    hungDivCellXY[cellId][rowNumb][colNumb] = [xValue, yValue]

def makeCellRowColFromPosDict(cellList, row, col):
    """    
    getCellRowColFromPos[row, col, rowPos, colPos] --> cell, rowNumb, colNumb
    """
    if row not in getCellRowColFromPos.keys(): getCellRowColFromPos[row] = {}
    if col not in getCellRowColFromPos[row].keys(): getCellRowColFromPos[row][col] = {}

    cellId, rowPos, colPos, rowNumb, colNumb = cellList[0], cellList[1], cellList[2], cellList[3], cellList[4]
    if rowPos not in getCellRowColFromPos[row][col].keys(): getCellRowColFromPos[row][col][rowPos] = {}

    getCellRowColFromPos[row][col][rowPos][colPos] = [cellId, rowNumb, colNumb]

def calculatePrice(row, col, targCell, targRowNumb, targColNumb, posCell, posRowNumb, posColNumb):
    ##strLog = "\n At Region[" + row +"][" + col + "]\n " + "cell : " + targCell + "(" + targRowNumb + ", "+ targColNumb + ") is swaped with "
    #+ posCell + "(" + posRowNumb + ", " + posColNumb + ")\n"
    #fLogA.write(strLog)
    #print(targCell, targRowNumb, targColNumb, globDivCellXY[targCell].keys())

    globTargX, globTargY = globDivCellXY[targCell][targRowNumb][targColNumb]
    hungTargX, hungTargY = hungDivCellXY[targCell][targRowNumb][targColNumb]
    
    #print(posCell, posRowNumb, posColNumb, hungDivCellXY[targCell].keys())
    globPosX,  globPosY = globDivCellXY[posCell][posRowNumb][posColNumb]
    hungPosX, hungPosY = hungDivCellXY[posCell][posRowNumb][posColNumb]

    displacementBefore = abs(globTargX - hungTargX) + abs(globTargY - hungTargY)
    + abs(globPosX - hungPosX) + abs(globPosY - hungPosY)

    displacementAfter =  abs(globTargX - hungPosX) + abs(globTargY - hungPosY)
    + abs(globPosX - hungTargX) + abs(globPosY - hungTargY)

    return displacementAfter - displacementBefore

def calculatePrice2(row, col, targCell, targRowNumb, targColNumb, pRow, pCol):
    price =0
    xOrg = regionXConst*col
    yOrg = regionYConst*row
    xValue = xOrg + pCol*dcellWidth*unitWidth
    yValue = yOrg + pRow*dcellHeight*unitHeight

    globTargX, globTargY = globDivCellXY[targCell][targRowNumb][targColNumb]
    hungTargX, hungTargY = hungDivCellXY[targCell][targRowNumb][targColNumb]

    displacementBefore = abs(globTargX - hungTargX) + abs(globTargY - hungTargY)
    displacementAfter =  abs(globTargX - xValue) + abs(globTargY - yValue)

    return displacementAfter - displacementBefore

def makePriceMtx(cellList, row, col):
    # cellList = cellId, rowPos, colPos, rowNumb, colNumb, rowMax, colMax 하나에 대해서.
    
    # price mtx 만들기.
    if row not in priceMtx.keys(): priceMtx[row] = {}
    if col not in priceMtx[row].keys(): priceMtx[row][col] = {}

    # overlap mtx 만들기. <-- 추가 됨.
    if row not in overlapMtx.keys(): overlapMtx[row] = {}
    if col not in overlapMtx[row].keys(): overlapMtx[row][col] = {}

    # cellId --> width/height dict 만들기.
    # cellInfoDict[cellId] = {width, height} <-- int 환산단위. ex) {2, 3} // 2행 3열.
    if row not in cellInfoDict.keys(): cellInfoDict[row] = {}
    if col not in cellInfoDict[row].keys(): cellInfoDict[row][col] = {}

    # ILP Result Dict 만들기.
    if row not in ILPResultDict.keys(): ILPResultDict[row] = {}
    if col not in ILPResultDict[row].keys(): ILPResultDict[row][col] = []

    cellId, rowPos, colPos, rowNumb, colNumb, rowMax, colMax = cellList[0], cellList[1], cellList[2], cellList[3], cellList[4], cellList[5], cellList[6]
    posList = []
    price = 0

    if cellId == -1: return

    cellInfoDict[row][col][cellId] = [str(rowMax), str(colMax)]

    for dy in range(1, rowMax+1):
        for dx in range(1, colMax+1):
            # price mtx operation
            pRow = dy - rowNumb + rowPos
            pCol = dx - colNumb + colPos

            if pRow < 0 or pRow >= regionDcellYea or pCol < 0 or pCol >= regionDcellXea: continue
            posList.append([pRow, pCol, dy, dx])

            # overlap mtx operation
            if pRow not in overlapMtx[row][col].keys(): overlapMtx[row][col][pRow] = {}
            if pCol not in overlapMtx[row][col][pRow].keys():overlapMtx[row][col][pRow][pCol] = [[cellId, rowNumb, colNumb]]
            else: overlapMtx[row][col][pRow][pCol].append([cellId, rowNumb, colNumb])

    for pRow, pCol, dy, dx in posList:
        targCell, targRowNumb, targColNumb = cellId, dy, dx
        #print(cellId, row, col, pRow, pCol, getCellRowColFromPos[row][col].keys())
        posCell, posRowNumb, posColNumb = getCellRowColFromPos[row][col][pRow][pCol]

        if posCell != -1:
            price = price + calculatePrice(row, col, targCell, targRowNumb, targColNumb, posCell, posRowNumb, posColNumb)
        else:
            price = price + calculatePrice2(row, col, targCell, targRowNumb, targColNumb, pRow, pCol)

    if cellId not in priceMtx[row][col].keys(): priceMtx[row][col][cellId] = {}
    if rowNumb not in priceMtx[row][col][cellId].keys(): priceMtx[row][col][cellId][rowNumb] = {}
    priceMtx[row][col][cellId][rowNumb][colNumb] = price

def runILP(row, col):
    Y, X = range(regionDcellYea), range(regionDcellXea) # Y = range(10) : 0~9 # X = range(30) : 0~29

    # 1. model generation
    m = Model()

    # 2. cell Id <--> index matrix 생성.
    #    ex) IdMtx[idx] = cId
    IdMtx = {}
    cIdMtx = {}
    idx = 0
    for cId in priceMtx[row][col].keys():
        IdMtx[idx] = cId
        cIdMtx[cId] = idx
        idx+=1
    Idx = range(idx) # Idx = 0 ~ idx-1

    x = [[[m.add_var(var_type=BINARY) # x[idx, i, j]
    for j in range(len(priceMtx[row][col][IdMtx[idx]][1].keys()))] 
    for i in range(len(priceMtx[row][col][IdMtx[idx]].keys()))] 
    for idx in Idx] 
    
    m.objective = minimize(
        xsum(
            priceMtx[row][col][IdMtx[idx]][i+1][j+1]*x[idx][i][j] 
            for idx in Idx 
            for i in range(len(priceMtx[row][col][IdMtx[idx]].keys()))
            for j in range(len(priceMtx[row][col][IdMtx[idx]][1].keys()))
        )
    )
    """
    Constraint 1. 
    : cell 마다 1 개 선택.
    """
    for idx in Idx:
        m += xsum(x[idx][i][j] 
        for i in range(len(priceMtx[row][col][IdMtx[idx]].keys())) 
        for j in range(len(priceMtx[row][col][IdMtx[idx]][1].keys()))) == 1
    
    """
    Constraint 2.
    : 겹치는 애들 제거.
      overlapMtx[row][col][pRow][pCol] = [cellId, rowNumb, colNumb], [cellId, rowNumb, colNumb], [cellId, rowNumb, colNumb] ...]
    """
    for pRow in overlapMtx[row][col].keys():
        for pCol in overlapMtx[row][col][pRow].keys():
            idxSet = set(); iSet = set(); jSet = set(); isReal = {}

            for cId, i, j in overlapMtx[row][col][pRow][pCol]:
                idx = cIdMtx[cId]
                idxSet.add(idx)
                iSet.add(i)
                jSet.add(j)

            for idx in idxSet:
                if idx not in isReal.keys(): isReal[idx] = {}
                for i in iSet:
                    if i not in isReal[idx].keys(): isReal[idx][i] = {}
                    for j in jSet:
                        if j not in isReal[idx][i].keys(): isReal[idx][i][j] = False

            for cId, i, j in overlapMtx[row][col][pRow][pCol]:
                idx = cIdMtx[cId]
                isReal[idx][i][j] = True
            print("@@@@@@@@@@@@@@")
            print(overlapMtx[row][col][pRow][pCol])
            print(isReal)
            print(idxSet, iSet, jSet)
            print("-----------------")
            m += xsum(x[idx][i-1][j-1] for idx in idxSet for i in iSet for j in jSet if isReal[idx][i][j] == True) <= 2

    m.optimize()
    numb = 0
    fLogB.write("#rowcol,"+str(row)+ "," + str(col)+"\n")
    for idx in Idx:
        for i in range(len(priceMtx[row][col][IdMtx[idx]].keys())):
            for j in range(len(priceMtx[row][col][IdMtx[idx]][1].keys())):
                if x[idx][i][j].x >= 0.99: 
                    #print(IdMtx[idx], i+1, j+1)
                    #print("cost is " , priceMtx[row][col][IdMtx[idx]][i+1][j+1])
                    
                    # str(i+1), str(j+1) : 선택된 cell의 rowNumb, colNumb
                    # cellInfoDict[row][col][IdMtx[idx]] : 선택된 cell의 rowMax, colMax
                    # 즉 저장되는건 선택된 cellId, row, col, rowMax, colMax
                    fLogB.write(str(IdMtx[idx])+"," + str(i+1)+ "," + str(j+1)+ "," + ",".join(cellInfoDict[row][col][IdMtx[idx]]) + "\n")
                    ILPResultDict[row][col].append([IdMtx[idx], i+1, j+1] + cellInfoDict[row][col][IdMtx[idx]])
                
posXYDict = {} # posXYDict[row][col][cellId] = [rowPos, colPos]     

def addPatchToFig2(fig, data):
    cellId = str(data[0]) + "\n(" + str(data[3]) + ", " + str(data[4]) + ")\n/(" + str(data[5]) + ", " + str(data[6]) + ")"
    row, col = data[1], data[2]
    left, width = .03*(col), .03*int(data[6])
    bottom, height = .1*(row), .1*int(data[5])
  
    right = left + width
    top = bottom + height

    #print(cellId, left, right, top, bottom)

    a,b,c = str(hex((data[0]*5)%256))[2:], str(hex((3*data[0]+30)%256))[2:], str(hex((data[0]+60)%256))[2:]
    if len(a) == 1: a = a + "0"
    if len(b) == 1: b = b + "0"
    if len(c) == 1: c = c + "0"
    colorStr = "#"+a+b+c

    p = patches.Rectangle((left, bottom), width, height, fill=True, color=colorStr)
    fig.add_artist(p)
    fig.text(0.5*(left+right), 0.5*(bottom+top), cellId,
         horizontalalignment='center', verticalalignment='center',
         fontsize=10, color='black')

def showDistribute2(row, col):
    fig = plt.figure()
    for cellId, rowNumb, colNumb, rowMax, colMax in ILPResultDict[row][col]:
        rowPos, colPos = posXYDict[row][col][cellId][rowNumb][colNumb]
        #print(cellId, rowPos, colPos)
        rowPosMod, colPosMod = rowPos - (rowNumb-1), colPos - (colNumb -1)
        cell = [cellId, rowPosMod, colPosMod, rowNumb, colNumb, rowMax, colMax]
        #print(cell)
        addPatchToFig2(fig, cell)
    plt.show()

def saveHungResult(cellLists):
    # cellList = [cellId, rowPos, colPos, rowNumb, colNumb, rowMax, colMax
    for cellList in cellLists:
        cellId, rowPos, colPos, rowNumb, colNumb = cellList[0], cellList[1], cellList[2], cellList[3], cellList[4]
        if row not in posXYDict.keys(): posXYDict[row] = {}
        if col not in posXYDict[row].keys(): posXYDict[row][col] = {}
        if cellId not in posXYDict[row][col].keys(): posXYDict[row][col][cellId] = {}
        if rowNumb not in posXYDict[row][col][cellId].keys(): posXYDict[row][col][cellId][rowNumb] = {}
        posXYDict[row][col][cellId][rowNumb][colNumb] = [rowPos, colPos]

# Test Code
for row, col in [[0,0]]:
    cellLists, totalCost = runHungary(row, col) # cellList = [cellId, rowPos, colPos, rowNumb, colNumb, rowMax, colMax
    saveHungResult(cellLists)
    #for cellList in cellLists:
    #    print(cellList)
    showDistribute(cellLists)
        
    # Data Generation
    for cellList in cellLists:
        makeHungCellXY(cellList, row, col)
        makeCellRowColFromPosDict(cellList, row, col)

    # Data Generation
    for cellList in cellLists:    
        makePriceMtx(cellList, row, col)

    runILP(row, col)
    showDistribute2(row, col)
    """
    idx = 0
    for cell in priceMtx[row][col].keys():
        for pRow in priceMtx[row][col][cell].keys():
            for pCol in priceMtx[row][col][cell][pRow].keys():
                idx+=1
                print(idx, cell, pRow, pCol)
    #showDistribute(positionList)
    """
    
#showDistribute(cellLists)
#print(totalCost)
#print(regionCellDict[1][1][299]) # [14.4062, 4.1479, 9254]
#print(regionPosDict[1][1][287])  # [15.04, 14.592, 9, 17]

#candidate = makeCandidate(cellList)  # 
#result = reDistribute(candidate)
#showDistribteXYWH(result)

# last code
"""
t1 = time()
totalDisplacement = 0
for row in range(numOfRegionRow):
    if row == int(numOfRegionRow/10): t2= time(); sec = t2-t1; print("10 percent done. it takes ", datetime.timedelta(seconds=sec))
    elif row == int(numOfRegionRow/3): t2= time(); sec = t2-t1; print("30 percent done. it takes ", datetime.timedelta(seconds=sec))
    elif row == int(numOfRegionRow/2): t2= time(); sec = t2-t1; print("50 percent done. it takes ", datetime.timedelta(seconds=sec))
    elif row == int(numOfRegionRow/1.3): t2= time(); sec = t2-t1; print("80 percent done. it takes ", datetime.timedelta(seconds=sec))
    for col in range(numOfRegionCol):
        cellList, totalCost = runHungary(row,col)
        totalDisplacement = totalDisplacement + totalCost
print("total Cost is ", totalDisplacement)
"""
