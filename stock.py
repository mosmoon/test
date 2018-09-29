import numpy as np
import pandas as pd
import datetime
import time
import tushare as ts
import os

data_dir = "/home/shangjz/PycharmProjects/stock/data/"  # 下载数据的存放路径
sleep_time = 5

#本地实现判断市场开市函数
#@date: str类型日期 eg.'2017-11-23'
def is_open_day(date):
    if date in cal_dates['calendarDate'].values:
        return cal_dates[cal_dates['calendarDate']==date].iat[0,1]==1
    return False





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

#从TuShare获取tick data数据并保存到本地
#@symbol: str类型股票代码 eg.600030
#@date: date类型日期
#symbol = stocks[1]
#date = dates[1]
def get_save_tick_data(symbol, date):
    global sleep_time,data_dir
    res=True
    str_date=str(date)
    dir=data_dir+symbol+'/'+str(date.year)+'/'+str(date.month)
    file=dir+'/'+symbol+'_'+str_date+'_tick_data.h5'
    if is_open_day(str_date):
        if not os.path.exists(dir):
            os.makedirs(dir)
        if not os.path.exists(file):
            try:
                d= ts.get_tick_data(symbol, str_date, pause=0.1,src='tt')
            except IOError as msg:
                print(str(msg).decode('UTF-8'))
                sleep_time=min(sleep_time*2, 128)#每次下载失败后sleep_time翻倍，但是最大128s
                print('Get tick data error: symbol: ' + symbol + ', date: ' + str_date + ', sleep time is: ' + str(sleep_time))
                return res
            else:
                hdf5_file=pd.HDFStore(file, 'w',complevel=4, complib='blosc')
                ##hdf5_file.keys()          #没有保存数据
                hdf5_file.append("d",d)
                hdf5_file.close()
                sleep_time=max(sleep_time/2, 2) #每次成功下载后sleep_time变为一半，但是至少2s
                print('Successfully download and save file: ' + file + ', sleep time is: ' + str(sleep_time))
                return res
        else:
            print("Data already downloaded before, skip " + file)
            res=False
            return res

#ts.get_sz50s() #获取上证50成份股  返回值为DataFrame：code股票代码 name股票名称
cal_dates = ts.trade_cal() #返回交易所日历，类型为DataFrame, calendarDate  isOpen
cal_dates.head(1)

# 从TuShare下载感兴趣的所有股票的历史成交数据，并保存到本地HDF5压缩文件
# dates=get_date_list(datetime.date(2017,11,6), datetime.date(2017,11,12))
dates = get_date_list(datetime.date(2018, 7, 30), datetime.date(2018, 9, 28))
stocks = get_all_stock_id()
sorcks = get_hs300_stock_id()
for stock in stocks:
    for date in dates:
        if get_save_tick_data(stock, date):
            time.sleep(sleep_time)

#根据分笔成交数据生成1分钟线
#根据分笔成交数据生成1分钟线
def gen_min_line(symbol, date):
    global data_dir
    str_date=str(date)
    dir=data_dir+symbol+'\\'+str(date.year)+'\\'+str(date.month)
    tickfile=dir+'\\'+symbol+'_'+str_date+'_tick_data.h5'
    minfile=dir+'\\'+symbol+'_'+str_date+'_1min_data.h5'
    if (os.path.exists(tickfile)) and (not os.path.exists(minfile)):
        hdf5_file=pd.HDFStore(tickfile, 'r')
        df=hdf5_file['data']
        hdf5_file.close()
        print "Successfully read tick file: "+tickfile
        if df.shape[0]<10: #TuShare即便在停牌期间也会返回tick data，并且只有三行错误的数据，这里利用行数小于10把那些unexpected tickdata数据排除掉
            print "No tick data read from tick file, skip generating 1min line"
            return 0
        df['time']=str_date+' '+df['time']
        df['time']=pd.to_datetime(df['time'])
        df=df.set_index('time')
        price_df=df['price'].resample('1min').ohlc()
        price_df=price_df.dropna()
        vols=df['volume'].resample('1min').sum()
        vols=vols.dropna()
        vol_df=pd.DataFrame(vols,columns=['volume'])
        amounts=df['amount'].resample('1min').sum()
        amounts=amounts.dropna()
        amount_df=pd.DataFrame(amounts,columns=['amount'])
        newdf=price_df.merge(vol_df, left_index=True, right_index=True).merge(amount_df, left_index=True, right_index=True)
        hdf5_file2=pd.HDFStore(minfile, 'w')
        hdf5_file2['data']=newdf
        hdf5_file2.close()
        print "Successfully write to minute file: "+minfile

dates=get_date_list(datetime.date(2017,8,1), datetime.date(2017,11,12))
stocks=get_all_stock_id()
for stock in stocks:
    for date in dates:
        gen_min_line(stock, date)


