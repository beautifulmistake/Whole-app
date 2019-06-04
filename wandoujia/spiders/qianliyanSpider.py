from urllib.parse import urljoin
import scrapy

from wandoujia.items import QianLiYanItem


class QianLiYanSpider(scrapy.Spider):
    name = "QianLiYan"

    def start_requests(self):
        """
        读取文件获取初始url
        :return:
        """
        with open(r'G:\工作\APP\wandoujia\urls.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for url in lines[:1]:
            # 发起请求
            yield scrapy.Request(url=url.strip())

    def parse(self, response):
        """
        解析页面获取详情页的看链接
        :param response:
        :return:
        """
        # 当前的url
        curr_url = response.url
        # 获取拼接前的url
        base = "/".join(curr_url.split("/")[:3])
        # 获取详情页的列表
        detail_urls = response.xpath('//div[@id="main"]/table[@id="category_table"]/'
                                     'tbody/tr/td[2]/div/a/@href').extract()
        # 下一页
        is_next = response.xpath('//table[@id="category_table"]/tfoot//a[last()]/text()').extract_first()
        # 请求详情页
        for detail_url in detail_urls:
            url = urljoin(base, detail_url)
            print("查看获取的url:", url)
            yield scrapy.Request(url=url, callback=self.parse_detail)
        if is_next == "下一页":
            # 获得下一页的链接
            next = response.xpath('//table[@id="category_table"]/tfoot//a[last()]/@href').extract_first()
            yield scrapy.Request(url=urljoin(base, next), callback=self.parse)

    def parse_detail(self, response):
        """
        解析详情页
        :param response:
        :return:
        """
        # 创建item
        item = QianLiYanItem()
        # 搜索标题
        search_title = response.xpath('//div[@id="main"]/div/article/h1/text()').extract_first()
        # 服务区域,------>列表
        service_area = response.xpath('//div[@id="main"]/div/article/section[1]'
                                      '/ul/li[1]/descendant-or-self::text()').extract()
        # 联系人,------>列表
        contact = response.xpath('//div[@id="main"]/div/article/section[1]'
                                 '/ul/li[2]/descendant-or-self::text()').extract()
        # 联系人手机（图片）
        image_urls = response.xpath('//div[@id="main"]/div/article/section[1]'
                                    '/ul/li[3]/span[2]/img/@src').extract_first()
        # 联系人QQ
        contact_qq = response.xpath('//div[@id="main"]/div/article/section[1]'
                                    '/ul/li[4]/descendant-or-self::text()').extract()
        # 联系人邮箱
        contact_email = response.xpath('//div[@id="main"]/div/article/section[1]'
                                       '/ul/li[5]/descendant-or-self::text()').extract()
        item['search_title'] = search_title
        item['service_area'] = service_area
        item['contact'] = contact
        item['image_urls'] = image_urls
        item['contact_qq'] = contact_qq
        item['contact_email'] = contact_email
        yield item
