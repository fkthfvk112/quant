import pandas as pd
import numpy as np
import FinanceDataReader as fdr
from datetime import timedelta
from datetime import datetime


def get_highPrice_Ndays(df, nowDate, n):
    dateBefore = nowDate - timedelta(days=n)
    nowDate_m1 = nowDate - timedelta(days=1)
    nowDate_m1_str = nowDate_m1.strftime("%Y-%m-%d")
    dateBefore_str = dateBefore.strftime("%Y-%m-%d")
    cnt = 0
    while(not(dateBefore_str in df.index)):
        cnt = cnt+1
        print('인덱스에 값 없음:이전 일자 탐색', dateBefore_str)
        dateBefore = dateBefore - timedelta(days=1)
        dateBefore_str = dateBefore.strftime("%Y-%m-%d")
        if(cnt >= 7): return 'noValideData' #no valid date index

    tempDf = df.loc[dateBefore_str:nowDate_m1_str]
    tempDf = tempDf['Close']
    nMaxValue = tempDf.max()
    print(dateBefore_str, ", ",nowDate_m1_str, "사이 최고가 : ", nMaxValue)
    return nMaxValue

def isBreakOut(df, nowDate, n_highPrice):
    if(not(nowDate in df.index)): return False
    nowPrice_open = df.loc[nowDate]['Open']
    nowPrice_close = df.loc[nowDate]['Close']
    print('금일 가격', nowPrice_close)
    print('최고가', n_highPrice)
    nowPrice_close = int(nowPrice_close)
    n_highPrice = int(n_highPrice)
    if(nowPrice_close > n_highPrice and nowPrice_open < n_highPrice): return True
    else: return False

def costAfterN(df, dateNow, n):
    resultDf = df
    resultDate = dateNow + timedelta(days = n)
    resultDateStr = resultDate.strftime("%Y-%m-%d")
    cnt = 0
    while(not(resultDateStr in df.index)):
        resultDate = resultDate + timedelta(days = 1)
        resultDateStr = resultDate.strftime("%Y-%m-%d")
        
    return df.loc[resultDateStr]['Close']

    
def percentageOfLater(beforePrice, afterPrice):
    #  등락률 = (금일종가 – 전일종가) / 전일종가 * 100
    return (afterPrice-beforePrice)/beforePrice*100

    
allDatas = fdr.StockListing('KRX')


one_days_after_result = []
three_days_after_result = []
seven_days_after_result = []
thirty_days_after_result = []
sixty_days_after_result = []
breakDays = []



datas50 = allDatas['Code'][200:250]

for code in datas50:#종목 반복
    stock = fdr.DataReader(code)
    stock = stock.loc['2018-02-02':'2023-02-02']#검토 일자

    startDate = datetime(2020, 1, 1)
    startDate_str = startDate.strftime("%Y-%m-%d")
    endDate_str = '2022-02-06'
    print('종목 코드: ', code)
    notValidCnt = 0


    while(startDate_str != endDate_str):#하루씩 증가시키며 검사(날짜 반복)
        if(not(startDate_str in stock.index)): #휴장일이면 다음 날로 넘어감
            startDate = startDate + timedelta(days = 1)
            startDate_str = startDate.strftime("%Y-%m-%d")
        
        if(notValidCnt >= 3): break #유효하지 않은 값 3번 이상이면 제외

        print('현재 날짜 : ', startDate_str)
        if(startDate_str == endDate_str): break
        high = get_highPrice_Ndays(stock, startDate, 365)#365일 고가를 기준으로
        if(high == 'noValideData'): 
            notValidCnt = notValidCnt + 1
            continue
        conBreakOut = isBreakOut(stock, startDate_str, high)#돌파
        print(conBreakOut)
        if(conBreakOut):
            afterOnePrice = costAfterN(stock, startDate, 1)
            afterThreePrice = costAfterN(stock, startDate, 3)
            afterSevenPrice = costAfterN(stock, startDate, 7)
            afterThirtyPrice = costAfterN(stock, startDate, 30)
            afterSixtyPrice = costAfterN(stock, startDate, 60)

            nowPrice = stock.loc[startDate_str]['Close']
            
            profitOne = percentageOfLater(nowPrice, afterOnePrice)
            profitThree = percentageOfLater(nowPrice, afterThreePrice)
            profitSeven = percentageOfLater(nowPrice, afterSevenPrice)
            profitThirty = percentageOfLater(nowPrice, afterThirtyPrice)
            profitSixty = percentageOfLater(nowPrice, afterSixtyPrice)
            
            #print('1일 이후 가격 : ', afterPrice, '현재 가격 :', nowPrice, '이익 :', profit)
            one_days_after_result.append(round(profitOne, 3))
            three_days_after_result.append(round(profitThree, 3))
            seven_days_after_result.append(round(profitSeven, 3))
            thirty_days_after_result.append(round(profitThirty, 3))
            sixty_days_after_result.append(round(profitSixty, 3))

            breakDays.append(startDate_str)
        startDate = startDate + timedelta(days = 1)
        startDate_str = startDate.strftime("%Y-%m-%d") 

#print(breakDays)
print('1일후', one_days_after_result)
print('3일후', three_days_after_result)
print('7일후', seven_days_after_result)
print('30일후', thirty_days_after_result)
print('60일후', sixty_days_after_result)

print("데이터 생성 완료")
resultDatasOne = pd.Series(one_days_after_result)
resultDatasThree = pd.Series(three_days_after_result)
resultDatasSeven = pd.Series(seven_days_after_result)
resultDatasThirty = pd.Series(thirty_days_after_result)
resultDatasSixty = pd.Series(sixty_days_after_result)




dateList = [1, 3, 7, 30, 60]
inx = 0
for resultData in [resultDatasOne, resultDatasThree, resultDatasSeven, resultDatasThirty, resultDatasSixty]:
    print('------------------{0}일 후----------------------\n'.format(dateList[inx]))
    inx += 1
    print("최대값", resultData.max())
    print("최소값", resultData.min())
    print("평균", resultData.mean())
    print("중위수", resultData.median())
    print("총 돌파 데이터 개수", resultData.count())

    increasDatas = resultData[resultData > 0]
    decreaseDatas = resultData[resultData <= 0]

    print('상승한 개수', increasDatas.count())
    print('하락한 개수', decreaseDatas.count())
    print('오를 확률', increasDatas.count()/resultDatasOne.count())
    print('떨어질 확률', decreaseDatas.count()/resultDatasOne.count())
    print('상승한 데이터의 평균', increasDatas.mean())
    print('상승한 데이터의 중위수', increasDatas.median())

    print('하락한 데이터의 평균', decreaseDatas.mean())
    print('하락한 데이터의 중위수', decreaseDatas.median())

