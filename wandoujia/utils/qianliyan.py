import json
from urllib.parse import urljoin
import requests
from lxml import etree

# 构造二级分类的url
base_url = "http://bj.ohqly.com/"
# 一级目录
cates = [
    {"cate_name": "工商注册", "url": "/1811.shtml"},
    {"cate_name": "商标专利", "url": "/1813.shtml"}
]


def get_first_category():
    """
    获取千里眼网站的各地区网站链接
    :return:
    """
    # 请求北京地区的链接
    result = requests.get(base_url)
    # 转换为HTML
    html = parse_response(result)
    # 直辖市
    direct_cities = html.xpath('//div[@id="content"]/div[1]/a[@class="weui_cell"]')
    for direct_city in direct_cities:
        # 创建字典
        dd = dict()
        # 直辖市名称
        city_name = direct_city.xpath('./span/text()')[0]
        print("查看城市的名称：", city_name)
        # 直辖市的链接
        city_url = direct_city.xpath('./@href')[0]
        # 向字典中增加数据
        dd['city_name'] = city_name
        dd['city_url'] = city_url
        # 写入文件
        record_result(dd)
    # 各省名称
    provinces = html.xpath('//div[@id="content"]/div[1]/a[@class="weui_cell parent"]')
    for index, province in enumerate(provinces):
        # 创建字典用于存储省市信息
        dd = dict()
        # 获取省的名称
        province_name = province.xpath('./span/text()')[0]
        # 获取各省-->市的列表
        cites = html.xpath('//div[@id="content"]/div[1]/div[{}]/a'.format(index + 1))
        # 创建一个列表用于存储每一个省份的城市信息
        dp = list()
        for city in cites:
            # 创建字典，存储城市和url
            dc = dict()
            # 获取城市名称
            city_name = city.xpath('./span/text()')[0]
            # 获取城市链接
            city_url = city.xpath('./@href')[0]
            # 字典中添加数据
            dc['city_name'] = city_name
            dc['city_url'] = city_url
            # 将该城市信息添加到列表中
            dp.append(dc)
        # 向省市的字典中添加数据
        dd['province_name'] = province_name
        dd['city'] = dp
        # 写入文件
        record_result(dd)


def start_urls(path):
    """
    读取文件，拼接两类的请求地址
    :param path:
    :return:
    """
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    dd = list()
    for line in lines:
        data = json.loads(line)
        # 判断字典值是否为空
        if data.get('city_url'):
            url = data.get('city_url')
            dd.append(url)
        else:
            for d in data.get('city'):
                url = d.get('city_url')
                dd.append(url)
    with open(r'G:\工作\APP\wandoujia\urls.txt', 'w+', encoding='utf-8') as f:
        # 拼接两类的url
        for u in dd:
            for cate in cates:
                # 获取url
                url = cate.get('url')
                whole = urljoin(u, url)
                f.write(whole + "\n")


def record_result(data):
    """
    将结果写入文件
    :param data:
    :return:
    """
    path = r'G:\工作\APP\wandoujia\city_urls.json'
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
    # get_first_category()
    start_urls(r'G:\工作\APP\wandoujia\city_urls.json')
