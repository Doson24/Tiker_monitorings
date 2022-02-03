import pandas as pd
import yfinance as yf
import datetime
from pathlib import Path
from ichimoku import open_file_and_split
from ichimoku import tenkan_sen, senkou_spanA, senkou_spanB, chikou_span
import winsound
import time
from ichimoku import show_plot
import sys
from loguru import logger
from collections import Counter
logger.remove()
logger.add(sys.stderr, format="{time} {level} {message}")
logger.add("logger.log")

def sound():
    frequency = 800  # Set Frequency To 2500 Hertz
    duration = 2000  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)
    time.sleep(1)


""" Точки входа """


def input_trades(data_ichimoko, tenkan_sen_value, kijun_sen_value, senkou_spanA_value, senkou_spanB_value,
                 chikou_span_value, tiker, n, interval):
    # точки входа за последние n дней
    cost = data_ichimoko['Close'][tiker].dropna()
    cost_open = data_ichimoko['Open'][tiker].dropna()
    lag = 26
    # цена > (стандарта и разворота) + выше облака, стандарт >= разворотной, стандарт выше облака, опаздывающая > цены
    for i in range(1, n):
        if cost[-i] > tenkan_sen_value[i - 1] > kijun_sen_value[i - 1] and cost[-i] > kijun_sen_value[i - 1] and \
                cost[-i] > senkou_spanA_value[i + lag] and cost[-i] > senkou_spanB_value[i + lag] and \
                (cost[-(i + 1)] <= senkou_spanA_value[i + lag] or cost[-(i + 1)] <= senkou_spanB_value[i + lag]) and \
                (chikou_span_value[-i] > cost_open[-(i + lag)]) and (chikou_span_value[-i] > cost[-(i + lag)]):

            logger.info(f'{tiker} {cost.index[-i].date()} - '
                            f'{float("{0:.1f}".format(cost[-i]))}$ Entry point for Up Trend for interval={interval}')
            # print("-" * 70, '\n' f'{tiker} {cost.index[-i].date()} {cost.index[-i].strftime("%H:%M:%S")} - '
            #                 f'{float("{0:.1f}".format(cost[-i]))}$ Entry point for Up Trend')
            # print("-" * 70)
            # print(recommendationLast(tiker), '\n', '_' * 69)

            # show_plot(tenkan_sen_value, kijun_sen_value, senkou_spanA_value, senkou_spanB_value, chikou_span_value)
            # sound()
            return {'name': tiker, 'date_time': [cost.index[-i].date(), cost.index[-i].strftime("%H:%M:%S")],
                    'text': f'{float("{0:.1f}".format(cost[-i]))}$ Entry point for Up Trend'}

    if tenkan_sen_value[0] > kijun_sen_value[0] and cost[-1] > senkou_spanB_value[25] and cost[-1] > senkou_spanA_value[
        25] and tenkan_sen_value[1] < kijun_sen_value[1]:
        logger.info(f'{tiker} {cost.index[-1].date()} '
                        f'- Возможная точка ПОДБОРА в UP trend (c>p, c[-1] < p [-1], выше облака)for interval={interval}')

        # print("-" * 70, '\n' f'{tiker} {cost.index[-1].date()} {cost.index[-1].strftime("%H:%M:%S")} '
        #                 f'- Возможная точка ПОДБОРА в UP trend (c>p, c[-1] < p [-1], выше облака)')
        # print("-" * 70)
        # print(recommendationLast(tiker))
        # sound()
        return {'name': tiker, 'date_time': [cost.index[-1].date(), cost.index[-1].strftime("%H:%M:%S")],
                    'text': f'{float("{0:.1f}".format(cost[-1]))}$ - Возможная точка ПОДБОРА в UP trend (c>p, c[-1] < p [-1], выше облака)'}


''' Текущие тренды '''


def current_trend(data_ichimoko, tenkan_sen_value, kijun_sen_value, senkou_spanA_value, senkou_spanB_value,
                  chikou_span_value, tiker):

    """Не определяет тренд для ENRU.ME 14.12.21
        потому что запаздывающая линия ниже цены для Up trend"""

    cost = data_ichimoko['Close'][tiker].dropna()
    cost_open = data_ichimoko['Open'][tiker].dropna()
    if kijun_sen_value[0] < tenkan_sen_value[0] and cost[-1] < kijun_sen_value[0] and cost[-2] > tenkan_sen_value[0]:
        print(f'{tiker} {cost.index[-1].date()} - резкое пробитие линии разворота {float("{0:.1f}".format(cost[-1]))}$')
    if tenkan_sen_value[0] < kijun_sen_value[0] and cost[-1] > senkou_spanA_value[25] > senkou_spanB_value[25]:
        print(f'{tiker} {cost.index[-1].date()} - Low UP Trend {float("{0:.1f}".format(cost[-1]))}$')
    if tenkan_sen_value[0] > kijun_sen_value[0] and cost[-1] < senkou_spanA_value[25] and cost[-1] < senkou_spanB_value[
        25]:
        print(f'{tiker} {cost.index[-1].date()} - Low Down Trend {float("{0:.1f}".format(cost[-1]))}$')
    if senkou_spanA_value[25] < cost[-1] < senkou_spanB_value[25] or senkou_spanB_value[25] < cost[-1] < \
            senkou_spanA_value[25]:
        print(f'{tiker} {cost.index[-1].date()} - Dont Trade (cost in cloud) {float("{0:.1f}".format(cost[-1]))}$')
    if tenkan_sen_value[0] < kijun_sen_value[0] and cost[-1] < senkou_spanB_value[25] and cost[-1] < senkou_spanA_value[
        25]:
        # and chikou_span_value[-1] < cost[-(1 + 24)] and chikou_span_value[-1] < cost_open[-(1 + 24)]:
        print(f'{tiker} {cost.index[-1].date()} - Down Trend {float("{0:.1f}".format(cost[-1]))}$')
        # logger.info(f'{tiker} {cost.index[-1].date()} - Down Trend {float("{0:.1f}".format(cost[-1]))}$')
    if tenkan_sen_value[0] > kijun_sen_value[0] and cost[-1] > senkou_spanB_value[25] and cost[-1] > senkou_spanA_value[
        25] and chikou_span_value[-1] > cost[-(1 + 24)] and chikou_span_value[-1] > cost_open[-(1 + 24)] and \
            (senkou_spanA_value[25] < tenkan_sen_value[0] < senkou_spanB_value[25] or
             senkou_spanA_value[25] > tenkan_sen_value[0] > senkou_spanB_value[25]):
        print(
            f'{tiker} {cost.index[-1].date()} - Цена вышла из облака, a Линия Стандарта нет {float("{0:.1f}".format(cost[-1]))}$')

    if tenkan_sen_value[0] > kijun_sen_value[0] and cost[-1] > senkou_spanB_value[25] and cost[-1] > senkou_spanA_value[
        25] and chikou_span_value[-1] > cost[-(1 + 24)] and chikou_span_value[-1] > cost_open[-(1 + 24)] and \
            tenkan_sen_value[0] > senkou_spanB_value[25] and tenkan_sen_value[0] > senkou_spanA_value[25]:
        print(f'{tiker} {cost.index[-1].date()} - Strong UP Trend {float("{0:.1f}".format(cost[-1]))}$')

def max_counter(inputlist):
    a = Counter(pd.Series.tolist(inputlist))
    maxList = []
    max_count_el = 0
    sortlist = sorted(a.values(), reverse=True)
    # if max(a.values()) == 0.0:
    #     max_el = max(a.values()) - 1
    for key, value in a.items():
        if value == sortlist[0] and key == 0.0:
            max_count_el = sortlist[1]
    for key, value in a.items():
        if value == max_count_el:
            maxList.append(key)
    return {max_count_el: maxList}

def crosing_point_bigline_cloud(cost, point):
    return cost[-1] > point > cost[-2] or cost[-1] < point < cost[-2]

def crossing_bigLine_ichimoko_cloud(data_ichimoko, tiker, points, interval):
    cost = data_ichimoko['Close'][tiker].dropna()
    a = list(points.values())
    for point in a[0]:
        if crosing_point_bigline_cloud(cost, point) is True:
            logger.warning(f'{tiker} {cost.index[-1].date()} - '
                        f'{float("{0:.1f}".format(cost[-1]))}$ crossing big line Ichimoko cloud for interval={interval}')
            return {'name': tiker, 'date_time': [cost.index[-1].date(), cost.index[-1].strftime("%H:%M:%S")],
                    'text': f'{float("{0:.1f}".format(cost[-1]))}$ crossing big line Ichimoko cloud'}


def file_tiker(filename, period, interval):
    path = Path(filename)
    searchList = open_file_and_split(path)
    # searchList = 'BABA', 'CSCO'

    # start_date = '2008-01-01'
    start_date = '2021-01-01'

    data = yf.download(searchList, period=period, interval=interval)
    data_ichimoko = data.dropna(how='all')
    buy_list = 0
    list_input_trades = []
    for tiker in searchList:
        b = None
        try:
            tenkan_sen_value = tenkan_sen(data_ichimoko, 9, tiker)
            kijun_sen_value = tenkan_sen(data_ichimoko, 26, tiker)
            senkou_spanA_value = senkou_spanA(tenkan_sen_value, kijun_sen_value, 26)
            senkou_spanB_value = senkou_spanB(tenkan_sen(data_ichimoko, 52, tiker), tenkan_sen_value, 26)
            chikou_span_value = chikou_span(data_ichimoko, 26, tiker)

            a = input_trades(data_ichimoko, tenkan_sen_value, kijun_sen_value, senkou_spanA_value, senkou_spanB_value,
                             chikou_span_value, tiker, 5, interval)
            crossing_bigLine_ichimoko_cloud(data_ichimoko, tiker, max_counter(senkou_spanA_value), interval)
            crossing_bigLine_ichimoko_cloud(data_ichimoko, tiker, max_counter(senkou_spanB_value), interval)
            if a != None:
                list_input_trades.append(a)
            # b = a
            # current_trend(data_ichimoko, tenkan_sen_value, kijun_sen_value, senkou_spanA_value, senkou_spanB_value,
            #               chikou_span_value, tiker)
        except Exception:
            print(f"{tiker} - ERROR input data ichimoku  ")

        if a != None:
            buy_list += 1

        # print(max_counter(senkou_spanA_value))
    if buy_list == 0:
        print('_' * 70, '\nНет точек входа для выбранных инструментов')
        # time.sleep(120)
    # if buy_list != 0:
    #     time.sleep(3600)
    return list_input_trades

def recommendationLast(tiker):
    try:
        a = yf.Ticker(tiker).recommendations.tail(5)
    except:
        a = f'No recommendation this {tiker}'
    return a


if __name__ == '__main__':
    start = datetime.datetime.now()
    """
    period : str
            Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            Either Use period parameter or use start and end
    interval : str
            Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            Intraday data cannot extend last 60 days
    """
    period = '2y'
    interval = '1wk'
    # print('Текущий портфель\n ')
    # list = file_tiker('Portfolio.txt', period, interval)
    #
    # print('\n Список желаемых \n ')
    # file_tiker('Список желаемых.txt', period, interval)
    #
    # print('\n Индексы, валюта \n ')
    # list = file_tiker('Список индексов.txt', period, interval)

    # print('\n Вся МОС БИРЖА \n ')
    # list = file_tiker('ALL_Moex.txt', period, interval)

    print('\n Вся СПБ БИРЖА \n ')
    list1 = file_tiker('ALL_spb.txt', period, interval)
    print(f'\n{"_" * 70}')
    for key in list1:
        print(f"{key['name']} {key['date_time'][0].strftime('%Y-%m-%d')} {key['date_time'][1]} {key['text']}")

    """
    'name': tiker, 'date_time': [cost.index[-i].date(), cost.index[-i].strftime("%H:%M:%S")],
                    'text': f'{float("{0:.1f}".format(cost[-i]))}$ Entry point for Up Trend'
    """

    end = datetime.datetime.now() - start
    print(f'\nВремя работы: {end}')

    time.sleep(3600)

# up trend 100% cost > c > p, cost > senkou_spanA > senkouB, lag > cost
# down trend 100% cost < c < p, cost < senkou_spanA < senkouB, lag < cost
# low up trend c < p, cost > senkou_spanA > senkouB, lag > cost
# dont trade senkou_spanB < cost < senkou_spanA or senkou_spanA < cost < senkou_spanB
#
