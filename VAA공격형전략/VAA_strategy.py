import pandas as pd
import numpy as np
import yfinance as yf
from datetime import timedelta
from datetime import datetime

def getPrices_nM_ago(df, n, today):
    resultDf = df
    resultDate = today - timedelta(days = n*30)
    resultDateStr = resultDate.strftime("%Y-%m-%d")
    cnt = 0
    while(not(resultDateStr in df.index)):
        cnt = cnt+1
        if(cnt >= 15): break
        resultDate = resultDate - timedelta(days = 1)
        resultDateStr = resultDate.strftime("%Y-%m-%d")
    return df.loc[resultDateStr]['Close']

def makePriceList(df, today):
    plist = []
    plist.append(getPrices_nM_ago(df, 0, today))
    plist.append(getPrices_nM_ago(df, 1, today))
    plist.append(getPrices_nM_ago(df, 3, today))
    plist.append(getPrices_nM_ago(df, 6, today))
    plist.append(getPrices_nM_ago(df, 12, today))
    return plist

def make_rate_of_return_df(df_financePrices, isDefence = False):
    if(isDefence):
        result_df = pd.DataFrame(index = ['LQD', 'IEF', 'SHY'], columns= ['now', '1m ago', '3m ago', '6m ago', '12m ago'])
    else:
        result_df = pd.DataFrame(index = ['AGG', 'EFA', 'VWO', 'SPY'], columns= ['now', '1m ago', '3m ago', '6m ago', '12m ago'])
    for tiker in df_financePrices.index:
        priceNow = df_financePrices.loc[tiker]['now']
        result_df.loc[tiker]['now'] = " "
        result_df.loc[tiker]['1m ago'] = priceNow/df_financePrices.loc[tiker]['1m ago']-1
        result_df.loc[tiker]['3m ago'] = priceNow/df_financePrices.loc[tiker]['3m ago']-1
        result_df.loc[tiker]['6m ago'] = priceNow/df_financePrices.loc[tiker]['6m ago']-1
        result_df.loc[tiker]['12m ago'] = priceNow/df_financePrices.loc[tiker]['12m ago']-1
    return result_df

def make_momentumScore_df(rate_of_return_df, isDefence = False):
    if(isDefence):
        result_df = pd.DataFrame(index = ['LQD', 'IEF', 'SHY'], columns= ['now', '1m ago', '3m ago', '6m ago', '12m ago'])
    else:
        result_df = pd.DataFrame(index = ['AGG', 'EFA', 'VWO', 'SPY'], columns= ['now', '1m ago', '3m ago', '6m ago', '12m ago'])
    for tiker in result_df.index:
        result_df.loc[tiker]['now'] = 0
        result_df.loc[tiker]['1m ago'] = rate_of_return_df.loc[tiker]['1m ago']*12
        result_df.loc[tiker]['3m ago'] =  rate_of_return_df.loc[tiker]['3m ago']*4
        result_df.loc[tiker]['6m ago'] =  rate_of_return_df.loc[tiker]['6m ago']*2
        result_df.loc[tiker]['12m ago'] =  rate_of_return_df.loc[tiker]['12m ago']*1
    return result_df

def main():
    today = datetime.today()

    #공격형 자산
    df_AGG = yf.download('AGG',start= '2019-01-01')
    df_EFA = yf.download('EFA',start = '2019-01-01')
    df_VWO = yf.download('VWO',start = '2019-01-01')
    df_SPY = yf.download('SPY',start = '2019-01-01')

    df_financePrices = pd.DataFrame(index = ['AGG', 'EFA', 'VWO', 'SPY'], columns= ['now', '1m ago', '3m ago', '6m ago', '12m ago'])
    df_financePrices.loc['AGG'] = makePriceList(df_AGG, today)
    df_financePrices.loc['EFA'] = makePriceList(df_EFA, today)
    df_financePrices.loc['VWO'] = makePriceList(df_VWO, today)
    df_financePrices.loc['SPY'] = makePriceList(df_SPY, today)
    rate_of_return_df = make_rate_of_return_df(df_financePrices)
    momentumScore_df = make_momentumScore_df(rate_of_return_df)
    momentumScoreTotal = momentumScore_df.sum(axis=1)
    display('기준일', today.strftime("%Y-%m-%d"))
    display('주가', df_financePrices)
    display('수익률', rate_of_return_df)
    display('모멘텀 스코어', momentumScore_df)
    momentumScoreTotal = momentumScoreTotal.sort_values(ascending = False)
    display('공격자산 종합 모멘텀 스코어', momentumScoreTotal)
    buy_OffensiveAssets = True

        #안전자산
    df_LQD = yf.download('LQD',start= '2019-01-01')
    df_IEF = yf.download('IEF',start = '2019-01-01')
    df_SHY = yf.download('SHY',start = '2019-01-01')

    df_financePricesDefence = pd.DataFrame(index = ['LQD', 'IEF', 'SHY'], columns= ['now', '1m ago', '3m ago', '6m ago', '12m ago'])
    df_financePricesDefence.loc['LQD'] = makePriceList(df_LQD, today)
    df_financePricesDefence.loc['IEF'] = makePriceList(df_IEF, today)
    df_financePricesDefence.loc['SHY'] = makePriceList(df_SHY, today)
    rate_of_return_df_defence = make_rate_of_return_df(df_financePricesDefence, isDefence = True)
    momentumScore_df_defence = make_momentumScore_df(rate_of_return_df_defence, isDefence = True)
    momentumScoreTotal_defence = momentumScore_df_defence.sum(axis=1)
    display('기준일', today.strftime("%Y-%m-%d"))
    display('주가', df_financePricesDefence)
    display('수익률', rate_of_return_df_defence)
    display('안전 자산 모멘텀 스코어', momentumScore_df_defence)
    momentumScoreTotal_defence = momentumScoreTotal_defence.sort_values(ascending = False)
    display('안전자산 종합 모멘텀 스코어', momentumScoreTotal_defence)

    for score in momentumScoreTotal:
        if(score <= 0):
            buy_OffensiveAssets = False
    if(buy_OffensiveAssets):
        print('\033[1m')
        print('\033[105m','공격자산 매수', '\033[0m')
        print("매수할 종목명 및 스코어 :\n", momentumScoreTotal.iloc[0:1])#가장 스코어가 높은 자산을 매수
    else:
        print('\033[1m')
        print('\033[106m','안전자산 매수', '\033[0m')
        print("매수할 종목명 및 스코어 :\n", momentumScoreTotal_defence.iloc[0:1])#가장 스코어가 높은 자산을 매수

if __name__ =="__main__":
    main()