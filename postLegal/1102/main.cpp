#include "functions.h"

// 1. main path 정하기
string mainPath = "C:/Users/김화평/Desktop/ispd_2015_benchMark/mgc_fft_1/res/";
//string mainPath = "C:/Users/김화평/Desktop/ispd_2015_benchMark/mgc_fft_2/res/";
//string mainPath = "C:/Users/김화평/Desktop/ispd_2015_benchMark/mgc_des_perf_1/res/";

// 2. output path
string placeFile = mainPath + "place.txt";
string netCellFile = mainPath + "net_cell_match.txt";
string cellNetFile = mainPath + "cell_net_match.txt";

string netRpt = "netReport.txt";
string cellRpt = "cellReport.txt";
string logCalcCost = "cost_calculate.txt";

// 3. device 결정
/* mgc_fft_1*/

float blockX = 265, siteX = 0.2;
float blockY = 265, siteY = 2;
float maxDisp = 30;

/* mgc_fft_2*/
/*
float blockX = 342, siteX = 0.2;
float blockY = 342, siteY = 2;
float maxDisp = 50;
*/
/* mgc_des_perf_1*/
/*
float blockX = 445, siteX = 0.2;
float blockY = 445, siteY = 2;
float maxDisp = 30;
*/
int main()
{
    clock_t start, finish;
    // 1. pre-processing.
    vector<string> cellName = genNameMap(placeFile);
    vector<string> netName = genNameMap(netCellFile);
    vector<vector<float>> cellInfo = genCellInfoMap(placeFile);
    vector<vector<int>> cellsInNet = genNetInfoMap(netCellFile);
    vector<vector<int>> netsInCell = genCellNetInfoMap(cellNetFile);
    vector<tuple<int, float>> dataHPWL = genDataHPWL(cellsInNet, cellInfo);
    
    vector<bool> validCell = validCellCheck(cellsInNet, netsInCell);

    vector<vector<int>> blockCellMap = genBlockMap(blockX, blockY, siteX, siteY);
    // vector<vector<int>> blockAreaMap = genBlockMap(blockX, blockY, siteX, siteY);
    modifyBlockCellMap(blockCellMap, cellInfo, siteX, siteY);
    // modifyBlockAreaMap(blockAreaMap, cellInfo, siteX, siteY);

    int numOfCell = cellName.size();
    int numOfNet = netName.size();

    if (checkOverlap(cellInfo, siteX, siteY, blockX, blockY) == false) return -1;
    //cout << blockCellMap.size() << " -- " << blockCellMap[0].size() << endl;
    cout << "cell 개수는 " << numOfCell << " 이고, net 개수는 " << numOfNet << " 이다. " << endl;
    cout << "avg displacement = " << getAvgDisplace(cellInfo) << endl;
    cout << "avg HPWL = " << getAvgHPWL(cellsInNet, cellInfo) << endl;
    netReport(cellsInNet, cellInfo, netName, netRpt);
    cellReport(cellInfo, cellName, cellRpt);
    cout << " 첫번째 step 끝." << endl;

    // 2. algorithm start.
    float marginA = 1.1; // getWindowCell
    float marginB = 1.2; // calculateCost
    start = clock();
    runAlgorithm(dataHPWL, cellsInNet, netName, cellInfo, siteX, siteY, blockCellMap, validCell, netsInCell, logCalcCost, marginA, marginB, maxDisp);
    finish = clock();

    double duration = (double)(finish - start) / CLOCKS_PER_SEC;
    cout << duration << "초" << endl;

    checkOverlap(cellInfo, siteX, siteY, blockX, blockY);
}
