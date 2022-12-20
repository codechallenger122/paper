/*
  1. 변경 사항. queue.empty() 에서 moreImprove(isMoved) 로 변경.
  --> 즉 runAlgorithm 에서 queue 가 모두 F 인 경우에 한 net 에 대한 procedure 를 종료
*/
#include "functions.h"
vector<vector<int>> genBlockMap(float blockX, float blockY, float siteX, float siteY) {
    int numOfRow = floor(blockY / siteY);
    int numOfCol = floor(blockX / siteX);
    vector<vector<int>> blockMap(numOfCol, vector<int>(numOfRow, -1));
    return blockMap;
}
void modifyBlockCellMap(vector<vector<int>>& blockCellMap, vector<vector<float>>& cellInfo, float siteX, float siteY) {
    for (int cId = 0; cId < cellInfo.size(); cId++) {
        float xLeg = cellInfo[cId][0];
        float yLeg = cellInfo[cId][1];
        float xSize = cellInfo[cId][4];
        float ySize = cellInfo[cId][5];

        int xGrid = ceil(xLeg / siteX);
        int yGrid = ceil(yLeg / siteY);
        blockCellMap[xGrid][yGrid] = cId;
    }
}
void modifyBlockAreaMap(vector<vector<int>>& blockAreaMap, vector<vector<float>>& cellInfo, float siteX, float siteY) {
    for (int cId = 0; cId < cellInfo.size(); cId++) {
        float xLeg = cellInfo[cId][0];
        float yLeg = cellInfo[cId][1];
        float xSize = cellInfo[cId][4];
        float ySize = cellInfo[cId][5];

        int xGrid = ceil(xLeg / siteX);
        int yGrid = ceil(yLeg / siteY);
        int xGridEnd = xGrid + ceil(xSize / siteX);
        int yGridEnd = yGrid + ceil(ySize / siteY);
        for (int i = xGrid; i < xGridEnd; i++) {
            for (int j = yGrid; j < yGridEnd; j++) {
                blockAreaMap[i][j] = cId;
            }
        }
    }
}
vector<string> parseString(string str, string del) {
    //string str = "This_is,the,,C/C++ world";
    //string del = "/, _";
    vector<string> output;
    for (auto start = str.begin(), stop = start; stop != str.end(); )
    {
        stop = find_first_of(start, str.end(), del.begin(), del.end());
        output.push_back(string(start, stop));
        if (stop != str.end())
            start = stop + 1;
    }
    return output;
}
vector<string> genNameMap(string fileName) {
    string str;
    ifstream file(fileName);
    vector<string> nameList;
    int idx = 0;
    while (getline(file, str)) {
        vector<string> tmpdata = parseString(str, ":");
        string name = tmpdata[1];
        nameList.push_back(name);
        if (to_string(idx) != tmpdata[0]) {
            std::cout << fileName << " encrytion failed !" << endl;
            std::cout << "idx = " << idx << ", tmpdata[0] = " << tmpdata[0] << endl;
            exit(EXIT_FAILURE);
        }
        idx += 1;
    }
    return nameList;
}
vector<vector<float>> genCellInfoMap(string fileName) {
    string str;
    ifstream file(fileName);
    vector<vector<float>> cellInfoList;
    while (getline(file, str)) {
        vector<string> dataInfo = parseString(str, ":");
        vector<float> cellInfo;
        for (int i = 2; i < dataInfo.size(); i++) {
            cellInfo.push_back(floorf(100 * stof(dataInfo[i])) / 100);
        }
        std::cout << endl;
        cellInfoList.push_back(cellInfo);
    }
    return cellInfoList;
}
vector<vector<int>> genNetInfoMap(string fileName) {
    string str;
    ifstream file(fileName);
    vector<vector<int>> netInfoList;
    while (getline(file, str)) {
        vector<string> dataInfo = parseString(str, ":");
        vector<int> netInfo;
        for (int i = 2; i < dataInfo.size(); i++) {
            netInfo.push_back(stoi(dataInfo[i]));
        }
        netInfoList.push_back(netInfo);
    }
    return netInfoList;
}
vector<vector<int>> genCellNetInfoMap(string fileName) {
    string str;
    ifstream file(fileName);
    vector<vector<int>> cellInfoList;
    while (getline(file, str)) {
        vector<string> dataInfo = parseString(str, ":");
        vector<int> cellInfo;
        for (int i = 2; i < dataInfo.size(); i++) {
            cellInfo.push_back(stoi(dataInfo[i]));
        }
        cellInfoList.push_back(cellInfo);
    }
    return cellInfoList;
}

float getAvgDisplace(vector<vector<float>>& cellInfo) {
    float result = 0;
    for (int i = 0; i < cellInfo.size(); i++) {
        result += getDisplace(i, cellInfo);
    }
    return result / float(cellInfo.size());
}
float getHPWL(int net, vector<vector<int>>& cellsInNet, vector<vector<float>>& cellInfo) {
    /*
    cellInfo   파일 포맷<float> : xLeg[0] : yLeg[1] : xGlob[2] : yGlob[3] : xSize[4] : ySize[5]
    cellsInNet 파일 포맷<int> : cId[0] : cId[1] : cId[2] ... */
    vector<int> cells = cellsInNet[net];
    float xMin = 100000, yMin = 100000, xMax = -1, yMax = -1;
    for (auto i = 0; i < cells.size(); i++) {
        vector<float> info = cellInfo[cells[i]];
        float xLL = info[0], yLL = info[1], xUR = xLL + info[4], yUR = yLL + info[5];
        //cout << xLL << " " << yLL << " " << xUR << " " << yUR << endl;
        if (xLL < xMin) xMin = xLL;
        if (yLL < yMin) yMin = yLL;
        if (xUR > xMax) xMax = xUR;
        if (yUR > yMax) yMax = yUR;
    }
    float HPWL = xMax - xMin + yMax - yMin;
    //cout << "net : " << net << "(" << xMax << " - " << xMin << ") + (" << yMax << " - " << yMin << ") = " << HPWL << endl;
    return HPWL;
}
bool compareHPWL(const tuple<int, float>& t1, const tuple<int, float>& t2) {
    return get<1>(t1) > get<1>(t2);
}
vector<tuple<int, float>> genDataHPWL(vector<vector<int>>& cellsInNet, vector<vector<float>>& cellInfo) {
    int numOfNet = cellsInNet.size();
    vector<tuple<int, float>> dataHPWL;
    tuple<int, float> netHPWL;
    for (int nId = 0; nId < numOfNet; nId++) {
        get<0>(netHPWL) = nId;
        get<1>(netHPWL) = getHPWL(nId, cellsInNet, cellInfo);
        dataHPWL.push_back(netHPWL);
    }
    sort(dataHPWL.begin(), dataHPWL.end(), compareHPWL);
    return dataHPWL;
}
float getAvgHPWL(vector<vector<int>>& cellsInNet, vector<vector<float>>& cellInfo) {
    float result = 0;
    for (int net = 0; net < cellsInNet.size(); net++) {
        result += getHPWL(net, cellsInNet, cellInfo);
    }
    return result / float(cellsInNet.size());
}
bool compareNet(const tuple<string, float, float, int>& t1, const tuple<string, float, float, int>& t2) {
    return get<1>(t1) < get<1>(t2);
}
bool compareCell(const tuple<string, float>& t1, const tuple<string, float>& t2) {
    return get<1>(t1) < get<1>(t2);
}
void netReport(vector<vector<int>>& cellsInNet, vector<vector<float>>& cellInfo, vector<string>& netName, string outFileName) {
    vector<tuple<string, float, float, int>> infoList; // <net, HPWL, 소속 cell 의 displacement, numOfcell>
    int numOfTarget = 0;
    for (int nId = 0; nId < cellsInNet.size(); nId++) {
        string net = netName[nId];
        float HPWL = getHPWL(nId, cellsInNet, cellInfo);
        int numOfCell = cellsInNet[nId].size();
        float disp = 0;
        for (int i = 0; i < numOfCell; i++) {
            disp += getDisplace(cellsInNet[nId][i], cellInfo);
        }
        float avgDisp = disp / float(numOfCell);
        infoList.push_back(make_tuple(net, HPWL, avgDisp, numOfCell));

        if (avgDisp > 5 && HPWL > 50) numOfTarget++;
    }
    std::cout << "average distance 가 5 이상이고, HPWL 이 50 이상인 애들이 " << numOfTarget << " 개 이다." << endl;
    sort(infoList.begin(), infoList.end(), compareNet);
    ofstream file(outFileName);
    for (int i = 0; i < cellsInNet.size(); i++) {
        file << get<0>(infoList[i]) << ":" << get<1>(infoList[i]) << ":" << get<2>(infoList[i]) << ":" << get<3>(infoList[i]) << endl;
    }
    file.close();
}
void cellReport(vector<vector<float>>& cellInfo, vector<string>& cellName, string outFileName) {
    vector<tuple<string, float>> infoList; // <cell, displacement>
    for (int cId = 0; cId < cellInfo.size(); cId++) {
        string cell = cellName[cId];
        float displace = getDisplace(cId, cellInfo);
        infoList.push_back(make_tuple(cell, displace));
    }
    sort(infoList.begin(), infoList.end(), compareCell);
    ofstream file(outFileName);
    for (int i = 0; i < cellInfo.size(); i++) {
        file << get<0>(infoList[i]) << ":" << get<1>(infoList[i]) << endl;
    }
    file.close();
}
void netAdjustment(vector<vector<float>>& cellInfo, vector<vector<int>>& cellsInNet, vector<vector<int>>& netsInCell, vector<float>& dataHPWL) {

}
queue<int> genCellQueue(vector<vector<int>>& cellsInNet, int nId, vector<vector<float>>& cellInfo) {
    vector<int> cells = cellsInNet[nId];
    queue<int> cellQueue;
    vector<int> tmp;

    float xMin = 100000, yMin = 100000, xMax = -1, yMax = -1;
    for (auto i = 0; i < cells.size(); i++) {
        vector<float> info = cellInfo[cells[i]];
        float xLL = info[0], yLL = info[1], xUR = xLL + info[4], yUR = yLL + info[5];
        //cout << xLL << " " << yLL << " " << xUR << " " << yUR << endl;
        if (xLL < xMin) xMin = xLL;
        if (yLL < yMin) yMin = yLL;
        if (xUR > xMax) xMax = xUR;
        if (yUR > yMax) yMax = yUR;
    }

    for (int i = 0; i < cells.size(); i++) {
        vector<float> info = cellInfo[cells[i]];
        float xLL = info[0], yLL = info[1], xUR = xLL + info[4], yUR = yLL + info[5];
        if (xLL == xMin || yLL == yMin || xUR == xMax || yUR == yMax) {
            cellQueue.push(cells[i]);
        }
        else {
            tmp.push_back(cells[i]);
        }
    }

    for (int i = 0; i < tmp.size(); i++) {
        cellQueue.push(tmp[i]);
    }
    return cellQueue;
}
vector<int> getWindowHPWL(int nId, vector<vector<int>>& cellsInNet, vector<vector<float>>& cellInfo, float siteX, float siteY) {
    vector<int> data; // xmin, xmax, ymin, ymax <-- int 단위로.
    vector<int> cells = cellsInNet[nId];
    float xMin = 100000, yMin = 100000, xMax = -1, yMax = -1;
    for (auto i = 0; i < cells.size(); i++) {
        vector<float> info = cellInfo[cells[i]];
        float xLL = info[0], yLL = info[1], xUR = xLL + info[4], yUR = yLL + info[5];
        //cout << xLL << " " << yLL << " " << xUR << " " << yUR << endl;
        if (xLL < xMin) xMin = xLL;
        if (yLL < yMin) yMin = yLL;
        if (xUR > xMax) xMax = xUR;
        if (yUR > yMax) yMax = yUR;
    }
    int xImin = xMin / siteX, yImin = yMin / siteY, xImax = xMax / siteX, yImax = yMax / siteY;
    data.push_back(xImin); data.push_back(xImax); data.push_back(yImin); data.push_back(yImax);
    return data;
}
vector<tuple<int, int>> getWindowCell(vector<int>& windowHPWL, int cId, vector<vector<float>>& cellInfo, float siteX, float siteY, float margin, vector<vector<int>>& blockCellMap, float maxDisp) {
    vector<tuple<int, int>> windowOut;
    int xLimit = blockCellMap.size(), yLimit = blockCellMap[0].size();
    int xImin = windowHPWL[0], xImax = windowHPWL[1], yImin = windowHPWL[2], yImax = windowHPWL[3];
    float xLeg = cellInfo[cId][0], yLeg = cellInfo[cId][1], xGlob = cellInfo[cId][2], yGlob = cellInfo[cId][3];
    float displacement = (abs(xGlob - xLeg) + abs(yGlob - yLeg)) * margin;
    //cout << "displacement is " << displacement << endl;
    if (displacement > maxDisp) displacement = maxDisp;
    int xStart = (xGlob - displacement) / siteX, yStart = (yGlob - displacement) / siteY;
    int xEndTmp = (xGlob + displacement) / siteX, yEndTmp = (yGlob + displacement) / siteY;
    int xEnd = xEndTmp + 1, yEnd = yEndTmp + 1;
    for (int i = xStart; i <= xEnd; i++) {
        for (int j = yStart; j <= yEnd; j++) {
            if (xImin <= i && i <= xImax && yImin <= j && j <= yImax && i < xLimit && j < yLimit) {
                int dist = abs(i * siteX - xGlob) + abs(j * siteY - yGlob);
                if (dist <= displacement) windowOut.push_back(make_tuple(i, j));
            }
        }
    }
    return windowOut;
}
;
vector<int> getCandidateCell(vector<tuple<int, int>>& windowCell, vector<vector<int>>& blockCellMap, int cId, vector<vector<float>>& cellInfo, vector<bool> validCell) {
    // windowCell = (i, i), (i, i), ..

    vector<int> candidateCell;
    float xSize = cellInfo[cId][4], ySize = cellInfo[cId][5];
    for (int i = 0; i < windowCell.size(); i++) {
        int x = get<0>(windowCell[i]), y = get<1>(windowCell[i]);
        int blockCell = blockCellMap[x][y];

        if (find(candidateCell.begin(), candidateCell.end(), blockCell) != candidateCell.end()) continue;

        if (blockCell == -1 || blockCell == cId) {
            continue;
        }
        // valid 하지 않으면 패스.. <-- 이미 fix 된 경우 제외
        else if (validCell[blockCell] == false) {
            continue;
        }
        else {

            float xSizeC = cellInfo[blockCell][4], ySizeC = cellInfo[blockCell][5];
            if (xSize == xSizeC && ySize == ySizeC) {
                candidateCell.push_back(blockCellMap[x][y]);
            }

        }
    }
    return candidateCell;
}
vector<int> getCandidateCell_try(vector<tuple<int, int>>& windowCell, vector<vector<int>>& blockCellMap, int cId, vector<vector<float>>& cellInfo, vector<bool> validCell,
    float siteX, float siteY, vector<vector<int>>& blockAreaMap, int numOfRow, int numOfCol) {

    // windowCell = (i, i), (i, i), ...
    float xLegC = cellInfo[cId][0];
    float yLegC = cellInfo[cId][1];
    float xSizeC = cellInfo[cId][4];
    float ySizeC = cellInfo[cId][5];

    int xGridC = ceil(xLegC / siteX);
    int yGridC = ceil(yLegC / siteY);

    vector<int> candidateCell;

    for (int i = 0; i < windowCell.size(); i++) {
        int x = get<0>(windowCell[i]), y = get<1>(windowCell[i]);
        int blockCell = blockCellMap[x][y];

        if (find(candidateCell.begin(), candidateCell.end(), blockCell) != candidateCell.end()) continue;

        if (blockCell == -1 || blockCell == cId) {
            continue;
        }
        // valid 하지 않으면 패스.. <-- 이미 fix 된 경우 제외
        else if (validCell[blockCell] == false) {
            continue;
        }
        else {
            float xLegS = cellInfo[blockCell][0]; float yLegS = cellInfo[blockCell][1];
            float xSizeS = cellInfo[blockCell][4], ySizeS = cellInfo[blockCell][5];

            int xGridS = ceil(xLegS / siteX);
            int yGridS = ceil(yLegS / siteY);

            int xGridEndCS = xGridC + ceil(xSizeS / siteX);
            int yGridEndCS = yGridC + ceil(ySizeS / siteY);
            int xGridEndSC = xGridS + ceil(xSizeC / siteX);
            int yGridEndSC = yGridS + ceil(ySizeC / siteY);

            int xGridEndC = xGridC + ceil(xSizeC / siteX);
            int yGridEndC = yGridC + ceil(ySizeC / siteY);
            int xGridEndS = xGridS + ceil(xSizeS / siteX);
            int yGridEndS = yGridS + ceil(ySizeS / siteY);


            if (xSizeC == xSizeS && ySizeC == ySizeS) {
                candidateCell.push_back(blockCell);
            }
            else {
                bool flag = true;

                //cout << xGridC << ", " << xGridS << ", " << yGridC << ", " << yGridS << endl;
                //cout << xGridEndCS << ", " << yGridEndCS << ", " << xGridEndSC << ", " << yGridEndSC << endl;
                if (xGridEndCS > numOfCol) flag = false;
                if (yGridEndCS > numOfRow) flag = false;
                if (xGridEndSC > numOfCol) flag = false;
                if (yGridEndSC > numOfRow) flag = false;
                if (flag == true) {
                    vector<tuple<int, int>> freeSpaceC;
                    vector<tuple<int, int>> freeSpaceS;
                    for (int i = xGridC; i < xGridEndCS; i++) {
                        for (int j = yGridC; j < yGridEndCS; j++) {
                            //if (blockAreaMap[i][j] == cId || blockAreaMap[i][j] == -1) continue;
                            //else flag = false;
                            if (blockAreaMap[i][j] == cId) continue;
                            else if (blockAreaMap[i][j] == -1) {
                                freeSpaceC.push_back(make_tuple(i, j));
                            }
                            else flag = false;
                        }
                    }
                    for (int i = xGridS; i < xGridEndSC; i++) {
                        for (int j = yGridS; j < yGridEndSC; j++) {
                            //if (blockAreaMap[i][j] == blockCell || blockAreaMap[i][j] == -1) continue;
                            //else flag = false;
                            if (blockAreaMap[i][j] == cId) continue;
                            else if (blockAreaMap[i][j] == -1) {
                                freeSpaceS.push_back(make_tuple(i, j));
                            }
                            else flag = false;
                        }
                    }
                    for (auto pairC : freeSpaceC) {
                        for (auto pairS : freeSpaceS) {
                            if (get<0>(pairC) == get<0>(pairS) && get<1>(pairC) == get<1>(pairS))
                                flag = false;
                        }
                    }
                    if (flag) {
                        candidateCell.push_back(blockCell);

                    }
                }
            }
        }

    }
    return candidateCell;
}
float getDisplace(int cell, vector<vector<float>>& cellInfo) {
    vector<float> info = cellInfo[cell];
    float xLeg = info[0], yLeg = info[1], xGlob = info[2], yGlob = info[3];
    float displace = abs(xGlob - xLeg) + abs(yGlob - yLeg);
    //cout << xLeg << ", " << xGlob << ", " << yLeg << ", " << yGlob << endl;
    //cout << displace << endl;
    return displace;
}
float getDisplaceWithNewLeg(int cell, vector<vector<float>>& cellInfo, float xLeg, float yLeg) {
    vector<float> info = cellInfo[cell];
    float xGlob = info[2], yGlob = info[3];
    float displace = abs(xGlob - xLeg) + abs(yGlob - yLeg);
    //cout << xLeg << ", " << xGlob << ", " << yLeg << ", " << yGlob << endl;
    //cout << displace << endl;
    return displace;
}
float getHPWLWithNewLeg(int net, vector<vector<int>>& cellsInNet, vector<vector<float>>& cellInfo, int cId, int scId) {
    vector<float> info_cId = cellInfo[cId];
    vector<float> info_scId = cellInfo[scId];

    vector<int> cells = cellsInNet[net];
    float xMin = 100000, yMin = 100000, xMax = -1, yMax = -1;
    for (auto i = 0; i < cells.size(); i++) {
        vector<float> info;
        if (cells[i] == cId) {
            info = info_scId;
        }
        else if (cells[i] == scId) {
            info = info_cId;
        }
        else {
            info = cellInfo[cells[i]];
        }

        float xLL = info[0], yLL = info[1], xUR = xLL + info[4], yUR = yLL + info[5];
        //cout << xLL << " " << yLL << " " << xUR << " " << yUR << endl;
        if (xLL < xMin) xMin = xLL;
        if (yLL < yMin) yMin = yLL;
        if (xUR > xMax) xMax = xUR;
        if (yUR > yMax) yMax = yUR;
    }
    float HPWL = xMax - xMin + yMax - yMin;
    //cout << "net : " << net << "(" << xMax << " - " << xMin << ") + (" << yMax << " - " << yMin << ") = " << HPWL << endl;
    return HPWL;
}

tuple<float, int> calculateSwapCost(int nId, int cId, int scId, vector<vector<float>>& cellInfo, vector<vector<int>>& netsInCell,
    vector<vector<int>>& cellsInNet, string file, float margin, vector<DataHPWL>& HPWLArch) {
    ofstream fout(file);
    //cout << "\n  >>>  net : " << nId << ", change cell" << cId << " with " << scId << ".\n";
    float cost = 0;
    // 1. delta-displace 계산.
    float xLeg_cId = cellInfo[cId][0], yLeg_cId = cellInfo[cId][1], xLeg_scId = cellInfo[scId][0], yLeg_scId = cellInfo[scId][1];
    float displace_cId_before = getDisplace(cId, cellInfo);
    float displace_scId_before = getDisplace(scId, cellInfo);
    float displace_cId_after = getDisplaceWithNewLeg(cId, cellInfo, xLeg_scId, yLeg_scId);
    float displace_scId_after = getDisplaceWithNewLeg(scId, cellInfo, xLeg_cId, yLeg_cId);

    float displace_before = displace_cId_before + displace_scId_before;
    float displace_after = displace_cId_after + displace_scId_after;

    float delta_displace = displace_after - displace_before;
    //cout << " \ncell : " << cId << " 's displacment changes from " << displace_cId_before << " to " << displace_cId_after << endl;
    //cout << " cell : " << scId << " 's displacment changes from " << displace_scId_before << " to " << displace_scId_after << endl;
    //cout << " delta displacement is " << delta_displace << endl;
    // 2. delta-HPWL 계산.
    float HPWL_before = 0;
    for (int i = 0; i < netsInCell[cId].size(); i++) {
        int net = netsInCell[cId][i];
        //HPWL_before += getHPWL(net, cellsInNet, cellInfo);
        HPWL_before += readHPWL(net, HPWLArch);
        //cout << "\nbefore! < " << getHPWL(net, cellsInNet, cellInfo) << " - after > " << readHPWL(net, HPWLArch);
        //if (getHPWL(net, cellsInNet, cellInfo) != readHPWL(net, HPWLArch)) cout << "mismatch detected" << endl;
    }
    for (int i = 0; i < netsInCell[scId].size(); i++) {
        int net = netsInCell[scId][i];
        //HPWL_before += getHPWL(net, cellsInNet, cellInfo);
        HPWL_before += readHPWL(net, HPWLArch);
        //cout << "\nbefore! < " << getHPWL(net, cellsInNet, cellInfo) << " - after > " << readHPWL(net, HPWLArch);
        //if (getHPWL(net, cellsInNet, cellInfo) != readHPWL(net, HPWLArch)) cout << "mismatch detected" << endl;
    }

    float HPWL_after = 0;
    for (int i = 0; i < netsInCell[cId].size(); i++) {
        int net = netsInCell[cId][i];
        //HPWL_after += getHPWLWithNewLeg(net, cellsInNet, cellInfo, cId, scId);
        HPWL_after += readModifiedHPWL(net, HPWLArch, cId, scId, cellInfo, cellsInNet);
        //cout << "\nbefore.. " << getHPWLWithNewLeg(net, cellsInNet, cellInfo, cId, scId) << " after :" << readModifiedHPWL(net, HPWLArch, cId, scId, cellInfo, cellsInNet);
        //if (getHPWLWithNewLeg(net, cellsInNet, cellInfo, cId, scId) != readModifiedHPWL(net, HPWLArch, cId, scId, cellInfo, cellsInNet)) {
        //    cout << "net = " << net << "cId = " << cId << "scId = " << scId << endl;
        //    cout << "different result in modify\n " << getHPWLWithNewLeg(net, cellsInNet, cellInfo, cId, scId) << "\n" << readModifiedHPWL(net, HPWLArch, cId, scId, cellInfo, cellsInNet) << endl;
        //}
    }
    //cout << HPWL_after << endl;
    for (int i = 0; i < netsInCell[scId].size(); i++) {
        int net = netsInCell[scId][i];
        //HPWL_after += getHPWLWithNewLeg(net, cellsInNet, cellInfo, cId, scId);
        HPWL_after += readModifiedHPWL(net, HPWLArch, scId, cId, cellInfo, cellsInNet);
        //cout << "\nbefore.. " << getHPWLWithNewLeg(net, cellsInNet, cellInfo, cId, scId) << " after :" << readModifiedHPWL(net, HPWLArch, scId, cId, cellInfo, cellsInNet);
        // if (getHPWLWithNewLeg(net, cellsInNet, cellInfo, cId, scId) != readModifiedHPWL(net, HPWLArch, cId, scId, cellInfo)) {
        //    cout << "different result in modify\n " << getHPWLWithNewLeg(net, cellsInNet, cellInfo, cId, scId) << "\n" << readModifiedHPWL(net, HPWLArch, cId, scId, cellInfo) << endl;
        //}
    }
    float delta_HPWL = HPWL_after - HPWL_before;
    // 3. cost 결정.
    // HPWL, displacement 
    // displace_before = 100, delta <= displace_before*(margin-1)
    //cout << "\n== in CalculateCost, Net : " << nId << " 에 대해서, "<< endl;
    //cout << "                     cell : " << cId << " 를 cell : " << scId << " 로 바꾸면, " << endl;
    //cout << "                     delta_dispace = " << delta_displace << ", deltaHPWL = " << delta_HPWL << endl;
    //cout << "                     HPWL changes from " << HPWL_before << " to " << HPWL_after << endl;
    if (delta_displace <= displace_before * (margin - 1) && delta_HPWL < -0.01) {
        return make_tuple(delta_HPWL, scId);
    }
    return make_tuple(10000, scId);
}

bool compareCost(tuple<float, int> t1, tuple<float, int> t2) {
    return get<0>(t1) < get<0>(t2);
}
vector<bool> validCellCheck(vector<vector<int>>& cellsInNet, vector<vector<int>>& netsInCell) {
    int numOfCell = netsInCell.size();
    int limitNumb = 500;
    vector<bool> validCell(numOfCell, true);
    //for (int i = 0; i < numOfCell; i++) {
    //    vector<int> nets = netsInCell[i];
    //    for (auto net : nets) {
    //        if (cellsInNet[net].size() > limitNumb) {
    //            validCell[i] = false;
    //        }
    //    }
    //}
    return validCell;
}
bool checkOverlap(vector<vector<float>>& cellInfo, float siteX, float siteY, float blockX, float blockY) {
    int numOfRow = floor(blockY / siteY);
    int numOfCol = floor(blockX / siteX);

    vector<vector<int>> overlapMap(numOfCol, vector<int>(numOfRow, -1));

    for (int cId = 0; cId < cellInfo.size(); cId++) {
        float xLeg = cellInfo[cId][0];
        float yLeg = cellInfo[cId][1];
        float xSize = cellInfo[cId][4];
        float ySize = cellInfo[cId][5];
        // cout << xLeg << ", " << yLeg << ", " << xSize << ", " << ySize << endl;
        int xGrid = ceil(xLeg / siteX);
        int yGrid = ceil(yLeg / siteY);
        int xGridEnd = xGrid + ceil(xSize / siteX);
        int yGridEnd = yGrid + ceil(ySize / siteY);
        // cout << "cell = " << cId << ", grid = " << xGrid << ", " << yGrid << ", " << xGridEnd << ", " << yGridEnd << endl;
        for (int i = xGrid; i < xGridEnd; i++) {
            for (int j = yGrid; j < yGridEnd; j++) {
                if (overlapMap[i][j] == -1) {
                    overlapMap[i][j] = cId;
                    //cout << "overlap" << "[" << i << ", " << j << " ]" << "is " << cId << endl;
                }
                else {
                    std::cout << "overlap" << "[" << i << ", " << j << " ]" << "is " << cId << endl;
                    std::cout << "overlap detected !!" << endl;
                    std::cout << "check cell :" << overlapMap[i][j] << " and " << cId << endl;
                    return false;
                }
            }
        }
    }
    std::cout << "overlap NOT detected !!" << endl;
    return true;
}

vector<DataHPWL> genHPWLArch(vector<vector<int>>& cellsInNet, vector<vector<float>>& cellInfo) {
    vector<DataHPWL> dataList;
    DataHPWL data;
    for (int net = 0; net < cellsInNet.size(); net++) {
        float xMin = 100000, yMin = 100000, xMax = -1, yMax = -1;
        float xMinSub = 100000, yMinSub = 100000, xMaxSub = -1, yMaxSub = -1;
        for (int cell : cellsInNet[net]) {
            vector<float> info = cellInfo[cell];
            float xLL = info[0], yLL = info[1], xUR = xLL + info[4], yUR = yLL + info[5];
            //cout << xLL << " " << yLL << " " << xUR << " " << yUR << endl;
            if (xLL < xMin) {
                xMinSub = xMin;
                xMin = xLL;
            }
            else if (xLL < xMinSub) xMinSub = xLL;

            if (yLL < yMin) {
                yMinSub = yMin;
                yMin = yLL;
            }
            else if (yLL < yMinSub) yMinSub = yLL;

            if (xUR > xMax) {
                xMaxSub = xMax;
                xMax = xUR;
            }
            else if (xUR > xMaxSub) xMaxSub = xUR;

            if (yUR > yMax) {
                yMaxSub = yMax;
                yMax = yUR;
            }
            else if (yUR > yMaxSub)yMaxSub = yUR;
        }
        float HPWL = xMax - xMin + yMax - yMin;
        data.xMax = xMax; data.xMaxSub = xMaxSub; data.yMax = yMax; data.yMaxSub = yMaxSub;
        data.xMin = xMin; data.xMinSub = xMinSub; data.yMin = yMin; data.yMinSub = yMinSub;
        data.HPWL = HPWL;
        dataList.push_back(data);
    }
    return dataList;
}
float readHPWL(int net, vector<DataHPWL>& HPWLArch) {
    return HPWLArch[net].HPWL;
}
float readModifiedHPWL_bkup(int net, vector<DataHPWL>& HPWLArch, int delCell, int addCell, vector<vector<float>>& cellInfo, vector<vector<int>>& cellsInNet) {
    float xMax = HPWLArch[net].xMax, xMin = HPWLArch[net].xMin, yMax = HPWLArch[net].yMax, yMin = HPWLArch[net].yMin;
    float xMaxSub = HPWLArch[net].xMaxSub, xMinSub = HPWLArch[net].xMinSub, yMaxSub = HPWLArch[net].yMaxSub, yMinSub = HPWLArch[net].yMinSub;

    bool flag = true;
    vector<int> cells = cellsInNet[net];
    if ((find(cells.begin(), cells.end(), delCell) != cells.end())
        && (find(cells.begin(), cells.end(), addCell) != cells.end())) return HPWLArch[net].HPWL;

    vector<float> info = cellInfo[delCell];
    float xLL = info[0], yLL = info[1], xUR = xLL + info[4], yUR = yLL + info[5];
    if (xLL == xMin) xMin = xMinSub;
    if (xUR == xMax) xMax = xMaxSub;
    if (yLL == yMin) yMin = yMinSub;
    if (yUR == yMax) yMax = yMaxSub;

    info = cellInfo[addCell];
    xLL = info[0]; yLL = info[1]; xUR = xLL + info[4]; yUR = yLL + info[5];
    if (xLL < xMin) xMin = xLL;
    if (xUR > xMax) xMax = xUR;
    if (yLL < yMin) yMin = yLL;
    if (yUR > yMax) yMax = yUR;
    float HPWL = xMax - xMin + yMax - yMin;
    return HPWL;
}
float readModifiedHPWL(int net, vector<DataHPWL>& HPWLArch, int delCell, int addCell,
    vector<vector<float>>& cellInfo, vector<vector<int>>& cellsInNet) {

    float xMax = HPWLArch[net].xMax, xMin = HPWLArch[net].xMin, yMax = HPWLArch[net].yMax, yMin = HPWLArch[net].yMin;
    float xMaxSub = HPWLArch[net].xMaxSub, xMinSub = HPWLArch[net].xMinSub, yMaxSub = HPWLArch[net].yMaxSub, yMinSub = HPWLArch[net].yMinSub;
    vector<int> cells = cellsInNet[net];

    //지우고자하는 cell 과 추가하고자 하는 cell, 즉 swap 의 대상이되는 cell 들이 모두 net에 연결. --> 그대로. --> 이건 사이즈가 같을때나 그렇지.. 이제 무조건 해줘야 해..
    //if ((find(cells.begin(), cells.end(), delCell) != cells.end())
    //    && (find(cells.begin(), cells.end(), addCell) != cells.end())) return HPWLArch[net].HPWL;
    vector<float> info = cellInfo[delCell];
    vector<float> info2 = cellInfo[addCell];
    float xLLD = info[0], yLLD = info[1], xURD = xLLD + info[4], yURD = yLLD + info[5],
        xURD2 = xLLD + info2[4], yURD2 = yLLD + info2[5];

    float xLLA = info2[0], yLLA = info2[1], xURA = xLLA + info[4], yURA = yLLA + info[5],
        xURA2 = xLLA + info2[4], yURA2 = yLLA + info2[5];

    if ((find(cells.begin(), cells.end(), delCell) != cells.end())
        && (find(cells.begin(), cells.end(), addCell) != cells.end())) {
        // dCell 지우고
        if (xLLD == xMin) xMin = xMinSub;
        if (xURD == xMax) xMax = xMaxSub;
        if (yLLD == yMin) yMin = yMinSub;
        if (yURD == yMax) yMax = yMaxSub;

        // addCell 지우고
        if (xLLA == xMin) xMin = xMinSub;
        if (xURA2 == xMax) xMax = xMaxSub;
        if (yLLA == yMin) yMin = yMinSub;
        if (yURA2 == yMax) yMax = yMaxSub;

        // addCell 추가
        if (xLLA < xMin) xMin = xLLA;
        if (xURA > xMax) xMax = xURA;
        if (yLLA < yMin) yMin = yLLA;
        if (yURA > yMax) yMax = yURA;

        // dCell 추가
        if (xLLD < xMin) xMin = xLLD;
        if (xURD2 > xMax) xMax = xURD2;
        if (yLLD < yMin) yMin = yLLD;
        if (yURD2 > yMax) yMax = yURD2;
        float HPWL = xMax - xMin + yMax - yMin;
        return HPWL;
    }


    // 지우고자 하는 cell이 net에 이미 있다면, 실행
    if ((find(cells.begin(), cells.end(), delCell) != cells.end())) {
        if (xLLD == xMin) xMin = xMinSub;
        if (xURD == xMax) xMax = xMaxSub;
        if (yLLD == yMin) yMin = yMinSub;
        if (yURD == yMax) yMax = yMaxSub;
    }
    // 추가하고자 하는 cell이 net에 없다면, 실행
    if ((find(cells.begin(), cells.end(), addCell) == cells.end())) {
        if (xLLA < xMin) xMin = xLLA;
        if (xURA > xMax) xMax = xURA;
        if (yLLA < yMin) yMin = yLLA;
        if (yURA > yMax) yMax = yURA;
    }
    float HPWL = xMax - xMin + yMax - yMin;
    return HPWL;
}

void updateHPWL_try(int cId, int scId_picked, vector<vector<int>>& cellsInNet, vector<vector<int>>& netsInCell, vector<vector<float>>& cellInfo, vector<DataHPWL>& HPWLArch,
    float siteX, float siteY, vector<vector<int>>& blockCellMap, vector<vector<int>>& blockAreaMap) {

    // 1. before update 계산. -- debugging 시만 on
    //cout << "before update 계산." << endl;
    float HPWL_before_update = 0;
    for (int i = 0; i < netsInCell[cId].size(); i++) {
        int net = netsInCell[cId][i];
        HPWL_before_update += readHPWL(net, HPWLArch);
        //cout << "net : " << net << "'s HPWL = " << readHPWL(net, HPWLArch) << endl;
    }
    for (int i = 0; i < netsInCell[scId_picked].size(); i++) {
        int net = netsInCell[scId_picked][i];
        HPWL_before_update += readHPWL(net, HPWLArch);
        //cout << "net : " << net << "'s HPWL = " << readHPWL(net, HPWLArch) << endl;
    }
    // for TEST
    /*
    cout << "after update 계산 1." << endl;
    float HPWL_after = 0;
    for (int i = 0; i < netsInCell[cId].size(); i++) {
        int net = netsInCell[cId][i];
        HPWL_after += readModifiedHPWL(net, HPWLArch, cId, scId_picked, cellInfo, cellsInNet);
        cout << "net : " << net << "'s HPWL = " << readModifiedHPWL(net, HPWLArch, cId, scId_picked, cellInfo, cellsInNet) << endl;
        cout << HPWL_after << endl;
    }

    for (int i = 0; i < netsInCell[scId_picked].size(); i++) {
        int net = netsInCell[scId_picked][i];
        HPWL_after += readModifiedHPWL(net, HPWLArch, scId_picked, cId, cellInfo, cellsInNet);
        cout << "net : " << net << "'s HPWL = " << readModifiedHPWL(net, HPWLArch, scId_picked, cId, cellInfo, cellsInNet) << endl;
        cout << HPWL_after << endl;
    }
    cout << HPWL_after << endl;
    cout << "\n Update 전 " << cId << " 와 " << scId_picked << " swap 이후에 cost는 "
        << HPWL_before_update << " 에서 " << HPWL_after << " 로 감소했다." << endl;
    */
    // 2. update 
    float xLeg_cId = cellInfo[cId][0], yLeg_cId = cellInfo[cId][1], xLeg_scId = cellInfo[scId_picked][0], yLeg_scId = cellInfo[scId_picked][1];
    cellInfo[cId][0] = xLeg_scId;
    cellInfo[cId][1] = yLeg_scId;
    cellInfo[scId_picked][0] = xLeg_cId;
    cellInfo[scId_picked][1] = yLeg_cId;
    /*
    cout << "cell : " << cId << "(" << xLeg_cId << ", " << yLeg_cId  << ") "
        << "가 cell : " << scId_picked << "(" << xLeg_scId << ", " << yLeg_scId << ") 과 위치 change" << endl;
    cout << "결과 cell : " << cId << "(" << cellInfo[cId][0] << ", " << cellInfo[cId][1] << ") " << endl;
    cout << "결과 cell : " << scId_picked << "(" << cellInfo[scId_picked][0] << ", " << cellInfo[scId_picked][1] << ") " << endl; */
    for (auto net : netsInCell[cId]) {
        float xMin = 100000, yMin = 100000, xMax = -1, yMax = -1;
        float xMinSub = 100000, yMinSub = 100000, xMaxSub = -1, yMaxSub = -1;
        for (int cell : cellsInNet[net]) {
            vector<float> info = cellInfo[cell];
            float xLL = info[0], yLL = info[1], xUR = xLL + info[4], yUR = yLL + info[5];
            //cout << xLL << " " << yLL << " " << xUR << " " << yUR << endl;
            if (xLL < xMin) {
                xMinSub = xMin;
                xMin = xLL;
            }
            else if (xLL < xMinSub) xMinSub = xLL;

            if (yLL < yMin) {
                yMinSub = yMin;
                yMin = yLL;
            }
            else if (yLL < yMinSub) yMinSub = yLL;

            if (xUR > xMax) {
                xMaxSub = xMax;
                xMax = xUR;
            }
            else if (xUR > xMaxSub) {
                xMaxSub = xUR;
            }

            if (yUR > yMax) {
                yMaxSub = yMax;
                yMax = yUR;
            }
            else if (yUR > yMaxSub) {
                yMaxSub = yUR;
            }
        }
        float HPWL = xMax - xMin + yMax - yMin;
        HPWLArch[net].xMax = xMax; HPWLArch[net].xMaxSub = xMaxSub; HPWLArch[net].yMax = yMax; HPWLArch[net].yMaxSub = yMaxSub;
        HPWLArch[net].xMin = xMin; HPWLArch[net].xMinSub = xMinSub; HPWLArch[net].yMin = yMin; HPWLArch[net].yMinSub = yMinSub;
        HPWLArch[net].HPWL = HPWL;
    }
    for (auto net : netsInCell[scId_picked]) {
        float xMin = 100000, yMin = 100000, xMax = -1, yMax = -1;
        float xMinSub = 100000, yMinSub = 100000, xMaxSub = -1, yMaxSub = -1;
        for (int cell : cellsInNet[net]) {
            vector<float> info = cellInfo[cell];
            float xLL = info[0], yLL = info[1], xUR = xLL + info[4], yUR = yLL + info[5];
            //cout << xLL << " " << yLL << " " << xUR << " " << yUR << endl;
            if (xLL < xMin) {
                xMinSub = xMin;
                xMin = xLL;
            }
            else if (xLL < xMinSub) xMinSub = xLL;
            if (yLL < yMin) {
                yMinSub = yMin;
                yMin = yLL;
            }
            else if (yLL < yMinSub) yMinSub = yLL;
            if (xUR > xMax) {
                xMaxSub = xMax;
                xMax = xUR;
            }
            else if (xUR > xMaxSub) {
                xMaxSub = xUR;
            }
            if (yUR > yMax) {
                yMaxSub = yMax;
                yMax = yUR;
            }
            else if (yUR > yMaxSub) {
                yMaxSub = yUR;
            }
        }
        float HPWL = xMax - xMin + yMax - yMin;
        HPWLArch[net].xMax = xMax; HPWLArch[net].xMaxSub = xMaxSub; HPWLArch[net].yMax = yMax; HPWLArch[net].yMaxSub = yMaxSub;
        HPWLArch[net].xMin = xMin; HPWLArch[net].xMinSub = xMinSub; HPWLArch[net].yMin = yMin; HPWLArch[net].yMinSub = yMinSub;
        HPWLArch[net].HPWL = HPWL;
    }

    // 3. after update 계산.
    //cout << "after update 계산 2." << endl;
    float HPWL_after_update = 0;
    for (int i = 0; i < netsInCell[cId].size(); i++) {
        int net = netsInCell[cId][i];
        HPWL_after_update += readHPWL(net, HPWLArch);
        //cout << "net : " << net << "'s HPWL = " << readHPWL(net, HPWLArch) << endl;
    }
    //cout << HPWL_after_update << endl;
    for (int i = 0; i < netsInCell[scId_picked].size(); i++) {
        int net = netsInCell[scId_picked][i];
        HPWL_after_update += readHPWL(net, HPWLArch);
        //cout << "net : " << net << "'s HPWL = " << readHPWL(net, HPWLArch) << endl;
    }
    //cout << HPWL_after_update << endl;
    //cout << "\n Update HPWL 함수에서 " << cId << " 와 " << scId_picked << " swap 이후에 cost는 " 
        //<< HPWL_before_update << " 에서 " << HPWL_after_update << " 로 감소했다." << endl;

    // 4. block cellMap 업데이트
    /*for (int j = 45; j >= 41; j--) {
        for (int i = 1126; i < 1137; i++) {
            cout << blockCellMap[i][j] << ", ";
        }
        cout << endl;
    }
    cout << " ==== " << endl;*/
    float xLegC = cellInfo[cId][0];
    float yLegC = cellInfo[cId][1];
    float xSizeC = cellInfo[cId][4];
    float ySizeC = cellInfo[cId][5];

    int xGridC = ceil(xLegC / siteX);
    int yGridC = ceil(yLegC / siteY);

    blockCellMap[xGridC][yGridC] = cId;

    float xLegS = cellInfo[scId_picked][0];
    float yLegS = cellInfo[scId_picked][1];
    float xSizeS = cellInfo[scId_picked][4];
    float ySizeS = cellInfo[scId_picked][5];

    float xGridS = ceil(xLegS / siteX);
    float yGridS = ceil(yLegS / siteY);

    blockCellMap[xGridS][yGridS] = scId_picked;
    /*
    for (int j = 45; j >= 41; j--) {
        for (int i = 1126; i < 1137; i++) {
            cout << blockCellMap[i][j] << ", ";
        }
        cout << endl;
    }
    cout << " ==== " << endl; */
    // 5. block areaMap 업데이트
    /*
    for (int j = 45; j >= 41; j--) {
        for (int i = 1126; i < 1137; i++) {
            cout << blockAreaMap[i][j] << ", ";
        }
        cout << endl;
    }
    cout << " ==== " << endl; */
    int xGridEndC = xGridC + ceil(xSizeC / siteX);
    int yGridEndC = yGridC + ceil(ySizeC / siteY);
    int xGridEndS = xGridS + ceil(xSizeS / siteX);
    int yGridEndS = yGridS + ceil(ySizeS / siteY);

    int xGridEndCS = xGridC + ceil(xSizeS / siteX);
    int yGridEndCS = yGridC + ceil(ySizeS / siteY);
    int xGridEndSC = xGridS + ceil(xSizeC / siteX);
    int yGridEndSC = yGridS + ceil(ySizeC / siteY);
    //cout << xGridC << ", " << yGridC << ", " << xGridS << ", " << yGridS << endl;
    //cout << cId << ", " << xSizeC << ", " << ySizeC << ", " << scId_picked << ", " << xSizeS << ", " << ySizeS << endl;
    //cout << xGridEndC << ", " << yGridEndC << ", " << xGridEndS << ", " << yGridEndS << endl;
    // cout << xGridEndCS << ", " << yGridEndCS << ", " << xGridEndSC << ", " << yGridEndSC << endl;
    for (int i = xGridC; i < xGridEndCS; i++) {
        for (int j = yGridC; j < yGridEndCS; j++) {
            blockAreaMap[i][j] = -1;
        }
    }
    for (int i = xGridC; i < xGridEndC; i++) {
        for (int j = yGridC; j < yGridEndC; j++) {
            blockAreaMap[i][j] = cId;
        }
    }
    for (int i = xGridS; i < xGridEndSC; i++) {
        for (int j = yGridS; j < yGridEndSC; j++) {
            blockAreaMap[i][j] = -1;
        }
    }
    for (int i = xGridS; i < xGridEndS; i++) {
        for (int j = yGridS; j < yGridEndS; j++) {
            blockAreaMap[i][j] = scId_picked;
        }
    }
    /* (int j = 45; j >= 41; j--) {
        for (int i = 1126; i < 1137; i++) {
            cout << blockAreaMap[i][j] << ", ";
        }
        cout << endl;
    }*/
}

void updateBlockCell(int cellId, vector<vector<float>>& cellInfo, vector<vector<int>>& blockCellMap, int siteX, int siteY) {
    float xLeg = cellInfo[cellId][0];
    float yLeg = cellInfo[cellId][1];
    float xSize = cellInfo[cellId][4];
    float ySize = cellInfo[cellId][5];
    //cout << xLeg << ", " << yLeg << endl;
    int xGrid = ceil(xLeg / siteX);
    int yGrid = ceil(yLeg / siteY);

    //cout << "blockCellMap[" << xGrid << ", " << yGrid << "] is " << blockCellMap[xGrid][yGrid];
    blockCellMap[xGrid][yGrid] = cellId;
    // << " changed to " << blockCellMap[xGrid][yGrid];
}

// old functions. <- 지금 안씀.
/*
    place 파일 포맷 : cId[0]:instName[1]:xLeg[2]:yLeg[3]:xGlob[4]:yGlob[5]:xSize[6]:ySize[7]
    net 파일 포맷   : nId[0]:netName[1]:cId[2]:cId[3]:...
*/
vector<vector<string>> readFile(string fileName) {
    string str;
    ifstream file(fileName);
    vector<vector<string>> dataList;
    while (getline(file, str)) {
        vector<string> dataInfo = parseString(str, ":");
        dataList.push_back(dataInfo);
    }
    return dataList;
}
void checkEncrytion(vector<vector<string>> dataList, string dataListName) {
    for (int i = 0; i < dataList.size(); i++) {
        if (dataList[i][0] == to_string(i)) continue;
        std::cout << "your " << dataListName << " encrytion is failed !!" << endl;
    }
    std::cout << " congratulation !!\n your " << dataListName << " encrytion succeed !!" << endl;
}
map<int, bool> genBoolMap(queue<int> queue) {
    map<int, bool> isMoved;
    while(!queue.empty()) {
        isMoved.insert(make_pair(queue.front(), true));
        queue.pop();
    }
    return isMoved;
}

bool moreImprove(map<int, bool>& isMoved) {
    for (auto iter : isMoved) {
        if (iter.second == true) {
            //std::cout << iter.first << "가 고칠게 있다." << std::endl;
            return true;
        }
    }
    // 다 false 이면 여기로 온다.
    return false;
}

void runAlgorithm_try(vector<tuple<int, float>>& dataHPWL, vector<vector<int>>& cellsInNet, vector<string>& netName,
    vector<vector<float>>& cellInfo, float siteX, float siteY, vector<vector<int>>& blockCellMap,
    vector<bool>& validCell, vector<vector<int>>& netsInCell, string logCalcCost, float marginA,
    float marginB, float maxDisp, vector<DataHPWL>& HPWLArch, int netIter,
    vector<vector<int>>& blockAreaMap, int numOfRow, int numOfCol) {

    //for(auto i=2284;i<2285;i++){
    for (auto i = 0; i < netIter; i++) {
        int nId = get<0>(dataHPWL[i]);
        float HPWL = get<1>(dataHPWL[i]);
        std::cout << "net : " << nId << " : " << i << "th, " << netName[nId] << " is processing...   HPWL ="
             << HPWL << "  net 당 cell 개수 = " << cellsInNet[nId].size() << endl;
        if (cellsInNet[nId].size() > 50) continue;

        vector<int> windowHPWL = getWindowHPWL(nId, cellsInNet, cellInfo, siteX, siteY); // xmin, xmax, ymin, ymax <-- int 단위로.
        queue<int> queue = genCellQueue(cellsInNet, nId, cellInfo);
        map<int, bool> isMoved = genBoolMap(queue);
        vector<int> modifiedCells; // add 22. 11. 15. fix net swap argument cells of net.
        //while (!queue.empty()) {
        while(moreImprove(isMoved)){
            int cId = queue.front();
            queue.pop();
            vector<tuple<int, int>> windowCell = getWindowCell(windowHPWL, cId, cellInfo, siteX, siteY, marginA, blockCellMap, maxDisp);
            if (windowCell.size() == 0) {
                //continue;
                isMoved[cId] = false;
            }
            vector<int> candidateCells = getCandidateCell_try(windowCell, blockCellMap, cId, cellInfo, validCell, siteX, siteY, blockAreaMap, numOfRow, numOfCol);

            if (candidateCells.size() > 300) candidateCells.erase(candidateCells.begin() + 300, candidateCells.end());
            vector<tuple<float, int>> cost; // float = cost, int = candidateCells[i]

            for (int i = 0; i < candidateCells.size(); i++) {
                int scId = candidateCells[i]; // swap cell Id
                tuple<float, int> swapCost = calculateSwapCost(nId, cId, scId, cellInfo, netsInCell, cellsInNet, logCalcCost, marginB, HPWLArch);
                if (get<0>(swapCost) == 10000) {
                    continue;
                }
                else {
                    cost.push_back(swapCost);
                }
            }
            if (cost.empty()) {
                //continue;
                isMoved[cId] = false;
            }
            else {
                sort(cost.begin(), cost.end(), compareCost);
                // swap operation & update & queue 에 다시 집어 넣기.

                int scId_picked = get<1>(cost[0]);
                cout << "\n 따라서." << cId << " 를 " << scId_picked << " 로 swap 한다. !! HPWL decreased by" << get<0>(cost[0]) << endl;
                
                updateHPWL_try(cId, scId_picked, cellsInNet, netsInCell, cellInfo, HPWLArch, siteX, siteY, blockCellMap, blockAreaMap);
                //queue.push(cId);
                isMoved[cId] = true;
                if (find(modifiedCells.begin(), modifiedCells.end(), cId) == modifiedCells.end()) 
                    modifiedCells.push_back(cId);// add 22. 11. 15. fix net swap argument cells of net.
            }
            queue.push(cId);
        }
        // add 22. 11. 15. fix net swap argument cells of net.
        for (int i = 0; i < modifiedCells.size(); i++) validCell[i] = false;
    }
    std::cout << "after procedure, avg displacement = " << getAvgDisplace(cellInfo) << endl;
    std::cout << "after procedure, avg HPWL = " << getAvgHPWL(cellsInNet, cellInfo) << endl;
}
