# 0. globally path 선언.
mainPath = "C:\/Users\/김화평\/Desktop\/ispd_2015_benchMark\/mgc_fft_1"
outputPath = mainPath + "\/res"
# 0-1. input File
designFile = mainPath + "\/design.v"
cellFile = mainPath + "\/cells.lef"
placeGlobalFile = mainPath + "\/place_global.txt"
placeLegalFile = mainPath + "\/place_legal.txt"
# 0-2. output file
netInfoFile = outputPath + "\/net_cell_match.txt"
cellInfoFile = outputPath + "\/cell_net_match.txt"
placeFile = outputPath + "\/place.txt"

# 1. function define.
def genPlaceFile():
	cellInfoDict = {} # cId[0]:instName[1]:xLeg[2]:yLeg[3]:xGlob[4]:yGlob[5]:xSize[6]:ySize[7]
	cIdInstMap = {}
	instCIdMap = {}
	with open(placeLegalFile, "r") as f:
		cId = 0
		while True:
			line = f.readline()
			if not line: break
			lines = line.split(":")
			if len(lines) == 0 : continue
			instName, xLeg, yLeg = lines[0], lines[1], lines[2]
			if instName not in cellInfoDict.keys():
				cellInfoDict[instName] = [xLeg, yLeg]
				cIdInstMap[str(cId)] = instName
				instCIdMap[instName] = str(cId)
				cId+=1
			else: print("something is wrong.. instName 은 중복될 수 없다.")
	cellNumber = cId
	print("\n 1. genPlaceFile 의 결과, 전체 cell의 개수는 ", cellNumber, " 이다.")

	with open(placeGlobalFile, "r") as f:
		while True:
			line = f.readline()
			if not line: break
			lines = line.split(":")
			if len(lines) == 0 : continue
			instName, xGlob, yGlob, xSize, ySize = lines[0], lines[1], lines[2], lines[3], lines[4]
			if instName not in cellInfoDict.keys():
				print("something is wrong.. instName 있어야 한다.")
			else: cellInfoDict[instName].extend([xGlob, yGlob, xSize, ySize])

	with open(placeFile, "w") as f:
		for idx in range(0,cellNumber):
			instName = cIdInstMap[str(idx)]
			f.write(str(idx) + ":" + instName + ":" + ":".join(cellInfoDict[instName]) + "\n")	

	return cIdInstMap, instCIdMap

def getCellList(cellFile):
	# cellFile = "cells.lef" 파일 읽어서 cell 종류를 파악한다.
	cellNameList = []
	with open(cellFile, "r") as f:
		while True:
			line = f.readline()
			if not line: break
			lines = line.split()
			if len(lines) == 0: continue
			if "MACRO" == lines[0]:
				cellName = lines[1]
				if cellName in cellNameList: continue
				else: cellNameList.append(cellName)
	# print(cellNameList)		
	print(" getCellList 의 결과 # of defined cellType in \"cells.lef\" is {}".format(len(cellNameList)))
	return cellNameList

def getNetInfo(designFile, cellNameList, instCIdMap, cIdInstMap):
	""" net_cell_match.txt 를 만든다.
    	형식은 nId:netName:cId:cId:...

	"""
	netCellDict = {}
	netNIdMap = {}
	nIdNetMap = {}
	with open(designFile, "r") as f:
		nId = 0
		while True:
			line = f.readline()
			if not line: break
			lines = line.split()
			if len(lines) == 0: continue
			if lines[0] not in cellNameList: continue
			if lines[0] == "endmodule": 
				print("successfully inspected all data.")
				break
			instName = lines[1]
			args = " ".join(lines[2:])[1:-2]
			nets = args.split(", ")
			for net in nets:
				i = 0
				while True:
					if net[i] == "(": break
					else: i+=1	
				netA = net[i+1:-1]
				if netA not in netCellDict.keys(): 
					netCellDict[netA] = [instCIdMap[instName]]
					netNIdMap[netA] = str(nId)
					nIdNetMap[str(nId)] = netA
					nId+=1
				else: netCellDict[netA].append(instCIdMap[instName])
	netNumber = nId
	print(" \n 2. getNetInfo 의 결과 전체 net 개수는 {} 이다.".format(netNumber))
	with open(netInfoFile, "w") as f:
		for nId in range(0,netNumber):
			netName = nIdNetMap[str(nId)]
			f.write(str(nId) + ":" + netName + ":" + ":".join(netCellDict[netName]) + "\n")

	cIdNetDict = {}
	for nId in range(0, netNumber):
		netName = nIdNetMap[str(nId)]
		for cId in netCellDict[netName]:
			if cId not in cIdNetDict.keys(): cIdNetDict[cId] = [str(nId)]
			else: cIdNetDict[cId].append(str(nId))

	with open(cellInfoFile, "w") as f:
		for cId in range(0,len(cIdNetDict.keys())):
			cellName = cIdInstMap[str(cId)]
			f.write(str(cId) + ":" + cellName + ":" + ":".join(cIdNetDict[str(cId)]) + "\n")	


# 2. mainCode 
cIdInstMap, instCIdMap = genPlaceFile()
cellNameList = getCellList(cellFile)
getNetInfo(designFile, cellNameList, instCIdMap, cIdInstMap)
"""
place 파일 포맷 : cId[0]:instName[1]:xLeg[2]:yLeg[3]:xGlob[4]:yGlob[5]:xSize[6]:ySize[7]
net 파일 포맷 : nId[0]:netName[1]:cId[2]:cId[3]:...
"""
