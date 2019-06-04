import json
import requests
import scrapy
from lxml import etree
from wandoujia.items import JuHeBangItem


class JuHeBangSpider(scrapy.Spider):
    name = "JuHeBang"

    @staticmethod
    def parse_response(res):
        """
        将获取的响应转换为HTML
        :param res: 响应（text）
        :return: HTML
        """
        try:
            if res.status_code == 200:
                res.encoding = res.apparent_encoding
                return etree.HTML(res.text, etree.HTMLParser())
            else:
                print("响应的状态码不是200")
                return False
        except Exception as e:
            print(e)

    @staticmethod
    def get_phone(url):
        """
        请求url,从中解析出手机号码
        :return:
        """
        # 请求页面
        result = requests.get(url)
        # 转换成HTML
        html = JuHeBangSpider.parse_response(result)
        # 解析出手机号码
        phone = html.xpath('//div[@class="number"]/span[1]/text()')[0]
        return phone

    def start_requests(self):
        """
        读去jhb_city.json文件生成所有的url
        :return:
        """
        with open(r"G:\工作\APP\wandoujia\jhb_city.json", 'r', encoding='utf-8') as f:
            data = f.readlines()
        # 遍历数据列表
        for d in data:
            # json 转换位字典
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
            result = response.xpath('//div[@class="listhdcenter"]/span/text()').extract_first()
            # 判断是否有结果
            if result != "0":
                # 下一页
                is_next = response.xpath('//div[@class="pagination2"]/a[last()]/text()').extract_first()
                # 获取详情页的链接
                detail_urls = response.xpath('//ul[@id="SB"]/div/a')
                for detail_url in detail_urls:
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
        # 创建item
        item = JuHeBangItem()
        # 搜索地区
        local = response.meta['local']
        # 搜索的类别
        cate_name = response.meta['cate_name']
        # 手机号码,先获取 onclick 属性，从中匹配出链接
        onclick_ = response.xpath('//ul[@class="contacter"]/li/a/@onclick').extract_first()
        # 调用函数，去请求该连接，解析手机号码
        phone_url = onclick_.split(",")[3][1:-2]
        phone = JuHeBangSpider.get_phone(phone_url)
        # 搜索标题
        search_title = response.xpath('//div[@class="information_hd "]/ul/h1/text()').extract_first()
        # 地址
        address = response.xpath('//div[@class="contact"]/ul/li/descendant-or-self::text()').extract()
        # 联系方式的列表
        contacter_list = response.xpath('//ul[@class="contacter"]/li')
        # 创建一个字典存储信息
        info = dict()
        # 创建一个列表
        pic_url = list()
        for contacter in contacter_list:
            print("查看li", contacter)
            # 获取title
            title = contacter.xpath('./span/text()').extract_first()
            # 判断title的值
            if "联系人" in title:
                text = contacter.xpath('./font/text()').extract_first()
                info[title] = text
            else:
                text = contacter.xpath('./font/img/@src').extract_first()
                info[title] = text
                # 添加到图片下载的字段中
                pic_url.append(text)
        item['local'] = local if local else "暂无"
        item['cate_name'] = cate_name if cate_name else "暂无"
        item['search_title'] = search_title if search_title else "暂无"
        item['address'] = " ".join(address) if address else "暂无"
        item['contact_info'] = info if info else "暂无"
        item['phone'] = phone
        item['image_urls'] = pic_url
        yield item



