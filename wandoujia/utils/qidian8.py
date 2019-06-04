import json
from urllib.parse import urljoin
import requests
from lxml import etree

base_url = 'https://www.qd8.com/changecity.php'     # 各个地区的链接
cates = [
    {"cate_name": "公司注册", 'cate_url': 'gongsizhuce/'},
    {"cate_name": "商标", 'cate_url': 'shangbiao/'}
]


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
    all_cities = html.xpath('//dl[@id="clist"]/div/dd/a')
    for city in all_cities:
        # 城市名称
        local = city.xpath('./text()')[0]
        # 城市的链接
        city_url = city.xpath('./@href')[0]
        for cate in cates:
            # 创建字典
            dd = dict()
            # 类别名称
            cate_name = cate.get('cate_name')
            # 类别的链接
            cate_url = cate.get('cate_url')
            # 完整的URL
            url = urljoin(city_url, cate_url)
            # 字典中增添值
            dd['local'] = local
            dd['cate_name'] = cate_name
            dd['url'] = url
            # 写入文件
            record_result(dd)


def record_result(data):
    """
    将结果写入文件
    :param data:
    :return:
    """
    path = r'G:\工作\APP\wandoujia\QiDian8_city.json'
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
