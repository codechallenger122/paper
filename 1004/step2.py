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

dcellWidth = 2   # divided cell의 width
dcellHeight = 1  # divided ce ll의 height 
regionDcellXea = 50   # 30 x 5(dcellWidth)  = 150개 col grid ; Region에 있는 dcell의 총 col 개수
regionDcellYea = 12   # 10 x 1(dcellHeight) =  10개 row grid ; region에 있는 dcell의 총 row 개수

device = "mgc_des_perf_1"
device = "mgc_fft_1"

#pwd1 = "C:\/Users\/김화평\/Desktop\/workSpace\/benchMark\/"
pwd1 = "C:\/Users\/HPK\/Desktop\/paper\/benchMark\/"
pwd = pwd1 + device + "\/log\/"

logFile = pwd + "ILP_processing.log"
logFileA = pwd + "changeleg.log" # swap & price 계산.
logFileB = pwd + "last.log"      # ILP 결과 저장.
logFileC = pwd + "place_leg.txt" # 최종 아웃풋

fLog = open(logFile, "w")
fLogA = open(logFileA, "w")
fLogB = open(logFileB, "w")
fLogC = open(logFileC, "w")

# 1. Global variable Define
# at Step 0.
nodeFileName = pwd1 + device + "\/global.txt" ## input
infoFileName = pwd1 + device + "\/info.txt"
globCellName = []; globCellX = []; globCellY = []; globCellW = []; globCellH = []
legCellX = []; legCellY = []
xMax = float("-inf"); yMax = float("-inf")
sortedCellList = []
numOfCell = 0 ## original cell 개수.

# at Step 1.
unitHeight=0; unitWidth=0; blockHeight=0; blockWidth=0
with open(infoFileName, "r") as f:
    while True:
        line = f.readline()
        if not line: break
        lines = line.split(":")
        if len(lines) == 2 and lines[0] == "blockX": blockWidth = float(lines[1].split()[0])
        elif len(lines) == 2 and lines[0] == "blockY": blockHeight = float(lines[1].split()[0])
        elif len(lines) == 2 and lines[0] == "unitWidth": unitWidth = float(lines[1].split()[0])
        elif len(lines) == 2 and lines[0] == "unitHeight": unitHeight = float(lines[1].split()[0])      

print("unitWidth : ", unitWidth)
print("unitHeight : ", unitHeight)
print("blockWidth : ", blockWidth)
print("blockHeight : ", blockHeight)

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
with open(nodeFileName, "r") as f:
    while True:
        line = f.readline()
        if not line:break
        args = line.split(":")
        if len(args) != 6:
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

globCellXY = {}
cIdToNameDict = {}
idx = 0
for name, xLL, yLL, width, height in sortedCellList:
    globCellName.append(name)
    globCellX.append(xLL)
    globCellY.append(yLL)
    globCellW.append(width)
    globCellH.append(height)
    globCellXY[idx] = [xLL, yLL]
    cIdToNameDict[idx] = name
    idx+=1


""" ===================================================================================================== """
print("1. numOfRegionRow = ", numOfRegionRow)
print("   numOfRegionCol = ", numOfRegionCol)
print("2. regionUcellYea = ", regionUcellYea)
print("   regionUcellXea  = ", regionUcellXea)
regionCellFile = pwd + "cellAssignedToRegion.txt"
debugFile = pwd + "debug.txt"
fBug = open(debugFile, "w")
# visualize func
def addPatchToFig(fig, data):
    cellId = str(data[0]) + "\n(" + str(data[3]) + ", " + str(data[4]) + ")\n/(" + str(data[5]) + ", " + str(data[6]) + ")"
    row, col = data[1], data[2]
    left, width = .025*(col), .025
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
            else: displacement = 3000 # 큰 값.
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
rowMaxColMaxInfo = {}

cellInfoDict = {}
ILPResultDict = {} # ILPResultDict[row][col] = [ [cId, code], [cId, code], ... ]
def runILP(row, col):
    fLog.write("row:" + str(row) + " and col:" + str(col) + " is processing.\n")
    if row not in ILPResultDict.keys(): ILPResultDict[row] = {}
    if col not in ILPResultDict[row].keys(): ILPResultDict[row][col] = []
    # 1. model generation
    m = Model()

    # Xcid, j 의 경우 index 기반으로 움직이므로, cid <--> idx convert mtx 필요.
    IdMtx = {}
    cIdMtx = {}
    idx = 0

    codeMtx = {}
    decodeMtx = {}
    for cId in priceMtx[row][col].keys():
        IdMtx[idx] = cId
        cIdMtx[cId] = idx
        
        if idx not in codeMtx.keys(): codeMtx[idx] = {}
        if idx not in decodeMtx.keys(): decodeMtx[idx] = {}

        decodeIdx = 0 
        for code in priceMtx[row][col][cId].keys():
            codeMtx[idx][code] = decodeIdx 
            decodeMtx[idx][decodeIdx] = code
            decodeIdx +=1
        idx+=1
    Idx = range(idx) # Idx = 0 ~ idx-1

    # 2. x[idx, j] define.
    x = [[m.add_var(var_type=BINARY) 
    for j in range(len(priceMtx[row][col][IdMtx[idx]].keys()))] 
    for idx in Idx] 

    # 3. min(sigma(p[idx, j]*x[idx,j])) 를 목적함수로 설정.
    m.objective = minimize(
        xsum(
            priceMtx[row][col][IdMtx[idx]][decodeMtx[idx][j]]*x[idx][j] 
            for idx in Idx 
            for j in range(len(priceMtx[row][col][IdMtx[idx]].keys()))
        )
    )
    """
    Constraint 1. 
    : cell 마다 1 개 선택.
    """
    for idx in Idx:
        m += xsum(x[idx][j] 
        for j in range(len(priceMtx[row][col][IdMtx[idx]].keys()))) == 1
    
    """
    Constraint 2.
    : 겹치는 애들 제거.
      overlapMtx[row][col][pRow][pCol] = [cellId, rowNumb, colNumb], [cellId, rowNumb, colNumb], [cellId, rowNumb, colNumb] ...]
    """
    for overCode in overlapMtx[row][col].keys():
        idxSet = set(); decodeSet = set(); isTrue = {}
        
        for cId, code in overlapMtx[row][col][overCode]:
            idx = cIdMtx[cId]
            idxSet.add(idx)
            decode = codeMtx[idx][code]
            decodeSet.add(decode)

        for idx in idxSet:
            if idx not in isTrue.keys(): isTrue[idx] = {}
            for decode in decodeSet:
                if decode not in isTrue[idx].keys(): isTrue[idx][decode] = False

        for cId, code in overlapMtx[row][col][overCode]:
            idx = cIdMtx[cId]
            decode = codeMtx[idx][code]
            isTrue[idx][decode] = True

        for idx in idxSet:
            for decode in decodeSet:
                if isTrue[idx][decode] == True:
                    fBug.write("x[" + str(IdMtx[idx]) + "][" + str(decodeMtx[idx][decode]) + "] +")
            fBug.write(" 0 <= 1\n")        
        m += xsum(x[idx][j] for idx in idxSet for j in decodeSet if isTrue[idx][j] == True) <= 1

    m.optimize()
    numb = 0
    fLogB.write("#rowcol,"+str(row)+ "," + str(col)+"\n")
    for idx in Idx:
        for j in range(len(priceMtx[row][col][IdMtx[idx]].keys())):
            if x[idx][j].x >= 0.99: 
                print(IdMtx[idx], "is assigned to ", decodeMtx[idx][j])
                ILPResultDict[row][col].append([IdMtx[idx], decodeMtx[idx][j]])
    fLog.write("row:" + str(row) + " and col:" + str(col) + " succeed !\n")

posXYDict = {} # posXYDict[row][col][cellId] = [rowPos, colPos]     
def addPatchToFig2(fig, data):
    cellId = str(data[0]) + "\n (" + str(data[3]) + ", " + str(data[4]) + ")"
    row, col = data[1], data[2]
    left, width = .025*(col), .025*int(data[4])
    bottom, height = .1*(row), .1*int(data[3])
  
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
    if col == numOfRegionCol -1: regionXmax = int(lastRegionUcellXea/dcellWidth)
    else: regionXmax = regionDcellXea
    for cellId, code in ILPResultDict[row][col]:
        i = code//regionXmax
        j = code%regionXmax
        rowMax, colMax = rowMaxColMaxInfo[row][col][cellId]
        cell = [cellId, i, j, rowMax, colMax]
        print(cellId, i, j, rowMax, colMax)
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

def calculateCost(row, col, i, j, cellId, rowMax, colMax):
    # i = rowPosMod, j=colPosMod
    xGlob, yGlob = globCellXY[cellId]
    
    xOrg, yOrg = 0, 0
    if col < numOfRegionCol:
        xOrg = unitWidth * (regionUcellXea * col)
    else:
        xOrg = unitWidth * (regionUcellXea * (col-1) + lastRegionUcellXea)

    if row < numOfRegionRow:
        yOrg = unitHeight * (regionUcellYea * row)
    else: 
        yOrg = unitHeight * (regionUcellYea * (row-1) + lastRegionUcellYea)

    xLega, yLega = xOrg + j*dcellWidth*unitWidth, yOrg + i*dcellHeight*unitHeight
    cost = abs(xLega-yGlob) + abs(yLega-yGlob)
    costFinal = cost * rowMax * colMax
    return costFinal

def makePriceAndOverlapMtx(row, col, cellList, margin):
    """
    예시.
    cellList = ["A", 1,1,2,2,2,3]
    makePriceAndOverlapMtx(1, 2, cellList, 2)
    priceMtx[row][col][cellId][code] = price    
    // code = 30*i+j <-- code represent cellId's position at region.
    overlapMtx[row][col][overCode] = [[cellId, code], [cellId, code], ... ]
    // overCode = 30*i+j <-- code represent position at region.
    """
    
    # price mtx 만들기.
    if row not in priceMtx.keys(): priceMtx[row] = {}
    if col not in priceMtx[row].keys(): priceMtx[row][col] = {}

    # overlap mtx 만들기. <-- 추가 됨.
    if row not in overlapMtx.keys(): overlapMtx[row] = {}
    if col not in overlapMtx[row].keys(): overlapMtx[row][col] = {}

    # rowMax, colMax 정보 저장.
    if row not in rowMaxColMaxInfo.keys(): rowMaxColMaxInfo[row] = {}
    if col not in rowMaxColMaxInfo[row].keys(): rowMaxColMaxInfo[row][col] = {}   

    cellId, rowPos, colPos, rowNumb, colNumb, rowMax, colMax = cellList
    rowMaxColMaxInfo[row][col][cellId] = [rowMax, colMax]

    rowPosMod = rowPos - (rowNumb - 1) # 현재 rowPos 를 (rowNumb = 1, colNumb = 1) 기준 position 으로 변경.
    colPosMod = colPos - (colNumb - 1) # 현재 rowPos 를 (rowNumb = 1, colNumb = 1) 기준 position 으로 변경.

    rowPosModMax = rowPosMod + (rowMax -1)
    colPosModMax = colPosMod + (colMax -1)

    # 0. region 안에 완전히 속하는 candidate 만들기.
    generator = [] # 유의미한 position으로 assign 된 rowPosMod, colPosMod 의 집합.

    if col == numOfRegionCol -1: regionXmax = int(lastRegionUcellXea/dcellWidth)
    else: regionXmax = regionDcellXea

    if row == numOfRegionRow -1: regionYmax = int(lastRegionUcellYea/dcellHeight)
    else: regionYmax = regionDcellYea

    if margin == 0: 
        if rowPosMod >=0 and rowPosModMax < regionYmax and colPosMod >=0 and colPosModMax < regionXmax:
            generator.append([rowPosMod, colPosMod])
    else:
        for i in range(rowPosMod-margin, rowPosMod+margin+1):
            for j in range(colPosMod-margin, colPosMod+margin+1):
                if i >=0 and (i + rowMax -1) < regionYmax and j >=0 and (j + colMax -1) < regionXmax:
                    generator.append([i,j])    

    # 1. encoding coordinate to scalar value ; dimension 줄이려고.
    for i,j in generator:
        code = regionXmax*i+j # cell 의 시작지점 postion 에 대해 encoding 한 code
        #print("cell 시작 code ", code)
        # (1) priceMtx
        """ 
            priceMtx[row][col][cellId][code] = price # code = 30*i+j
        """
        if cellId not in priceMtx[row][col].keys():priceMtx[row][col][cellId] = {}
        
        price = calculateCost(row, col, i, j, cellId, rowMax, colMax)
        if code not in priceMtx[row][col][cellId].keys():
            priceMtx[row][col][cellId][code] = price
        
        """ Position 이 유의미한 range 안에 들어왔기 때문에, 
            <- rowPosMod >=0 and rowPosModMAx < 10 and colPosMod >=0 and colPosModMax < 30
            30*i+j 로 encoding 을 해도 괜찮다. """

        # 2. overlapMtx
        for di in range(i, i+rowMax):
            for dj in range(j, j+colMax):
                overCode = di*regionXmax + dj # cell 이 커버하는 전 영역에 대한 code.
                #print("cover 영역 코드 ", overCode, "\n rowMax, colMax = ", rowMax, colMax)
                fBug.write("cover 영역 코드 " + str(overCode)+"\n cellId, code, rowMax, colMax = " +str(cellId) + ", " + str(code) +", "+ str(rowMax) + ", " +str(colMax)+"\n")
                if overCode not in overlapMtx[row][col].keys(): overlapMtx[row][col][overCode] = []
                overlapMtx[row][col][overCode].append([cellId, code])
        fBug.write("\n")

def writeLegPlace(row, col):
    xOrg, yOrg = 0, 0
    if col < numOfRegionCol:
        xOrg = unitWidth * (regionUcellXea * col)
    else:
        xOrg = unitWidth * (regionUcellXea * (col-1) + lastRegionUcellXea)

    if row < numOfRegionRow:
        yOrg = unitHeight * (regionUcellYea * row)
    else: 
        yOrg = unitHeight * (regionUcellYea * (row-1) + lastRegionUcellYea)
 
    for cellId, code in ILPResultDict[row][col]:
        i = code//regionDcellXea
        j = code%regionDcellXea
        cellName, xLega, yLega = cIdToNameDict[cellId], xOrg + j*dcellWidth*unitWidth, yOrg + i*dcellHeight*unitHeight
        fLogC.write(cellName + ":" + str(xLega) + ":" + str(yLega) + "\n")

def runFinal(row, col):
    cellLists, totalCost = runHungary(row, col) # cellList = [cellId, rowPos, colPos, rowNumb, colNumb, rowMax, colMax
    saveHungResult(cellLists)
    #showDistribute(cellLists)
    print("for row: ", row, " col: ", col, ", hungarian algorithm is done")
    margin = 3
    for cellList in cellLists:
        cId = cellList[0]
        if cId != -1:   
            makePriceAndOverlapMtx(row, col, cellList, margin)

    iidx = 0

    if col == numOfRegionCol -1: regionXmax = int(lastRegionUcellXea/dcellWidth)
    else: regionXmax = regionDcellXea

    for overCode in overlapMtx[row][col].keys():
        iidx+=1
        fBug.write("\n" + str(iidx)+ ". overcode : " + str(overCode)+ "\n")
        for cellId, code in overlapMtx[row][col][overCode]:
            i, j = code//regionXmax, code%regionXmax
            fBug.write("cell : " + str(cellId)+"(" + str(i)+", "+str(j)+")\n")
    runILP(row, col)
    #showDistribute2(row, col)
    writeLegPlace(row, col)
        
    # delete data..
    del ILPResultDict[row][col]
    del priceMtx[row][col]
    del overlapMtx[row][col]

def runTest(row, col):
    cellLists, totalCost = runHungary(row, col) # cellList = [cellId, rowPos, colPos, rowNumb, colNumb, rowMax, colMax
    saveHungResult(cellLists)
    showDistribute(cellLists)

    margin = 4
    for cellList in cellLists:
        cId = cellList[0]
        if cId != -1:
            makePriceAndOverlapMtx(row, col, cellList, margin)

    iidx = 0

    if col == numOfRegionCol -1: regionXmax = int(lastRegionUcellXea/dcellWidth)
    else: regionXmax = regionDcellXea

    for overCode in overlapMtx[row][col].keys():
        iidx+=1
        fBug.write("\n" + str(iidx)+ ". overcode : " + str(overCode)+ "\n")
        for cellId, code in overlapMtx[row][col][overCode]:
            i, j = code//regionXmax, code%regionXmax
            fBug.write("cell : " + str(code) + "_" + str(cellId)+"(" + str(i)+", "+str(j)+")\n")
    print("ok here..")
    runILP(row, col)
    showDistribute2(row, col)

    # delete data..
    del ILPResultDict[row][col]
    del priceMtx[row][col]
    del overlapMtx[row][col]

# Test Code
#for row, col in [[4, 4]]:
#    runTest(row, col)

# last code
def doTest():
    t1 = time()
    for row in range(4, 5):
        for col in range(4, 5):
            print("row: ", row, " col: ", col, "processing...")
            runFinal(row, col)
#doTest()

# last code
def doFinal():
    t1 = time()
    totalDisplacement = 0
    for row in range(numOfRegionRow):
        if row == int(numOfRegionRow/10): t2= time(); sec = t2-t1; print("10 percent done. it takes ", datetime.timedelta(seconds=sec))
        elif row == int(numOfRegionRow/3): t2= time(); sec = t2-t1; print("30 percent done. it takes ", datetime.timedelta(seconds=sec))
        elif row == int(numOfRegionRow/2): t2= time(); sec = t2-t1; print("50 percent done. it takes ", datetime.timedelta(seconds=sec))
        elif row == int(numOfRegionRow/1.3): t2= time(); sec = t2-t1; print("80 percent done. it takes ", datetime.timedelta(seconds=sec))
        for col in range(numOfRegionCol):
            print("row: ", row, " col: ", col, "processing...")
            runFinal(row, col)
doFinal()
