"""
cellList = [cellId, rowPos, colPos, rowNumb, colNumb, rowMax, colMax]

1.  regionPosition (rowPos, colPos) 에 대한
    coordinate  <--> number transform 필요.
    (i 행, j 열) --> 30*i + j

0 <= rowPos < 10
0 <= colPos < 30

rowNumb, colNumb, rowMx, colMax 는 1 부터 기산.

rowPosMod = rowPos - (rowNumb - 1) # 현재 rowPos 를 (rowNumb = 1, colNumb = 1) 기준 position 으로 변경.
colPosMod = colPos - (colNumb - 1) # 현재 rowPos 를 (rowNumb = 1, colNumb = 1) 기준 position 으로 변경.

"""
priceMtx = {}
priceMtx[1] = {}
priceMtx[1][2] = {} # row,col

overlapMtx = {}
overlapMtx[1] = {}
overlapMtx[1][2] = {} # row,col

def calculatePrice(cellId, rowMax, colMax):
    price = 10 
    return price

def makePriceAndOverlapMtx(row, col, cellList, margin):
    """
    예시.
    cellList = ["A", 1,1,2,2,2,3]
    makePriceAndOverlapMtx(1, 2, cellList, 2)
    """
    cellId, rowPos, colPos, rowNumb, colNumb, rowMax, colMax = cellList
    rowPosMod = rowPos - (rowNumb - 1) # 현재 rowPos 를 (rowNumb = 1, colNumb = 1) 기준 position 으로 변경.
    colPosMod = colPos - (colNumb - 1) # 현재 rowPos 를 (rowNumb = 1, colNumb = 1) 기준 position 으로 변경.

    rowPosModMax = rowPosMod + (rowMax -1)
    colPosModMax = colPosMod + (colMax -1)

    generator = [] # 유의미한 position으로 assign 된 rowPosMod, colPosMod 의 집합.
    if margin == 0: 
        if rowPosMod >=0 and rowPosModMax < 10 and colPosMod >=0 and colPosModMax < 30:
            generator.append([rowPosMod, colPosMod])
    else:
        for i in range(rowPosMod-margin, rowPosMod+margin+1):
            for j in range(colPosMod-margin, colPosMod+margin+1):
                if i >=0 and (i + rowMax -1) < 10 and j >=0 and (j + colMax -1) < 30:
                    generator.append([i,j])    

    # 0. encoding coord --> scalar
    for i,j in generator:
        code = 30*i+j # cell 의 시작지점 postion 에 대해 encoding 한 code
        print("cell 시작 code ", code)
        # 1. priceMtx
        """ 
            priceMtx[row][col][cellId][code] = price # code = 30*i+j
        """
        if cellId not in priceMtx[row][col].keys():priceMtx[row][col][cellId] = {}
        
        price = calculatePrice(cellId, rowMax, colMax)
        if code not in priceMtx[row][col][cellId].keys():
            priceMtx[row][col][cellId][code] = price
        
        """ Position 이 유의미한 range 안에 들어왔기 때문에, 
            <- rowPosMod >=0 and rowPosModMAx < 10 and colPosMod >=0 and colPosModMax < 30
            30*i+j 로 encoding 을 해도 괜찮다. """

        # 2. overlapMtx
        for di in range(i, i+rowMax):
            for dj in range(j, j+colMax):
                overCode = di*30 + dj # cell 이 커버하는 전 영역에 대한 code.
                print("cover 영역 코드 ", overCode, "\n rowMax, colMax = ", rowMax, colMax)
                if overCode not in overlapMtx[row][col].keys(): overlapMtx[row][col][overCode] = []
                overlapMtx[row][col][overCode].append([cellId, code])

cellList = ["A", 1,1,2,2,2,3]
margin = 2
makePriceAndOverlapMtx(1, 2, cellList, margin)

