import json
import requests
from lxml import etree

cates = [
    {"cate_name": "软件分类", "url": "https://www.wandoujia.com/category/app"},
    {"cate_name": "游戏分类", "url": "https://www.wandoujia.com/category/game"}
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
        categories = html.xpath('//div[@class="container"]/ul/li[@class="parent-cate"]')
        for category in categories:
            # 获取二级分类的名称
            category_name = category.xpath('./a/text()')[0]
            # 获取三级分类的列表
            sub_category_list = category.xpath('./div/a')
            # 获取三级分类的名称和url
            for sub_category in sub_category_list:
                # 创建字典存储结果
                dd = dict()
                # 三级分类的名称
                sub_category_name = sub_category.xpath('./text()')[0]
                # 三级分类的url
                url = sub_category.xpath('./@href')[0]
                # 向字典中添加键值对儿
                dd['cate_name'] = cate_name
                dd['category_name'] = category_name
                dd['sun_category_name'] = sub_category_name
                dd['url'] = url
                data.append(dd)
    # 将结果写入文件
    record_result(data)


def record_result(data):
    """
    将结果写入文件
    :param data:
    :return:
    """
    path = r'G:\工作\APP\wandoujia\process.json'
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
