import requests
import numpy as np
import pandas as pd
import time
import json
from pyecharts import options as opts
from pyecharts.charts import Bar


def getTime():
    return int(round(time.time() * 1000))


def getList(length):
    List = []
    for i in range(length):
        temp = js['returndata']['datanodes'][i]['data']['strdata']
        # 原网站有同比增长数据为空，若直接使用eval()会报错，需要先判断
        if (len(temp) != 0):
            # eval()数字转字符串
            List.append(eval(temp))
    return List


if __name__ == '__main__':
    # 请求目标网址(链接?前面的东西)
    url = 'https://data.stats.gov.cn/easyquery.htm'
    # 请求头，User-Agent: 用来证明你是浏览器，满足一定格式即可，不一定和自己的浏览器一样
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}  # 浏览器代理
    key = {}  # 参数键值对
    key['m'] = 'QueryData'
    key['dbcode'] = 'csyd'
    key['rowcode'] = 'zb'
    key['colcode'] = 'sj'
    key['wds'] = '[{"wdcode":"reg","valuecode":"610100"}]'
    key['dfwds'] = '[]'
    key['k1'] = str(getTime())
    # 禁用安全请求警告
    requests.packages.urllib3.disable_warnings()
    # 发出请求，使用post方法，这里使用前面自定义的头部和参数
    # ！！！verify=False，国家统计局20年下半年改用https协议,若不加该代码无法通过SSL验证
    r = requests.post(url, headers=headers, params=key, verify=False)
    # 使用json库中loads函数，将r.text字符串解析成dict字典格式存储于js中
    js = json.loads(r.text)
    # print(js)
    # 得到所需数据的一维数组，利用np.array().reshape()整理为二维数组
    length = len(js['returndata']['datanodes'])
    res = getList(length)
    # 总数据划分成31行的格式
    # print(res)
    array = np.array(res).reshape(6, 10)
    # np.array()转换成pd.DataFrame格式，后续可使用to_excel()直接写入excel表格

    df_houseprice = pd.DataFrame(array)
    # print(df_houseprice)
    df_houseprice.columns = ['2021年10月',
                             '2021年9月',
                             '2021年8月',
                             '2021年7月',
                             '2021年6月',
                             '2021年5月',
                             '2021年4月',
                             '2021年3月',
                             '2021年2月',
                             '2021年1月']
    for ind in df_houseprice.columns:
        print(df_houseprice)
        print(ind)

        l1 = ["新建商品住宅销售价格指数(上月=100)",
                "新建商品住宅销售价格指数(上年同月=100)",
                "新建商品住宅销售价格指数(当期基期年=100)	",
                "二手住宅销售价格指数(上月=100)",
                "二手住宅销售价格指数(上年同月=100)",
                "二手住宅销售价格指数(当期基期年=100)"]
        arr = df_houseprice[""+ind+""]
        print(arr)
        # 此时传回的arr并不是真正能够使用的数组，而是dataframe类型的数据
        # 需要使用.value 建立一个新的数组（ar）
        ar = arr.values
        print(ar)
        bar = (
            Bar()
                .add_xaxis(l1)
                # 这时候如果直接在y轴取值的时候，直接传入数组 ar 根据debug 显示的是传回的是一个地址值
                # 这个时候 通过 list(ar) 将其改为可用数组，这个时候bar就可以正常使用了
                .add_yaxis("住宅销售价格", list(ar))
                # .add_yaxis("住宅销售价格", ["100.4","101.2","106.6","98.6","74.9","94.7"])
                .set_global_opts(xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-12)),
                                 title_opts=opts.TitleOpts(title="西安市部分住宅销售价格指数统计表", subtitle=str(ind))
                                 )
        )
        # bar.add
        filepath = 'houseprice_show/' + str(ind) + '西安市各类住宅销售价格指数统计.html'
        bar.render(path=filepath)

    print(df_houseprice)
