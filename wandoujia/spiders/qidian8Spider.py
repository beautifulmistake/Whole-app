import json
import scrapy
from wandoujia.items import QiDianBaItem


class QiDian8Spider(scrapy.Spider):
    name = "QiDianBa"

    def start_requests(self):
        """
        读取QiDian8_city.json文件生成所有的url
        :return:
        """
        with open(r"G:\工作\APP\wandoujia\QiDian8_city.json", 'r', encoding='utf-8') as f:
            data = f.readlines()
        # 遍历数据列表
        for d in data[:1]:
            # json 转换为字典
            d = json.loads(d)
            # 每一项都是一个字典：local-->url
            local = d.get('local')
            cate_name = d.get('cate_name')
            url = d.get('url')
            # 发起请求
            yield scrapy.Request(url=url, meta={"local": local, "cate_name": cate_name})

    def parse(self, response):
        """
        解析获取的页面
        :param response:
        :return:
        """
        # print('查看获取的响应：', response.text)
        if response.status == 200:
            # 判断是否有结果
            result = response.xpath('//div[@class="totalpost"]/font/strong/text()').extract_first()
            # 判断是否有结果
            if result != "0":
                # 下一页
                is_next = response.xpath('//div[@class="pagination2"]/a[last()]/text()').extract_first()
                # 获取详情页的链接
                detail_urls = response.xpath('//div[@class="section"]/ul/div/a')
                for detail_url in detail_urls[:1]:
                    # 详情页的链接
                    url = detail_url.xpath('./@href').extract_first()
                    # 请求详情页
                    yield scrapy.Request(url=url, meta=response.meta, callback=self.parse_detail)
                # 判断是否有下一页
                if is_next == "下一页>":
                    # 获取下一页的连接
                    next_url = response.xpath('//div[@class="pagination2"]/a[last()]/@href').extract_first()
                    # 发起下一页的请求
                    yield scrapy.Request(url=next_url, meta=response.meta, callback=self.parse)

    def parse_detail(self, response):
        """
        解析详情页
        :param response:
        :return:
        """
        # print("查看获取的响应：", response.text)
        # 创建item
        item = QiDianBaItem()
        # 搜索地区
        local = response.meta['local']
        # 搜索类别
        cate_name = response.meta['cate_name']
        # 搜索标题
        search_title = response.xpath('//div[@class="information_title"][1]/'
                                      'a/span/descendant-or-self::text()').extract_first()
        # 所属区域
        sub_local = response.xpath('//div[@class="extra"]/ul/li/descendant-or-self::text()').extract()
        # 联系人信息列表
        info_list = response.xpath('//div[@class="contact"]/ul/li')
        # 创建列表存储联系人的相关信息
        data = list()
        for info in info_list:
            value = info.xpath('./descendant-or-self::text()').extract()
            # 获取的为列表形式
            result = "".join([x for x in value if x != ' '])
            data.append(result)
        item['local'] = local
        item['cate_name'] = cate_name
        item['search_title'] = search_title if search_title else "暂无"
        item['sub_local'] = "".join(sub_local)
        item['info'] = "\t".join(data)
        yield item

