import json
from urllib.parse import urljoin
import requests
from lxml import etree

# 构造二级分类的url
base_url = "http://app.hicloud.com"
# 一级目录
cates = [
    {"cate_name": "软件", "url": "http://app.hicloud.com/soft/list"},
    {"cate_name": "游戏", "url": "http://app.hicloud.com/game/list"}
]
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
}


def get_first_category():
    """
    获取360手机助手网站的二级分类信息
    :return:
    """
    # 创建空字典，存储分类结果
    data = list()
    for cate in cates:
        # 分类url
        url = cate['url']
        # 软件分类名称
        cate_name = cate['cate_name']
        # 发起请求
        result = requests.get(url, headers=headers)
        # 获取HTML
        html = parse_response(result)
        # 解析HTML，获取二级分类
        categories = html.xpath('//div[@class="head-keys"]/p/span/a')
        for category in categories:
            # 创建字典，存储三级目录信息
            dd = dict()
            # 获取二级分类的名称
            category_name = category.xpath('./text()')[0]
            # 获取二级分类的链接
            category_url = urljoin(base_url, category.xpath('./@href')[0])
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
    path = r'G:\工作\APP\wandoujia\huawei_category_url.json'
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