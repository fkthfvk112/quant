import pandas as pd
import numpy as np
import FinanceDataReader as fdr
from datetime import timedelta

#오류(영업일 아님 등)는 계산에 넣지 않음 

def add_moving_avg(df):
    df['60mavg'] = df['Close'].rolling(60).mean()
    df['120mavg'] = df['Close'].rolling(120).mean()
    df['240mavg'] = df['Close'].rolling(240).mean()
    df['360mavg'] = df['Close'].rolling(360).mean()
    df.dropna(inplace = True)

def add_volum_avg(df):
    df['60volumAvg'] = df['Volume'].rolling(60).mean()
    df['120volumAvg'] = df['Volume'].rolling(120).mean()
    df['240volumAvg'] = df['Volume'].rolling(240).mean()
    df['360volumAvg'] = df['Volume'].rolling(360).mean()
    df.dropna(inplace = True)

def breakNmoveAvg(df, n):
    avgName = '{}mavg'.format(n)
    con1 = df['Close'] >= df[avgName]
    con2 = df['Open'] <= df[avgName]
    return df[con1 & con2]

def breakMoveVolumAvg(df, n):
    avgName = '{}volumAvg'.format(n)
    con1 = df['Volume'] >= df[avgName]
    return df[con1]

def costAfterN(df, date, n, cnt=0): 
    dateAfter = date + timedelta(days = n)
    if(cnt>=15): return None
    try:
        result = df.loc[dateAfter, 'Close']
        return result
    except:
        return costAfterN(df, date, n+1, cnt+1)
    
def percentageOfLater(beforePrice, afterPrice):
    #  등락률 = (금일종가 – 전일종가) / 전일종가 * 100
    return (afterPrice-beforePrice)/beforePrice*100


    
allDatas = fdr.StockListing('KRX')


result = []

datas1000 = allDatas['Code'][0:500]

for stockCode in datas1000:
    stock = fdr.DataReader(stockCode)
    add_volum_avg(stock)
    add_moving_avg(stock)
    stock = breakMoveVolumAvg(stock, 360) #시장 마감시 거래량이 n거래량 이동평균선 돌파
    stock = breakNmoveAvg(stock, 360)#종가가 n주가 이동평균성 돌파

    breakThoroughDays = stock.index
    rate_of_return = []
    for day in breakThoroughDays:
        costNow = stock.loc[day, 'Close']
        costAfter = costAfterN(stock, day, 240) #n일 후의 주가 
        if(costAfter == None):
            continue
            
        #display("현재가", costNow)
        #display("30일 이후 가", costAfter)
        rate_of_return.append([day,costNow, costAfter, percentageOfLater(costNow, costAfter)])

    _240n30daysResult = pd.DataFrame(rate_of_return, columns = ['기준일', 'cost before', 'cost after', '수익률'])
    #display(_240n30daysResult)
    result.append((_240n30daysResult['수익률'].mean()))
#display(result)
result = pd.Series(result)
#display(result)
result.dropna(inplace = True)
display("평균 상승률: ", round(result.mean(), 3))
display("중위수: ", round(result.median(), 3))