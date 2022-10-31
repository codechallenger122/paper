#pragma once
#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
#include <fstream>
#include <tuple>
#include <queue>
#include <cmath>
using namespace std;
vector<vector<int>> genBlockMap(float blockX, float blockY, float siteX, float siteY);
void modifyBlockCellMap(vector<vector<int>>& blockCellMap, vector<vector<float>>& cellInfo, float siteX, float siteY);
void modifyBlockAreaMap(vector<vector<int>>& blockAreaMap, vector<vector<float>>& cellInfo, float siteX, float siteY);
vector<string> parseString(string str, string del);
vector<string> genNameMap(string fileName);
vector<vector<float>> genCellInfoMap(string fileName);
vector<vector<int>> genNetInfoMap(string fileName);
vector<vector<int>> genCellNetInfoMap(string fileName);
bool compareHPWL(const tuple<int, float>& t1, const tuple<int, float>& t2);
vector<tuple<int, float>> genDataHPWL(vector<vector<int>>& cellsInNet, vector<vector<float>>& cellInfo);
float getDisplace(int cell, vector<vector<float>>& cellInfo);
float getAvgDisplace(vector<vector<float>>& cellInfo);
float getHPWL(int net, vector<vector<int>>& cellsInNet, vector<vector<float>>& cellInfo);
float getAvgHPWL(vector<vector<int>>& cellsInNet, vector<vector<float>>& cellInfo);
bool compareNet(const tuple<string, float, float, int>& t1, const tuple<string, float, float, int>& t2);
bool compareCell(const tuple<string, float>& t1, const tuple<string, float>& t2);
void netReport(vector<vector<int>>& cellsInNet, vector<vector<float>>& cellInfo, vector<string>& netName, string outFileName);
void cellReport(vector<vector<float>>& cellInfo, vector<string>& cellName, string outFileName);
queue<int> genCellQueue(vector<vector<int>>& cellsInNet, int nId, vector<vector<float>>& cellInfo);
vector<int> getWindowHPWL(int nId, vector<vector<int>>& cellsInNet, vector<vector<float>>& cellInfo, float siteX, float siteY);
vector<tuple<int, int>> getWindowCell(vector<int>& windowHPWL, int cId, vector<vector<float>>& cellInfo, float siteX, float siteY, float margin, vector<vector<int>>& blockCellMap);
vector<int> getCandidateCell(vector<tuple<int, int>>& windowCell, vector<vector<int>>& blockCellMap, int cId, vector<vector<float>>& cellInfo);
// cost, candidateCells[i] return.
tuple<float, int> calculateSwapCost(int nId, int cId, int scId, vector<vector<float>>& cellInfo, vector<vector<int>>& netsInCell, vector<vector<int>>& cellsInNet, string file, float margin);
bool compareCost(tuple<float, int> t1, tuple<float, int> t2);
// old functions. <- 지금 안씀.
vector<vector<string>> readFile(string fileName);
void checkEncrytion(vector<vector<string>> dataList, string dataListName);
