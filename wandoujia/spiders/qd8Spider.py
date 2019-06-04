import json
from urllib.parse import urljoin

import scrapy

from wandoujia.items import KuaiDian8


class KuaiDianBaSpider(scrapy.Spider):
    name = "Qd8"

    def start_requests(self):
        """
        读取文件获取初始url
        :return:
        """
        with open(r'G:\工作\APP\wandoujia\start_urls.json', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for line in lines:
            # 将json转换为字典
            data = json.loads(line)
            # 获取地区
            location = data.get('location')
            # 获取当前的类别
            cate_name = data.get('cate_name')
            # 获取链接
            start_url = data.get('start_url')
            # 发起请求
            yield scrapy.Request(url=start_url, meta={'location': location, 'cate_name': cate_name})

    def parse(self, response):
        """
        解析页面获取详情页的看链接
        :param response:
        :return:
        """
        # 下一页
        is_next = response.xpath('//div[@class="paginator"]/a[last()-2]/text()').extract_first()
        # 获取详情页的链接
        detail_urls = response.xpath('//div[@id="xinxilist"]//div/table/tr/td/a[1]/@href').extract()
        # 按 “/” 切分
        curr = "/".join(response.url.split("/")[:3])
        # 请求详情页数据
        for detail_url in detail_urls:
            if "tuiguang" not in detail_url:
                # 获取完整的url
                url = urljoin(curr, detail_url)
                # 推广类的网站过滤掉
                yield scrapy.Request(url=url, meta=response.meta, callback=self.parse_detail)

        if is_next == "下一页":
            # 获取属性值
            next_url = response.xpath('//div[@class="paginator"]/a[last()-2]/@href').extract_first()
            # 完整的url
            url = urljoin(curr, next_url)
            yield scrapy.Request(url, meta=response.meta, callback=self.parse)

    def parse_detail(self, response):
        """
        解析详情页
        :param response:
        :return:
        """
        item = KuaiDian8()
        # 获取第一个div
        base_list = response.xpath('//div[@id="baselist"]/ul/li/descendant-or-self::text()').extract()
        # 获取第二个div
        fbuser = response.xpath('//div[@id="fbuser"]/div/ul/li/descendant-or-self::text()').extract()
        # 搜索标题
        search_title = response.xpath('//div[@id="fangwu_view_title"]/h1/text()').extract_first()
        # 将两个列表合并
        result = " ".join(base_list + fbuser)
        item['search_title'] = search_title
        item['info'] = result
        yield item
