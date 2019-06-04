import json
from urllib.parse import urljoin
import scrapy
from wandoujia.items import JinTiItem


class JinTiSpider(scrapy.Spider):
    name = "JinTi"

    def start_requests(self):
        """
        读去all_city.json文件生成所有的url
        :return:
        """
        with open(r"G:\工作\APP\wandoujia\all_city.json", 'r', encoding='utf-8') as f:
            data = f.readlines()
        # 遍历数据列表
        for d in data[:1]:
            # json 转换位字典
            d = json.loads(d)
            # 每一项都是一个字典：local-->url
            local = d.get('local')
            url = d.get('url')
            # 发起请求
            yield scrapy.Request(url=url, meta={"local": local})

    def parse(self, response):
        """
        解析获取的页面
        :param response:
        :return:
        """
        # print('查看获取的响应：', response.text)
        # 获取当前的URL
        curr_url = '/'.join(response.url.split('/')[:-2])
        # 当前抓取的地区
        local = response.meta['local']
        # 获取下一页的链接
        is_next = response.xpath('//div[@id="PalCtrl"]/table/tr/td/a[last()]/text()').extract_first()
        print('查看是否有下一页：', is_next)
        # 解析列表页，获取详情页的链接
        detail_urls = response.xpath('//div[@class="liebiao"]/div[@class="fw_group"]/div[2]/div[1]/h2/a')
        for detail_url in detail_urls:
            # 搜索标题
            search_title = detail_url.xpath('./text()').extract_first()
            # 详情页链接
            url = detail_url.xpath('./@href').extract_first()
            #
            yield scrapy.Request(url=urljoin(curr_url, url), meta={'local': local, 'search_title': search_title},
                                 callback=self.parse_detail)
        if is_next == "下一页":
            print("采集下一页中")
            # 获取下一页的链接
            url = response.xpath('//div[@id="PalCtrl"]/table/tr/td/a[last()]/@href').extract_first()
            # 请求下一页
            yield scrapy.Request(url=url, meta=response.meta, callback=self.parse)

    def parse_detail(self, response):
        """
        解析详情页，获取目标字段
        :param response:
        :return:
        """
        # print("查看获取的响应：", response.text)
        # 创建item
        item = JinTiItem()
        # 搜索地区
        local = response.meta['local']
        # 搜索标题
        search_title = response.meta['search_title']
        # 信息的列表
        info_list = response.xpath('//div[@class="p_list907"]/p')
        # 创建两个列表
        title = list()
        text = list()
        for info in info_list:
            # 判断标签的内容
            title_ = info.xpath('./span[@class="gongsi907"]/text()').extract_first()
            title.append(title_)
            if "电话" in title_:
                text_ = info.xpath('./span[3]/a/@onclick').extract_first()[9:-3].strip()
                text.append(text_)
            else:
                text_ = info.xpath('./text()|./span[2]/descendant-or-self::text()').extract_first().strip()
                text.append(text_)
        data = dict(zip(title, text))
        # 添加数据
        item['local'] = local
        item['search_title'] = search_title
        item['info'] = data
        yield item




