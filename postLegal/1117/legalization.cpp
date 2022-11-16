#include "functions.h"

// 1. main path 정하기
string mainPath = "C:\/Users\/김화평\/Desktop\/workSpace\/ispd_2015_benchMarks\/mgc_fft_2\/res\/";
float blockX = 342, siteX = 0.2; float blockY = 342, siteY = 2; float maxDisp = 500;
float marginA = 2; // getWindowCell
float marginB = 1.2; // calculateCost - distance 최대값을 얼마까지 감수할 것인지?
int netIter = 5;

/*
string mainPath = "C:\/Users\/김화평\/Desktop\/workSpace\/ispd_2015_benchMarks\/mgc_des_perf_1\/res\/";
float blockX = 445, siteX = 0.2; float blockY = 445, siteY = 2; float maxDisp = 50;

string mainPath = "C:\/Users\/김화평\/Desktop\/workSpace\/ispd_2015_benchMarks\/mgc_matrix_mult_1\/res\/";
float blockX = 800, siteX = 0.2; float blockY = 800, siteY = 2; float maxDisp = 500;

string mainPath = "C:\/Users\/김화평\/Desktop\/workSpace\/ispd_2015_benchMarks\/mgc_des_perf_1\/res\/";
float blockX = 445, siteX = 0.2; float blockY = 445, siteY = 2; float maxDisp = 50;

string mainPath = "C:\/Users\/김화평\/Desktop\/workSpace\/ispd_2015_benchMarks\/mgc_fft_1\/res\/";
float blockX = 265, siteX = 0.2; float blockY = 265, siteY = 2; float maxDisp = 100;

string mainPath = "C:\/Users\/김화평\/Desktop\/workSpace\/ispd_2015_benchMarks\/mgc_edit_dist_a\/res\/";
float blockX = 800, siteX = 0.2; float blockY = 800, siteY = 2; float maxDisp = 50;

string mainPath = "C:\/Users\/김화평\/Desktop\/workSpace\/ispd_2015_benchMarks\/mgc_des_perf_a\/res\/";
float blockX = 900, siteX = 0.2; float blockY = 900, siteY = 2; float maxDisp = 50;

string mainPath = "C:\/Users\/김화평\/Desktop\/workSpace\/ispd_2015_benchMarks\/mgc_fft_a\/res\/";
float blockX = 800, siteX = 0.2; float blockY = 800, siteY = 2; float maxDisp = 50;

string mainPath = "C:\/Users\/김화평\/Desktop\/workSpace\/ispd_2015_benchMarks\/mgc_fft_2\/res\/";
float blockX = 342, siteX = 0.2; float blockY = 342, siteY = 2; float maxDisp = 500;

string mainPath = "C:/Users/김화평/Desktop/ispd_2015_benchMark/mgc_fft_b/res/";
float blockX = 800, siteX = 0.2; float blockY = 800, siteY = 2; float maxDisp = 500;

string mainPath = "C:/Users/김화평/Desktop/ispd_2015_benchMark/mgc_fft_2/res/";
float blockX = 342, siteX = 0.2; float blockY = 342, siteY = 2; float maxDisp = 500;

string mainPath = "C:/Users/김화평/Desktop/ispd_2015_benchMark/mgc_des_perf_1/res/";
float blockX = 445, siteX = 0.2; float blockY = 445, siteY = 2; float maxDisp = 50;

string mainPath = "C:/Users/김화평/Desktop/ispd_2015_benchMark/mgc_des_perf_b/res/";
float blockX = 600, siteX = 0.2; float blockY = 600, siteY = 2; float maxDisp = 50;

string mainPath = "C:/Users/김화평/Desktop/ispd_2015_benchMark/mgc_matrix_mult_1/res/";
float blockX = 800, siteX = 0.2; float blockY = 800, siteY = 2; float maxDisp = 50;
*/

// 2. output path
string placeFile = mainPath + "place.txt";
string netCellFile = mainPath + "net_cell_match.txt";
string cellNetFile = mainPath + "cell_net_match.txt";

string netRpt = "netReport.txt";
string cellRpt = "cellReport.txt";
string logCalcCost = "cost_calculate.txt";


int main()
{
    clock_t start, finish;
    // 1. pre-processing.
    // 1) cell 이름, net 이름 정의
    vector<string> cellName = genNameMap(placeFile);
    vector<string> netName = genNameMap(netCellFile);
    int numOfRow = floor(blockY / siteY);
    int numOfCol = floor(blockX / siteX);
    // 2) cell 정보, net에 연결된 cell 정보, cell에 연결된 net 정보 
    vector<vector<float>> cellInfo = genCellInfoMap(placeFile);
    vector<vector<int>> cellsInNet = genNetInfoMap(netCellFile);
    vector<vector<int>> netsInCell = genCellNetInfoMap(cellNetFile);
    
    // 3) HPWL 계산. 
    vector<tuple<int, float>> dataHPWL = genDataHPWL(cellsInNet, cellInfo);
    vector<DataHPWL> HPWLArch = genHPWLArch(cellsInNet, cellInfo);

    vector<bool> validCell = validCellCheck(cellsInNet, netsInCell);

    vector<vector<int>> blockCellMap = genBlockMap(blockX, blockY, siteX, siteY);
    modifyBlockCellMap(blockCellMap, cellInfo, siteX, siteY);

    vector<vector<int>> blockAreaMap = genBlockMap(blockX, blockY, siteX, siteY);
    modifyBlockAreaMap(blockAreaMap, cellInfo, siteX, siteY);

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

    // 2. algorithm start
    //netIter = dataHPWL.size();

    start = clock();
    //runAlgorithm(dataHPWL, cellsInNet, netName, cellInfo, siteX, siteY, blockCellMap, validCell, netsInCell, logCalcCost, marginA, marginB, maxDisp, HPWLArch, netIter);
    runAlgorithm_try(dataHPWL, cellsInNet, netName, cellInfo, siteX, siteY, blockCellMap, validCell, netsInCell, 
        logCalcCost, marginA, marginB, maxDisp, HPWLArch, netIter, blockAreaMap, numOfRow, numOfCol);
    finish = clock();

    double duration = (double)(finish - start) / CLOCKS_PER_SEC;
    cout << duration << "초" << endl;
    checkOverlap(cellInfo, siteX, siteY, blockX, blockY);
}
