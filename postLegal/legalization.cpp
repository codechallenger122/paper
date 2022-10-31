#include "functions.h"

string mainPath = "C:/Users/김화평/Desktop/ispd_2015_benchMark/mgc_fft_1/res/";
string placeFile = mainPath + "place.txt";
string netCellFile = mainPath + "net_cell_match.txt";
string cellNetFile = mainPath + "cell_net_match.txt";

string netRpt = "netReport.txt";
string cellRpt = "cellReport.txt";
string logCalcCost = "cost_calculate.txt";

float blockX = 265, siteX = 0.2;
float blockY = 265, siteY = 2;
int main()
{
    // 1. pre-processing.
    vector<string> cellName = genNameMap(placeFile);
    vector<string> netName = genNameMap(netCellFile);
    vector<vector<float>> cellInfo = genCellInfoMap(placeFile);
    vector<vector<int>> cellsInNet = genNetInfoMap(netCellFile);
    vector<vector<int>> netsInCell = genCellNetInfoMap(cellNetFile);
    vector<tuple<int, float>> dataHPWL = genDataHPWL(cellsInNet, cellInfo);
    
    vector<vector<int>> blockCellMap = genBlockMap(blockX, blockY, siteX, siteY);
    vector<vector<int>> blockAreaMap = genBlockMap(blockX, blockY, siteX, siteY);
    modifyBlockCellMap(blockCellMap, cellInfo, siteX, siteY);
    modifyBlockAreaMap(blockAreaMap, cellInfo, siteX, siteY);

    int numOfCell = cellName.size();
    int numOfNet = netName.size();

    cout << blockCellMap.size() << " -- " << blockCellMap[0].size() << endl;
    cout << "cell 개수는 " << numOfCell << " 이고, net 개수는 " << numOfNet << " 이다. " << endl;
    cout << "avg displacement = " << getAvgDisplace(cellInfo) << endl;
    cout << "avg HPWL = " << getAvgHPWL(cellsInNet, cellInfo) << endl;
    netReport(cellsInNet, cellInfo, netName, netRpt);
    cellReport(cellInfo, cellName, cellRpt);
    cout << " 첫번째 step 끝." << endl;

    // 2. algorithm start.
    float marginA = 1.2;
    float marginB = 1.2;
    //for (auto i = 0; i < dataHPWL.size(); i++) {
    for (auto i = 0; i < 30; i++) {
        int nId = get<0>(dataHPWL[i]);
        float HPWL = get<1>(dataHPWL[i]);
        cout << "net : " << nId << " - " << i << "th, " << netName[nId] << " is processing." << endl;
        if (cellsInNet[nId].size() > 50) continue;
        vector<int> windowHPWL = getWindowHPWL(nId, cellsInNet, cellInfo, siteX, siteY); // xmin, xmax, ymin, ymax <-- int 단위로.

        queue<int> queue = genCellQueue(cellsInNet, nId, cellInfo);
        while (!queue.empty()) {
            int cId = queue.front();
            queue.pop();
            vector<tuple<int, int>> windowCell = getWindowCell(windowHPWL, cId, cellInfo, siteX, siteY, marginA, blockCellMap);
            if (windowCell.size() == 0) continue;
            vector<int> candidateCells = getCandidateCell(windowCell, blockCellMap, cId, cellInfo);
            
            vector<tuple<float, int>> cost; // float = cost, int = candidateCells[i]
            cout << "candidate cell 개수 = " << candidateCells.size() << endl;
            for (int i = 0; i < candidateCells.size(); i++) {
                int scId = candidateCells[i]; // swap cell Id
                tuple<float, int> swapCost = calculateSwapCost(nId, cId, scId, cellInfo, netsInCell, cellsInNet, logCalcCost, marginB);
                //cout << i << " 번째 candidate cell," << cellName[scId] << "cost 계산 완료" << endl;
                if (get<0>(swapCost) == 10000) {
                    continue;
                }
                else {
                    cost.push_back(swapCost);
                }    
            }
            if (cost.empty()) continue;
            else {
                sort(cost.begin(), cost.end(), compareCost);
                // swap operation & update & queue 에 다시 집어 넣기.
                
                int scId_picked = get<1>(cost[0]);
                cout << "\n###" << cId << " --> " << scId_picked << " swapping " << endl;
                float xLeg_cId = cellInfo[cId][0], yLeg_cId = cellInfo[cId][1], xLeg_scId = cellInfo[scId_picked][0], yLeg_scId = cellInfo[scId_picked][1];
                cellInfo[cId][0] = xLeg_scId;
                cellInfo[cId][1] = yLeg_scId;
                cellInfo[scId_picked][0] = xLeg_cId;
                cellInfo[scId_picked][1] = yLeg_cId;

                //queue.push(scId_picked);
            }
        }     
        /*
        바깥에 위치한 cell 부터, cell 의 Global placement position 으로부터 
        (현재 displacement + alpha 범위 만큼의 region) 교집합 (HPWL region) 을 search 하면서,/
        같은 크기의 cell 을 찾아서, swap 시 cost 를 계산한다.
        이 중 가장 cost 가 작은(gain이 큰) cell 과 swap 하고 update.
        
        (모든 cell 에 대해서 적용. --> 취소.) ( xmin, xmax, ymin, ymax 에 기여한 cell 에 대해서 먼저 적용)
        Queue 에 처음에 c1, c2, c3, ... 를 바깥에 위치한 순서로 넣어 놓고 위의 function 을 진행.
        뽑았을 때, swap & update 를 진행 했다면 다시 queue 에 집어넣음.
        뽑았을 때, swap & update 를 진행 하지 않았다면, 그대로 끝.

        Queue 가 비면 stop !!
        */
    }
    cout << "after procedure, avg displacement = " << getAvgDisplace(cellInfo) << endl;
    cout << "after procedure, avg HPWL = " << getAvgHPWL(cellsInNet, cellInfo) << endl;
}
