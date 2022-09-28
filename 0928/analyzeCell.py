import os
"""
1. cellName, width, height
2. unitWidth, unitHeight
3. cellName, xLL, yLL, xUR, yUR  (glob result)
4. cellName, xLL, yLL, xUR, yUR  (leg  result)

"""
veriFile = "design.v"
cellFile = "cells.lef"

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

cellCntDict = {}
totInstNumber = 0
with open(veriFile, "r") as f:
	while True:
		line = f.readline()
		if not line: break
		lines = line.split()
		if len(lines) < 3: continue
		if lines[0] in cellWHDict.keys():
			totInstNumber +=1
			cellName = lines[0]
			if cellName not in cellCntDict.keys(): cellCntDict[cellName] = 1
			else: cellCntDict[cellName] += 1

idx = 0
for cell in  cellCntDict.keys():
	idx +=1
	width, height = cellWHDict[cell]
	print(idx, ". cell= ", cell, " width : ", width, " height : ", height, " #numb = ", cellCntDict[cell])
print("total number : ", totInstNumber)
