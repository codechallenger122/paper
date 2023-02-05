path = "C:\/Users\/김화평\/Desktop\/output\/output\/"
cellNetFile = path + "cell_net_match.txt"
netCellFile = path + "net_cell_match.txt"
placeLegFile = path + "place.txt"
placeOurFile = path + "our_algo_result.txt"

legTclFile = path + "leg_highlight.tcl"
ourTclFile = path + "our_highlight.tcl"
"""
cellNameMap = {}
cellNetMap = {}
netNameMap = {}
netCellMap = {}

cellWidth = {}   # float
cellHeight = {}  # float
cellLegX = {}    # float
cellLegY = {}    # float
cellOurX = {}    # float
cellOurY = {}    # float
"""
def getLegHPWL(nId):
    cIds = netCellMap[nId]
    xMin = 1000
    yMin = 1000
    xMax = -1
    yMax = -1
    for cId in cIds:
        x= float(cellLegX[cId])
        y= float(cellLegY[cId])
        w = float(cellWidth[cId])
        h = float(cellHeight[cId])
        xpos = x + w/2
        ypos = y + h/2
        if xpos < xMin: xMin = xpos
        if xpos > xMax: xMax = xpos     
        if ypos < yMin : yMin = ypos
        if ypos > yMax : yMax = ypos
    return xMax - xMin + yMax - yMin
def getOurHPWL(nId):
    cIds = netCellMap[nId]
    xMin = 1000
    yMin = 1000
    xMax = -1
    yMax = -1

    for cId in cIds:
        x= float(cellOurX[cId])
        y= float(cellOurY[cId])
        w = float(cellWidth[cId])
        h = float(cellHeight[cId])
        xpos = x + w/2
        ypos = y + h/2        
        if xpos < xMin: xMin = xpos
        if xpos > xMax: xMax = xpos     
        if ypos < yMin : yMin = ypos
        if ypos > yMax : yMax = ypos
    return xMax - xMin + yMax - yMin
def getLegNetPos(nId):
    xSum = 0
    ySum = 0
    n = len(netCellMap[nId])
    for cId in netCellMap[nId]:
        xSum+= float(cellLegX[cId])
        ySum+= float(cellLegY[cId])
    return [round(xSum/n,2), round(ySum/n,2)]
def getOurNetPos(nId):
    xSum = 0
    ySum = 0
    n = len(netCellMap[nId])
    for cId in netCellMap[nId]:
        xSum+= float(cellOurX[cId])
        ySum+= float(cellOurY[cId])
    return [round(xSum/n,2), round(ySum/n,2)]

# 1 단계
cellNameMap = {}
cellNetMap = {}
with open(cellNetFile, "r") as f:
    while True:
        line = f.readline()
        if not line: break
        args = line[:-1].split(":")
        cId, cellName = args[0], args[1]
        nets = args[2:]

        if cId not in cellNameMap.keys():
            cellNameMap[cId] = cellName
        else:
            print("에러 확륭이 있음. duplicate cId")
        
        if cId not in cellNetMap:
            cellNetMap[cId] = nets
        else:
            print("에러 확륭이 있음. duplicate cId")

# 2 단계
netNameMap = {}
netCellMap = {}
with open(netCellFile, "r") as f:
    while True:
        line = f.readline()
        if not line: break
        args = line[:-1].split(":")
        nId, netName = args[0], args[1]
        cells = args[2:]

        if nId not in netNameMap.keys():
            netNameMap[nId] = netName
        else:
            print("에러 확륭이 있음. duplicate nId")
        
        if nId not in netCellMap:
            netCellMap[nId] = cells
        else:
            print("에러 확륭이 있음. duplicate nId")

# 3 단계
cellWidth = {}   # float
cellHeight = {}  # float
cellLegX = {}    # float
cellLegY = {}    # float
cellOurX = {}    # float
cellOurY = {}    # float
with open(placeLegFile, "r")  as f:
    while True:
        line = f.readline()
        if not line: break
        args = line[:-1].split(":")
        cId = args[0]
        xpos, ypos, width, height = args[2], args[3], args[6], args[7]
        cellWidth[cId] = width
        cellHeight[cId] = height
        cellLegX[cId] = xpos
        cellLegY[cId] = ypos

with open(placeOurFile, "r") as f:
    idx = 0
    while True:
        line = f.readline()
        if not line: break
        cId = str(idx)
        args = line[:-1].split(":")
        xpos, ypos = args[1], args[2]
        cellOurX[cId] = xpos
        cellOurY[cId] = ypos
        idx +=1

# net 별 (1) HPWL 크기와 (2) cell 들의 center 지점 구하기

for nId in range(5):
    nId = str(nId)
    print(getLegHPWL(nId))
    print(getOurHPWL(nId))

for nId in range(5):
    nId = str(nId)    
    print(getLegNetPos(nId))
    print(getOurNetPos(nId))

# Final
legNetList = [] # [ [netName, HPWL 값, x좌표, y좌표], [netName, HPWL 값, x좌표, y좌표],  ... ]
ourNetList = [] # [ [netName, HPWL 값, x좌표, y좌표], [netName, HPWL 값, x좌표, y좌표],  ... ]
netNumb = len(netNameMap)
for nId in range(netNumb):
    nId = str(nId)
    netName = netNameMap[nId]
    legList = []
    ourList = []
    legList.append(netName)
    ourList.append(netName)
    
    legList.append(getLegHPWL(nId))
    ourList.append(getOurHPWL(nId))

    cIds = netCellMap[nId]
    cells = []
    for cId in cIds:
        cells.append(cellNameMap[cId])
    legList.append(cells)
    ourList.append(cells)

    legNetList.append(legList)
    ourNetList.append(ourList)

legNetList.sort(key = lambda x : x[1], reverse=True)
ourNetList.sort(key = lambda x : x[1], reverse=True)

legNetNumb = 0
for i in range(10000):
    if legNetList[i][1] < 100:
        print(i, legNetList[i][1])
        legNetNumb = i
        break

ourNetNumb = 0
for i in range(10000):
    if ourNetList[i][1] < 100:
        print(i, ourNetList[i][1])
        ourNetNumb = i
        break

"""
legNetList # 0 ~ 1127 의 net 이 HPWL = 100 이상.
ourNetList # 0 ~ 427 의 net 이 HPWL = 100 이상.
"""
 
legCellList = []
for i in range(legNetNumb):
    cells = legNetList[i][2]
    if len(cells) > 30: continue
    legCellList.extend(cells)

ourCellList = []
for i in range(ourNetNumb):
    cells = ourNetList[i][2]
    if len(cells) > 30: continue
    ourCellList.extend(cells)   

print(len(legCellList))
print(len(ourCellList))

with open(legTclFile, "w") as f:
    for cell in legCellList:
        f.write("highlight [dbGet -p top.insts.name {}]\n".format(cell))

with open(ourTclFile, "w") as f:
    for cell in ourCellList:
        f.write("highlight [dbGet -p top.insts.name {}]\n".format(cell))
