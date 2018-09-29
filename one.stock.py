import numpy as np
import pandas as pd
import datetime
import time
import tushare as ts
import os
import stockcommon

data_dir = "/home/shangjz/PycharmProjects/stock/data/"  # 下载数据的存放路径
sleep_time = 5




dates = get_date_list(datetime.date(2017, 10, 30), datetime.date(2017, 11, 4))
