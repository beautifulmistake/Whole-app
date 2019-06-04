import json
from urllib.parse import urljoin

import requests


# 小米商城首页
from lxml import etree

# 构造二级分类的url
base_url = "https://sj.qq.com/myapp/category.htm"
# 一级目录
cates = [
    {"cate_name": "应用", "url": "https://sj.qq.com/myapp/category.htm?orgame=1"},
    {"cate_name": "游戏", "url": "https://sj.qq.com/myapp/category.htm?orgame=2"}
]


def get_first_category():
    """
    获取豌豆荚网站的软件分类信息
    :return:
    """
    # 创建空字典，存储分类结果
    data = list()
    for cate in cates:
        # 软件分类
        url = cate['url']
        # 软件分类名称
        cate_name = cate['cate_name']
        # 发起请求
        result = requests.get(url)
        # 获取HTML
        html = parse_response(result)
        # 解析HTML，获取二级分类
        categories = html.xpath('//ul[@class="menu-junior"]/li')
        for category in categories:
            # 创建字典，存储三级目录信息
            dd = dict()
            if category.xpath('./a/text()') in [['全部软件'], ['展开更多'], [], ['全部游戏']]:
                continue
            # 获取二级分类的名称
            category_name = category.xpath('./a/text()')[0]
            # 获取二级分类的链接
            category_url = urljoin(base_url, category.xpath('./a/@href')[0])
            print("查看：", category_name, category_url)
            # 向字典中添加数据
            dd['cate_name'] = cate_name
            dd['category_name'] = category_name
            dd['category_url'] = category_url
            # 将结果添加至列表中
            data.append(dd)
    # 将结果写入文件
    record_result(data)


def record_result(data):
    """
    将结果写入文件
    :param data:
    :return:
    """
    path = r'G:\工作\APP\wandoujia\category_url.json'
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
    get_first_category()