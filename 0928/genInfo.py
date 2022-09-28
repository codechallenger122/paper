import os
"""
1. cellName, width, height
2. unitWidth, unitHeight
3. cellName, xLL, yLL, xUR, yUR  (glob result)
4. cellName, xLL, yLL, xUR, yUR  (leg  result)

"""
design = os.getcwd().split("/")[-1]
archive = "/home/users/khp1107/paper/Runbenchmark/output/" + design + "/"

cellFile = "cells.lef"
veriFile = "design.v"
techFile = "tech.lef"
floorFile = "floorplan.def"
globFile = "place_glob.def"
legFile = "place_leg.def"

if not os.path.exists(archive): os.mkdir(archive)

logFileInfo =  archive + "info.txt"
logFileGlob =  archive + "global.txt"
logFileLeg  =  archive + "legali.txt"

cellWHDict = {}
with open(cellFile, "r") as f:
	while True:
		line = f.readline()
		if not line: break
		lines = line.split()
		if len(lines) == 0: continue
		if lines[0] == "MACRO":
			cellName = lines[1]
		elif lines[0] == "SIZE":
			width, height = lines[1], lines[3]
			cellWHDict[cellName] = [width, height]

flag = "off"
with open(techFile, "r") as f:
	while True:
		line = f.readline()
		if not line: break
		lines = line.split()
		if len(lines) == 0: continue
		if lines[0] == "DATABASE" and lines[1] == "MICRONS":
			formFactor = int(lines[2])

		elif lines[0] == "SITE": flag ="on"

		if flag == "on" and lines[0] == "SIZE":
			unitWidth, unitHeight = lines[1], lines[3]

# where to round up
sig = max(len(unitWidth.split(".")[-1]), len(unitWidth.split(".")[-1]))
print("sig is ", sig)

with open(floorFile, "r") as f:
	while True:
		line = f.readline()
		if not line: break
		lines = line.split()
		if len(lines) == 0: continue
		if lines[0] == "DIEAREA":
			blockX, blockY = float(lines[6]), float(lines[7])

flag = "off"
globCellDict = {}
with open(globFile, "r") as f:
	while True:
		line = f.readline()
		if not line: break
		lines = line.split()
		if len(lines) < 2: continue
		if lines[0] == "COMPONENTS":
			flag = "on"
			numOfCellG = lines[1]
			
		if lines[0] == "END" and lines[1] == "COMPONENTS":
			break
	
		if flag == "on" and len(lines) > 4:
			instName, xLL, yLL, mstName = lines[1], lines[-4], lines[-3], lines[2]
			globCellDict[instName] = [xLL, yLL, mstName]

if int(len(globCellDict.keys())) != int(numOfCellG):
	print(len(globCellDict.keys()), numOfCellG)
	print("while reading place_glob.def file.. some cell omitted")
print("placed_glob.def reading done.")

flag = "off"
legCellDict = {}
with open(legFile, "r") as f:
	while True:
		line = f.readline()
		if not line: break
		lines = line.split()

		if len(lines) < 2: continue
		if lines[0] == "COMPONENTS":
			flag = "on"
			numOfCellL = lines[1]
			
		if lines[0] == "END" and lines[1] == "COMPONENTS":
			break
	
		if flag == "on" and len(lines) > 4:
			instName, xLL, yLL, mstName = lines[1], lines[-4], lines[-3], lines[2]
			legCellDict[instName] = [xLL, yLL, mstName]

if int(len(legCellDict.keys())) != int(numOfCellL):
	print("while reading place_glob.def file.. some cell omitted")

if numOfCellG != numOfCellL: print("number of global cell is not equal to number of legal cell..")

print("placed_leg.def reading done.")

f1 = open(logFileInfo, "w")
f1.write("blockX:" + str(blockX/formFactor) +"\n")
f1.write("blockY:" + str(blockY/formFactor) +"\n")
f1.write("unitWidth:" + unitWidth +"\n")
f1.write("unitHeight:" + unitHeight +"\n")
f1.write("numOfCell:" + numOfCellG + "\n")


f2 = open(logFileGlob, "w")
for instName in globCellDict.keys():
	xll, yll, mstName = globCellDict[instName]
	xLL, yLL = float(xll), float(yll)
	width, height = cellWHDict[mstName]
	f2.write(instName + ":" + str(round(xLL/formFactor, sig)) + ":" + str(round(yLL/formFactor, sig)) + ":" + width + ":" + height + ":" + mstName + "\n")
f2.close()

f2 = open(logFileLeg, "w")
for instName in legCellDict.keys():
	xll, yll, mstName = legCellDict[instName]
	xLL, yLL = float(xll), float(yll)
	width, height = cellWHDict[mstName]
	f2.write(instName + ":" + str(round(xLL/formFactor, sig)) + ":" + str(round(yLL/formFactor, sig)) + ":" + width + ":" + height + ":" + mstName + "\n")
#	dx, dy = cellWHDict[mstName]
#	xUR, yUR = round(xLL/formFactor + float(dx), sig), round(yLL/formFactor + float(dy), sig)
#	f2.write(instName + ":" + str(round(xLL/formFactor, sig)) + ":" + str(round(yLL/formFactor, sig)) + ":" + str(xUR) + ":" + str(yUR) + ":" + mstName + "\n")

f2.close()
