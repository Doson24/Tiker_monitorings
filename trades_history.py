import pandas as pd
import yfinance as yf
import datetime
from pathlib import Path
from ichimoku import open_file_and_split
from ichimoku import tenkan_sen, senkou_spanA, senkou_spanB, chikou_span
from ichimoku import show_plot

def all_input_trades(data_ichimoko, tenkan_sen_value, kijun_sen_value, senkou_spanA_value, senkou_spanB_value, chikou_span_value, tiker):
    cost = data_ichimoko['Close'][tiker].dropna()
    cost_open = data_ichimoko['Open'][tiker].dropna()
    count = 0
    lag = 26
    # цена > (стандарта и разворота) + выше облака, стандарт >= разворотной, стандарт выше облака, опаздывающая > цены
    for i in range(1, len(cost) - 25):
        if cost[-i] > tenkan_sen_value[i-1] and cost[-i] > kijun_sen_value[i-1] and \
                cost[-i] > senkou_spanA_value[i+lag] and cost[-i] > senkou_spanB_value[i+lag] and \
                (cost[-(i+1)] <= senkou_spanA_value[i+lag] or cost[-(i+1)] <= senkou_spanB_value[i+lag]) and \
                    (chikou_span_value[-i] > cost_open[-(i + lag)]) and (chikou_span_value[-i] > cost[-(i + lag)]):

                # (tenkan_sen_value[i-1] > (senkou_spanA_value[25] and senkou_spanB_value[25])) \
                # and (chikou_span_value[-1] > cost[-26]):
                # cost[-(i+1)] > (tenkan_sen_value[i] and kijun_sen_value[i]) and \

            print(f'{tiker} {cost.index[-i]} - Entry point for Up Trend ')
            count += 1
    return count
if __name__ == '__main__':
    # start = datetime.datetime.now()
    # path = Path('Search.txt')
    # searchList = open_file_and_split(path)
    searchList = 'BABA', 'CSCO'
    start_date = '2008-01-01'
    data = yf.download(searchList, start=start_date)
    data_ichimoko = data.dropna(how='all')

    for tiker in searchList:
        tenkan_sen_value = tenkan_sen(data_ichimoko, 9, tiker)
        kijun_sen_value = tenkan_sen(data_ichimoko, 26, tiker)
        senkou_spanA_value = senkou_spanA(tenkan_sen_value, kijun_sen_value, 26)
        senkou_spanB_value = senkou_spanB(tenkan_sen(data_ichimoko, 52, tiker), tenkan_sen_value, 26)
        chikou_span_value = chikou_span(data_ichimoko, 26, tiker)

        a = all_input_trades(data_ichimoko, tenkan_sen_value, kijun_sen_value, senkou_spanA_value, senkou_spanB_value, chikou_span_value, tiker)
        print(f'количество сигналов для {tiker} = {a}')