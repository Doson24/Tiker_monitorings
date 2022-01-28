
"""
Формулы расчета индикатора Bollinger Bands на примере простой Cкользящей средней (Simple Moving Average):

Основная линия (средняя)

ML = SUM(CLOSE N)/ N = SMA (CLOSE N), где:

SUM сумма за N периодов
CLOSE цена закрытия свечи
N количество периодов, используемых для расчета
SMA простая Скользящая средняя.
Верхняя линия рассчитывается на основании средней

TL = ML + (D* StdDev), где D - число стандартных отклонений.

Нижняя линия рассчитывается так же на основании средней

BL = ML – (D* StdDev), где D число стандартных отклонений.

При этом StdDev рассчитывается по формуле:

StdDev = SQRT (SUM ((CLOSE — SMA (CLOSE, N))^2, N)/N), где SQRT квадратный корень.
"""
import numpy as np
import yfinance as yf
from numpy import empty

from Alarms import sound, current_trend
from ichimoku import open_file_and_split
import json
import time
import pandas as pd
from statistics import stdev

def middle_line(data, tiker,period):
    data_close = data['Close'][tiker].dropna()
    ml_list = []
    for count in range(len(data_close)):
        data_period = data_close.iloc[(len(data_close) - count) - period: len(data_close) - count]
        ml_point = sum(data_period) / period
        ml_list.append(ml_point)
    ml = pd.Series(ml_list, data_close.index[::-1])
    return ml

def top_line(data, tiker, period, d):
    data_close = data['Close'][tiker].dropna()
    tl_list = []
    ml = middle_line(data, tiker,period)
    # ml = ml[::-1]
    # ml = ml[period-1:]
    for count in range(len(data_close)):
        data_period = data_close.iloc[(len(data_close) - count) - period: len(data_close) - count]
        # stdev выдает ошибку при пустом data_period
        if data_period.size == 0:
            break
        tl_point = ml[count] + (d * np.std(data_period))
        tl_list.append(tl_point)
    data_tl = data_close.index[::-1]
    data_tl = data_tl[:-period+1]
    tl = pd.Series(tl_list, data_tl) #из-за этого изменилась размерность tl_list
    return tl

def bottom_line(data, tiker, period, d):
    data_close = data['Close'][tiker].dropna()
    tl_list = []
    ml = middle_line(data, tiker, period)
    # ml = ml[::-1]
    # ml = ml[period-1:]
    for count in range(len(data_close)):
        data_period = data_close.iloc[(len(data_close) - count) - period: len(data_close) - count]
        # stdev выдает ошибку при пустом data_period
        if data_period.size == 0:
            break
        tl_point = ml[count] - (d * np.std(data_period))
        tl_list.append(tl_point)
    data_bl = data_close.index[::-1]
    data_bl = data_bl[:-period + 1]
    bl = pd.Series(tl_list, data_bl)  # из-за этого изменилась размерность tl_list
    return bl

def download_data(tikers, period,  interval='1h'):

    # tikers = list(templates.keys())

    data = yf.download(tikers, interval=interval, period=period)
    data = data.dropna(how='all')
    return data
#asdqerwaSaasdas
if __name__ == "__main__":
    tikers = ['SBER.ME', 'TAL', "VKCO.IL"]
    period_download = '1mo'
    data = download_data(tikers, period_download)
    tiker = tikers[0]
    period = 20
    middle_line(data, tiker, period)
    d = 2
    top_line(data, tiker, period, d)
    bottom_line(data, tiker, period, d)