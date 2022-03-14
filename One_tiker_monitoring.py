from ichimoku import tenkan_sen, senkou_spanA, senkou_spanB, chikou_span
import yfinance as yf
from Alarms import sound, current_trend, file_tiker
from ichimoku import open_file_and_split
import json
import time

def crossing_tenkan_sen(cost, tenkan_sen_value):
    return cost[-1] > tenkan_sen_value[0] > cost[-2] or cost[-1] < tenkan_sen_value[0] < cost[-2]


def crossing_kijun_sen(cost, kijun_sen_value):
    return cost[-1] > kijun_sen_value[0] > cost[-2] or cost[-1] < kijun_sen_value[0] < cost[-2]


def in_cloud(cost, senkou_spanA_value, senkou_spanB_value):
    return senkou_spanA_value[25] < cost[-1] < senkou_spanB_value[25] or senkou_spanB_value[25] < cost[-1] < \
            senkou_spanA_value[25]

def crossing_tenkan_and_kijun(tenkan_sen_value, kijun_sen_value):
    return tenkan_sen_value[0] > kijun_sen_value[0] and tenkan_sen_value[1] <= kijun_sen_value[1]

def down_trend(tenkan_sen_value, kijun_sen_value, cost, senkou_spanA_value, senkou_spanB_value):
    return tenkan_sen_value[0] < kijun_sen_value[0] and cost[-1] < senkou_spanB_value[25] and cost[-1] < senkou_spanA_value[
        25]

def monitoring(templates, interval='1h'):
    period = '1mo'
    tikers = list(templates.keys())

    data = yf.download(tikers,  interval=interval, period=period)
    data_ichimoko = data.dropna(how='all')
    # data_ichimoko = data_ichimoko.index.tz_convert('Asia/Krasnoyarsk')
    for tiker, value in templates.items():
        # value = 4

        tenkan_sen_value = tenkan_sen(data_ichimoko, 9, tiker)
        kijun_sen_value = tenkan_sen(data_ichimoko, 26, tiker)
        senkou_spanA_value = senkou_spanA(tenkan_sen_value, kijun_sen_value, 26)
        senkou_spanB_value = senkou_spanB(tenkan_sen(data_ichimoko, 52, tiker), tenkan_sen_value, 26)
        chikou_span_value = chikou_span(data_ichimoko, 26, tiker)

        cost = data_ichimoko['Close'][tiker].dropna()
        cost_open = data_ichimoko['Open'][tiker].dropna()
        # cost = cost.index.tz_convert('Asia/Krasnoyarsk')
        """
        1 пересечение цены линии стандарта
        2 пересечение цены линии разворота
        3 косание цены облака
        4 резкое пробитие линии разворота
        5 Low UP Trend
        6 Low Down Trend 
        7 Dont Trade (cost in cloud)
        8 Down Trend
        9 Цена вышла из облака, a Линия Стандарта нет
        10 Strong UP Trend
        """
        if value == 1 and crossing_tenkan_sen(cost, tenkan_sen_value):
            print(tiker, ' пересечение цены линии стандарта')
            sound()
        if value == 2 and crossing_kijun_sen(cost, kijun_sen_value):
            print(tiker, ' пересечение цены линии разворота')
            sound()
        if value == 3 and in_cloud(cost, senkou_spanA_value, senkou_spanB_value):
            print(tiker, ' косание цены облака')
            sound()

        if value == 4 and kijun_sen_value[0] < tenkan_sen_value[0] and\
                cost[-1] < kijun_sen_value[0] and cost[-2] > tenkan_sen_value[0]:
            print(
                f'{tiker} {cost.index[-1].date()} - резкое пробитие линии разворота {float("{0:.1f}".format(cost[-1]))}$')
        if value == 5 and tenkan_sen_value[0] < kijun_sen_value[0] and cost[-1] > senkou_spanA_value[25] > senkou_spanB_value[25]:
            print(f'{tiker} {cost.index[-1].date()} - Low UP Trend {float("{0:.1f}".format(cost[-1]))}$')
        if value == 6 and tenkan_sen_value[0] > kijun_sen_value[0] and cost[-1] < senkou_spanA_value[25] and cost[-1] < \
                senkou_spanB_value[25]:
            print(f'{tiker} {cost.index[-1].date()} - Low Down Trend {float("{0:.1f}".format(cost[-1]))}$')
        if value == 7 and (senkou_spanA_value[25] < cost[-1] < senkou_spanB_value[25] or senkou_spanB_value[25] < cost[-1] < senkou_spanA_value[25]):
            print(f'{tiker} {cost.index[-1].date()} - Dont Trade (cost in cloud) {float("{0:.1f}".format(cost[-1]))}$')

        if value == 8 and tenkan_sen_value[0] < kijun_sen_value[0] and cost[-1] < senkou_spanB_value[25] and cost[-1] < \
                senkou_spanA_value[25]:
            # and chikou_span_value[-1] < cost[-(1 + 24)] and chikou_span_value[-1] < cost_open[-(1 + 24)]:
            print(f'{tiker} {cost.index[-1].date()} - Down Trend {float("{0:.1f}".format(cost[-1]))}$')
            sound()
        if value == 9 and tenkan_sen_value[0] > kijun_sen_value[0] and cost[-1] > senkou_spanB_value[25] and cost[-1] > \
                senkou_spanA_value[
                    25] and chikou_span_value[-1] > cost[-(1 + 24)] and chikou_span_value[-1] > cost_open[-(1 + 24)] and \
                (senkou_spanA_value[25] < tenkan_sen_value[0] < senkou_spanB_value[25] or
                 senkou_spanA_value[25] > tenkan_sen_value[0] > senkou_spanB_value[25]):
            print(
                f'{tiker} {cost.index[-1].date()} - Цена вышла из облака, a Линия Стандарта нет {float("{0:.1f}".format(cost[-1]))}$')
            sound()
        if value == 10 and tenkan_sen_value[0] > kijun_sen_value[0] and cost[-1] > senkou_spanB_value[25] and cost[-1] > \
                senkou_spanA_value[
                    25] and chikou_span_value[-1] > cost[-(1 + 24)] and chikou_span_value[-1] > cost_open[-(1 + 24)] and \
                tenkan_sen_value[0] > senkou_spanB_value[25] and tenkan_sen_value[0] > senkou_spanA_value[25]:
            print(f'{tiker} {cost.index[-1].date()} - Strong UP Trend {float("{0:.1f}".format(cost[-1]))}$')
            sound()
        lag = 26
        for i in range(1, 5):
            if cost[-i] > tenkan_sen_value[i - 1] > kijun_sen_value[i - 1] and cost[-i] > kijun_sen_value[i - 1] and \
                    cost[-i] > senkou_spanA_value[i + lag] and cost[-i] > senkou_spanB_value[i + lag] and \
                    (cost[-(i + 1)] <= senkou_spanA_value[i + lag] or cost[-(i + 1)] <= senkou_spanB_value[i + lag]) and \
                    (chikou_span_value[-i] > cost_open[-(i + lag)]) and (chikou_span_value[-i] > cost[-(i + lag)]):
                print(
                    f'{tiker} {cost.index[-i].date()} {cost.index[-i].tz_convert("Asia/Krasnoyarsk").strftime("%H:%M:%S")} '
                    f'- {float("{0:.1f}".format(cost[-i]))}$ Entry point for Up Trend ')
                sound()
        if tenkan_sen_value[0] > kijun_sen_value[0] and cost[-1] > senkou_spanB_value[25] and cost[-1] > \
                senkou_spanA_value[
                    25] and tenkan_sen_value[1] < kijun_sen_value[1]:
            print(
                f'{tiker} {cost.index[-1].date()} {cost.index[-1].tz_convert("Asia/Krasnoyarsk").strftime("%H:%M:%S")}'
                f' - Возможная точка ПОДБОРА в UP trend (c>p, c[-1] < p [-1], выше облака')
            sound()
    print('_' * 70, "\nТекущие тренды \n")

    """
    Для текущего состояния тикеров
    """
    for tiker, value in templates.items():
        tenkan_sen_value = tenkan_sen(data_ichimoko, 9, tiker)
        kijun_sen_value = tenkan_sen(data_ichimoko, 26, tiker)
        senkou_spanA_value = senkou_spanA(tenkan_sen_value, kijun_sen_value, 26)
        senkou_spanB_value = senkou_spanB(tenkan_sen(data_ichimoko, 52, tiker), tenkan_sen_value, 26)
        chikou_span_value = chikou_span(data_ichimoko, 26, tiker)

        current_trend(data_ichimoko, tenkan_sen_value, kijun_sen_value, senkou_spanA_value, senkou_spanB_value,
              chikou_span_value, tiker)

def trend_interval(file, period, interval):
    pass

if __name__ == '__main__':
    # tiker = input('Введите отслеживаемый Тикер - ')
    # input('Введите варианты отслеживания: \n '
    #       '1 - пересечение цены линии стандарта \n'
    #       '2 - пересечение цены линии разворота \n'
    #       '3 - косание цены облака \n'
    #       '')

    # a = {'RUB=X': 2, 'BABA': 2, 'CSCO': 2, 'T': 2, 'KO': 2, 'MAIL.IL': 2, 'EBS': 2, 'MOMO': 2, 'INTC': 2, 'PFE': 2,
    #      'TAL': 2, 'VIPS': 2, 'AFLT.ME': 2, 'VTBR.ME': 2, 'GAZP.ME': 2, 'SIBN.ME': 2, 'ATVI': 2, 'AYX': 2, 'FLOT.ME': 2,
    #      'BYND': 2, 'TATN.ME': 2, 'HHR': 2, 'FXCN.ME': 2, 'BZUN': 2}
    list_periods = ['6mo', 'max', 'max']
    list_interval = ['1d', '1wk', '1mo']
    files = ['Portfolio.txt', 'Список желаемых.txt', 'Список индексов.txt'
             ,'ALL_Moex.txt', 'ALL_spb.txt']
    #

    file = 'Мониторинг.json'
    with open(file) as f:
        templates = json.load(f)
    s = input(f"insert Sleep time(s) for interval=1h, tikers={file}:")
    monitoring(templates)
    for file in files:
        for i in range(0, len(list_interval)-1):
            print(f'trends in {file}')
            result_1d = file_tiker(file, list_periods[i], list_interval[i])
            # name1d = [i['name'] for i in result_1d]
            # date_time1d = [i['date_time'] for i in result_1d]
            # text1d = [i['text'] for i in result_1d]
            # print(f'trends in {file}')
            # result_1w = file_tiker(file, list_periods[i], list_interval[i])
    time.sleep(int(s))
    print(list(templates.keys()))
    while True:
        monitoring(templates)
        seconds = int(s)
        print(f'sleep {seconds}')
        time.sleep(seconds)