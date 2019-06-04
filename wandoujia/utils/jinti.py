import json
import requests
from lxml import etree

base_url = 'http://www.jinti.com/shangbiao/selectcity/'     # 各个地区的链接


def get_start_urls():
    """
    请求所有地区的链接的页面，获取所有的地区的链接
    :return:
    """
    # 请求页面
    result = requests.get(base_url)
    # 转换成HTML
    html = parse_response(result)
    # 解析页面获取所有的地区名称和链接
    all_cities = html.xpath('//div[@id="map_1"]/div[2]/dl/dd/a')
    print("查看所由的城市：", all_cities)
    # 获取每一个地区名称和链接
    for city in all_cities:
        # 创建字典存储结果
        dd = dict()
        # 城市的名称, 此处需要注意一个问题就是 '\r\n'是获取的列表项的第一位
        local = "".join(city.xpath('./descendant::text()')).strip()
        # 城市的链接
        url = city.xpath('./@href')[0]
        # 向字典中更新数据
        dd['local'] = local
        dd['url'] = url
        # 将数据写入文件
        record_result(dd)


def record_result(data):
    """
    将结果写入文件
    :param data:
    :return:
    """
    path = r'G:\工作\APP\wandoujia\all_city.json'
    with open(path, 'a+', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def parse_response(res):
    """
    将获取的响应转换为HTML
    :param res: 响应（text）
    :return: HTML
    """
    try:
        if res.status_code == 200:
            # 测试时使用
            print("查看获取的响应<login-parse_response>：", res.text)
            res.encoding = res.apparent_encoding
            return etree.HTML(res.text, etree.HTMLParser())
        else:
            print("响应的状态码不是200")
            return False
    except Exception as e:
        print(e)


# 测试代码
if __name__ == "__main__":
    get_start_urls()