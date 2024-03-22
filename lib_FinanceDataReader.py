# https://backtesting.tistory.com/entry/How-to-Collect-Exchange-Rate-Information-Using-Python
import FinanceDataReader as fdr

# USD/KRW 환율 정보 가져오기

class Exchanger :
    usd = fdr.DataReader('USD/KRW', '2018-01-01', '2023-12-31')['Close']
    usd20180101 = usd['2018-01-01']
    usd20180102 = usd['2018-01-02']
    usd20180103 = usd['2018-01-03']
    #exchange_rate = fdr.DataReader('USD/KRW').iloc[-1][0]
    messages = []

    # pandas, dataframe, 특정 index 유무 검사, [in] '특정index명' in df.index
    truefalse1 = '2023-12-22' in usd.index
    truefalse2 = '2023-12-23' in usd.index
    truefalse3 = '2023-12-24' in usd.index
    truefalse4 = '2023-12-25' in usd.index
    
    def __init__(self):
        a = []
        #login = MailLogin()

    def getUSD2KRW(self):
        return fdr.DataReader('USD/KRW').iloc[-1][0]

if __name__ == '__main__':
    exc = Exchanger()
    a = exc.getUSD2KRW()
    print(a)
