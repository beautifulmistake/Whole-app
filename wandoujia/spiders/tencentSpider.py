import json
import scrapy


class TencentSpider(scrapy.Spider):
    name = "tencent"
    # 请求数据的接口 orgame=2&categoryId=147 默认从零开始
    load_url = 'https://sj.qq.com/myapp/cate/appList.htm?{0}&pageSize=20&pageContext={1}'

    def start_requests(self):
        """
        读取文件获取初始请求
        :return:
        """
        with open(r"G:\工作\APP\wandoujia\category_url.json", 'r', encoding='utf-8') as f:
            data = json.loads(f.read(), encoding="utf-8")
        # 遍历数据列表
        for d in data:
            # 每一项都是一个字典：cate_name-->category_name-->category_url
            cate_name = d.get('cate_name')
            category_name = d.get('category_name')
            category_url = d.get('category_url')
            print("查看获取的category_url：", category_url)
            cateId = category_url.split("?")[1]
            print("查看切分后的cateId:", cateId)
            # 判断是否存在
            yield scrapy.Request(
                url=self.load_url.format(cateId, str(0)),
                meta={'cate_name': cate_name, 'category_name': category_name, 'cateId': cateId})

    def parse(self, response):
        """
        获取的响应为json数据
        :param response:
        :return:
        """
        if response.status == 200:
            # 获取当前搜索的APP类别
            cateId = response.meta['cateId']
            # 解析数据
            res = json.loads(response.text, encoding="utf-8")
            # 获取pageContext--->用于判断是否继续发送请求
            pageContext = res.get('pageContext')
            print(pageContext, type(pageContext))
            # 获取数据，为一个列表--字典
            datas = res.get('obj')
            if datas:
                for data in datas:
                    # 每一个data中包含该APP的所有信息，不用请求详情页数据了
                    self.record(data)
            # 判断是否有下一页的请求
            if pageContext:
                # 发起下一页的请求
                yield scrapy.Request(url=self.load_url.format(cateId, pageContext),
                                     meta=response.meta, callback=self.parse)

    def record(self, data):
        """
        将二级分类的列表信息写入文件:字典转json
        :param data:
        :return:
        """
        with open(r'G:\工作\APP\wandoujia\tecent_info.json', 'a+', encoding="utf-8") as f:
            # 将字典的数据转为json
            result = json.dumps(data, ensure_ascii=False)
            # 将结果写入文件
            f.write(result + "\n")
