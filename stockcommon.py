import numpy as np
import pandas as pd
import datetime
import time
import tushare as ts
import os


data_dir = "/home/shangjz/PycharmProjects/stock/data/"  # 下载数据的存放路径
sleep_time = 5
# 获取感兴趣的所有股票信息，
def get_all_stock_id():
    stock_info = ts.get_stock_basics()
    return  stock_info.index.tolist()

#获取感兴趣的所有股票信息，这里只获取沪深300股票
def get_hs300_stock_id():
    stock_info=ts.get_hs300s()
    return stock_info['code'].values

#获取从起始日期到截止日期中间的的所有日期，前后都是封闭区间
def get_date_list(begin_date, end_date):
    date_list = []
    while begin_date <= end_date:
        #date_str = str(begin_date)
        date_list.append(begin_date)
        begin_date += datetime.timedelta(days=1)
    return date_list
