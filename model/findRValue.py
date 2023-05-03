import numpy as np
from sklearn.linear_model import LinearRegression
from openpyxl import load_workbook

def findRValue(x, y):
    x = np.array(x).reshape((-1, 1))
    y = np.array(y)

    model = LinearRegression().fit(x, y)
    return model.score(x, y)

# The source xlsx file is named as source.xlsx
wb=load_workbook("Analysis.xlsx")

rValues = []
for sheetKey in wb.sheetnames:
    sheet = wb[sheetKey]
    fptsColumn = sheet['GO']
    fpts = []
    isHeaderRow = True
    for x in range(len(fptsColumn)):
        if isHeaderRow:
            isHeaderRow = False
            continue
        fpts.append(fptsColumn[x].value) 

    for x in sheet.columns:
        values = []
        isHeaderRow = True
        statType = ''
        for cell in x:
            if isHeaderRow:
                isHeaderRow = False
                statType = cell.value
                continue
            values.append(cell.value)
        isHeaderRow = True

        rValue = findRValue(values, fpts)
        rValues.append(
            {
                'Position': sheetKey,
                'stat': statType,
                'rValue': rValue
            }
        )
        #print('R Value for {} is {}'.format(statType, rValue))

rValues.sort(key=lambda x: x['rValue'], reverse=True)
count = 0
for val in rValues:
    print(val)
    
    count += 1
    if count == 50:
        break
