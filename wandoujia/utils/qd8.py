import json
from urllib.parse import urljoin
import requests
from lxml import etree

# 所有地区的url
base_url = "http://www.qd8.com.cn/index.html"
# 二级类别
cates = [
    {"cate_name": "工商注册", "url": "/zhuce/"},
    {"cate_name": "商标专利", "url": "/shangbiaozhuanli/"}
]


def get_first_category():
    """
    获取快点8网站的各地区名称和链接
    :return:
    """
    # 发起请求进入主页面
    result = requests.get(base_url)
    # 获取HTML
    html = parse_response(result)
    # 解析HTML获取所有地区的名称和链接
    local_lists = html.xpath('//td[@class="citycontent"]/div/span/a')
    for local_list in local_lists:
        # 创建字典存储地区信息
        dd = dict()
        # 获取每一个地区的名称
        location = local_list.xpath('./descendant-or-self::text()')[0]
        # 获取每一个地区的链接
        local_url = local_list.xpath('./@href')[0]
        # 向字典中添加数据
        dd['location'] = location
        dd['local_url'] = local_url
        # 将结果写入文件
        record_result(dd)


def record_result(data):
    """
    将结果写入文件
    :param data:
    :return:
    """
    path = r'G:\工作\APP\wandoujia\start_urls.json'
    with open(path, 'a+', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def get_start_requests(path):
    """
    读取文件，拼接获取每个地区的两个类别链接
    :param path:
    :return:
    """
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # 遍历所有的地区
        for line in lines:
            # 每一条是json,转换为字典
            dict_ = json.loads(line)
            # 获取当前的地区
            location = dict_.get('location')
            # 获取当前的链接
            local_url = dict_.get('local_url')
            for cate_ in cates:
                # 创建字典
                data = dict()
                # 获取当前的类别
                cate = cate_.get('cate_name')
                # 获取当前的类别链接
                cate_url = cate_.get('url')
                # 向字典中增添值
                data['location'] = location
                data['cate_name'] = cate
                data['start_url'] = urljoin(local_url, cate_url)
                # 将字典写入文件
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


# 测试代码
if __name__ == "__main__":
    # get_first_category()
    get_start_requests(r'G:\工作\APP\wandoujia\local_url.json')
