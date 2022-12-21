#pragma once
#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
#include <fstream>
#include <tuple>
#include <queue>
#include <cmath>
#include <ctime>
#include <map>
/* cellInfo   파일 포맷<float> : xLeg[0] : yLeg[1] : xGlob[2] : yGlob[3] : xSize[4] : ySize[5]
   cellsInNet 파일 포맷<int> : cId[0] : cId[1] : cId[2] ... */
using namespace std;
class DataHPWL {
public:
    float HPWL;
    float xMin;
    float xMinSub;
    float xMax;
    float xMaxSub;
    float yMin;
    float yMinSub;
    float yMax;
    float yMaxSub;
};
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
vector<bool> validCellCheck(vector<vector<int>>& cellsInNet, vector<vector<int>>& netsInCell);
queue<int> genCellQueue(vector<vector<int>>& cellsInNet, int nId, vector<vector<float>>& cellInfo);
vector<int> getWindowHPWL(int nId, vector<vector<int>>& cellsInNet, vector<vector<float>>& cellInfo, float siteX, float siteY);
vector<tuple<int, int>> getWindowCell(vector<int>& windowHPWL, int cId, vector<vector<float>>& cellInfo, float siteX, float siteY, float margin, vector<vector<int>>& blockCellMap, float maxDisp);
vector<int> getCandidateCell(vector<tuple<int, int>>& windowCell, vector<vector<int>>& blockCellMap, int cId, vector<vector<float>>& cellInfo, vector<bool> validCell);
vector<int> getCandidateCell_try(vector<tuple<int, int>>& windowCell, vector<vector<int>>& blockCellMap, int cId, vector<vector<float>>& cellInfo, vector<bool> validCell,
    float siteX, float siteY, vector<vector<int>>& blockAreaMap, int numOfRow, int numOfCol);
void updateHPWL_try(int cId, int scId_picked, vector<vector<int>>& cellsInNet, vector<vector<int>>& netsInCell, vector<vector<float>>& cellInfo, vector<DataHPWL>& HPWLArch,
    float siteX, float siteY, vector<vector<int>>& blockCellMap, vector<vector<int>>& blockAreaMap);
// cost, candidateCells[i] return.
tuple<float, int> calculateSwapCost(int nId, int cId, int scId, vector<vector<float>>& cellInfo, vector<vector<int>>& netsInCell, vector<vector<int>>& cellsInNet, string file, float margin, vector<DataHPWL>& HPWLArch);
bool compareCost(tuple<float, int> t1, tuple<float, int> t2);
void runAlgorithm_try(vector<tuple<int, float>>& dataHPWL, vector<vector<int>>& cellsInNet, vector<string>& netName,
    vector<vector<float>>& cellInfo, float siteX, float siteY, vector<vector<int>>& blockCellMap,
    vector<bool>& validCell, vector<vector<int>>& netsInCell, string logCalcCost, float marginA,
    float marginB, float maxDisp, vector<DataHPWL>& HPWLArch, int netIter,
    vector<vector<int>>& blockAreaMap, int numOfRow, int numOfCol);
void updateBlockCell(int cellId, vector<vector<float>>& cellInfo, vector<vector<int>>& blockCellMap, int siteX, int siteY);
bool checkOverlap(vector<vector<float>>& cellInfo, float siteX, float siteY, float blockX, float blockY);
// 11.02 추가 function
/*
    func 1. genHPWLArch
    --> HPWL, xmin, xminSub, ymin, yminSub, xmax, xmaxSub, ymax, ymaxSub
    --> gen Archive for function 2. 3.
    func 2. readHPWL(net)
    --> get HPWL from net w/o calculation
    func 3. readModifiedHPWL(net, delCell, addCell)
    --> get HPWL from small change.
*/
map<int, bool> genBoolMap(queue<int> queue);
bool moreImprove(map<int, bool>& isMoved);
vector<DataHPWL> genHPWLArch(vector<vector<int>>& cellsInNet, vector<vector<float>>& cellInfo);
float readHPWL(int net, vector<DataHPWL>& HPWLArch);
float readModifiedHPWL(int net, vector<DataHPWL>& HPWLArch, int delCell, int addCell, vector<vector<float>>& cellInfo, vector<vector<int>>& cellsInNet);
// old functions. <- 지금 안씀.
vector<vector<string>> readFile(string fileName);
void checkEncrytion(vector<vector<string>> dataList, string dataListName);

class Node {
public:
    int net;
    float HPWL;
};

class MaxHeap {
private:
    int heapSize;
    vector<Node> data;
    map<int, int> netMap;
    vector<vector<int>> cellsInNet;
    vector<vector<float>> cellInfo;
public:
    MaxHeap(vector<vector<int>>& cellsInNet, vector<vector<float>>& cellInfo);
    void buildMaxHeap();
    void maxHeapify(int idx);
    void swapNode(int idx, int largest);
    void display();
    void updateNetMap(); // netMap[net] = idx.  // net 의 현재 heap 에서의 위치(idx) 찾는다.   
    void decreaseKey(int net); // net 을 주었을 때 key 를 decrease 한다.
    void maxHeapifyDecrease(int idx);
    Node popData();
};
void writeOutput(string resFileName, vector<vector<float>>& cellInfo, vector<string>& cellName);
