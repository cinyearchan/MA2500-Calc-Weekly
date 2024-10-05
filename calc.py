# -*- coding: UTF-8 -*-
import baostock as bs
import numpy as np
import pandas as pd
import datetime as dt
import requests
import os

SCKEY = os.environ.get('SCKEY')


def send_server(title, text):
    api = "https://sctapi.ftqq.com/{}.send".format(SCKEY)
    content = text.replace('\n', '\n\n')
    data = {
        'title': title,  # 标题
        'desp': content}  # 内容
    res = requests.post(api, data=data)
    return res


def main():
    try:
        lg = bs.login()
        print('login respond error_code:' + lg.error_code)
        print('login respond  error_msg:' + lg.error_msg)
        # LOGIN
        t = dt.datetime.utcnow()
        # print('伦敦标准时间', t)
        t = t + dt.timedelta(hours=8)
        # print('北京时间', t)
        t11 = t + dt.timedelta(days=-365 * 11 - 3)
        # print('11年前的此刻', t11)
        d = t.strftime('%Y-%m-%d')
        # print('当天日期', d)
        d11 = t11.strftime('%Y-%m-%d')
        # print('11年前的今天', d11)
        # TIME
        result = pd.DataFrame()
        k = bs.query_history_k_data_plus("sh.000001", "date,code,close", start_date=d11, end_date=d, frequency="d",
                                         adjustflag="3")
        result = pd.concat([result, k.get_data()], axis=0, ignore_index=True)
        result.date = pd.to_datetime(result.date)
        result = result.sort_values(by='date', ascending=False)
        result = result.reset_index(drop=True)
        # ESSENTIAL DATA
        today = pd.DataFrame()
        today['close'] = result.nlargest(2500, 'date').close
        ma_2500 = today.close.astype(float).mean()
        ma_underrate = int(ma_2500 / 1.2 * 100) / 100  # 比较便宜 与 极度低估 分界线
        ma_mild_bubble = int((ma_2500 * 1.2) * 100) / 100  # 估值合理 与 轻度泡沫 分界线
        ma_severely_bubble = int((ma_2500 * 1.4) * 100) / 100  # 轻度泡沫 与 重度泡沫 分界线
        ma_crazy = int((ma_2500 * 1.6) * 100) / 100  # 重度泡沫 与 玩命 分界线

        ma_2500 = int(ma_2500 * 100) / 100  # 估值合理 线

        close_today = int(float(result.loc[0, 'close']) * 100) / 100  # 收盘价
        # CALC ma_2500
        print('玩命线', ma_crazy)
        print('高度泡沫线', ma_severely_bubble)
        print('轻度泡沫线', ma_mild_bubble)
        print('ma_2500', ma_2500)
        print('低估线', ma_underrate)
        print('沪指今日收盘价', close_today)
        print('----------------------------')

        if close_today <= ma_underrate:
            tilt = "沪指极度低估"
        else:
            if close_today <= ma_2500:
                judge = "比较便宜"
            elif ma_2500 < close_today <= ma_mild_bubble:
                judge = "估值合理"
            elif ma_mild_bubble < close_today <= ma_severely_bubble:
                judge = "轻度泡沫"
            elif ma_severely_bubble < close_today <= ma_crazy:
                judge = "重度泡沫"
            else:
                judge = "玩命"
            tilt = "沪指" + str(close_today) + "点 " + judge
        print(tilt)
        # GENERATE TITLE
        # 斜杠用来代码换行
        cont = "北京时间：" + str(t) +\
               "\n今日数据 \n\t -拿命玩股线: " + str(ma_crazy) + \
               "\n\t -高度泡沫线: " + str(ma_severely_bubble) + \
               "\n\t -轻度泡沫线: " + str(ma_mild_bubble) + \
               "\n\t -估值合理线: " + str(ma_2500) + \
               "\n\t -极度低估线: " + str(ma_underrate)
        test_out = cont.replace('\n', '\n\n')
        print(cont)
        send_server(tilt, cont)  # 插入在需要推送的地方，我这里的"Her said"是我的标题，msg是我前面爬取的消息'''
        bs.logout
    except Exception:
        error = "服务异常"
        # send_server('每周ma_2500计算服务异常', error)
        print(error)
        print(Exception)


if __name__ == '__main__':
    main()
