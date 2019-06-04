import json
from urllib.parse import urljoin

import requests


# 小米商城首页
from lxml import etree

base_url = "http://app.mi.com/"


def get_cate():
    """
    获取小米应用商城所有软件分类信息
    :return:
    """
    # 创建空列表
    data = list()
    # 发起请求
    result = requests.get(base_url)
    # 获取HTML
    html = parse_response(result)
    # 解析获取二级分类的名称和链接
    cates = html.xpath('//div/ul[@class="category-list"]/li')
    for cate in cates:
        # 创建字典
        dd = dict()
        # 获取二级分类的名称
        cate_name = cate.xpath('./a/text()')[0]
        # 获取二级分类的链接
        cate_url = urljoin(base_url, cate.xpath('./a/@href')[0])
        # 字典中添加键值对儿
        dd['cate_name'] = cate_name
        dd['cate_url'] = cate_url
        # 更新到列表中
        data.append(dd)
    # 将结果写入文件
    record_result(data)


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


def record_result(data):
    """
    将结果写入文件
    :param data:
    :return:
    """
    path = r'G:\工作\APP\wandoujia\xiaomi_process.json'
    with open(path, 'a+', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


# 测试代码
if __name__ == "__main__":
    get_cate()