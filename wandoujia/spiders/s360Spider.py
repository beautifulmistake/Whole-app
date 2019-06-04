import json
from urllib.parse import urljoin

import scrapy

from wandoujia.items import SanLiuLing


class SanLiuLingSpider(scrapy.Spider):
    name = "SanLiuLing"
    base_url = "http://zhushou.360.cn"
    ranking_List = {
        "最新": '/order/newest/?page={}',
        "综合": '/weekdownload/?page={}',
        "总榜": '/order/download/?page={}',
        "好评": '/order/poll/?page={}'
    }

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
            # 为保证抓取的全面性，排行榜四个小区域也一起抓取
            for value in list(self.ranking_List.values()):
                print("查看获取的value:", value)
                # 去掉最后 /----> 在此使用urljoin时并不能拼接获取有效的url
                url = category_url[:-1] + value.format(str(1))
                print("查看请求的url：", url)
                yield scrapy.Request(
                    url=url,
                    meta={'cate_name': cate_name, 'category_name': category_name, 'page': 1, 'current_url': url})

    def parse(self, response):
        """
        获取详情页链接
        :param response:
        :return:
        """
        if response.status == 200:
            print("查看获取的响应：", response.text)
            cate_name = response.meta['cate_name']
            # 二级分类名称
            category_name = response.meta['category_name']
            # 搜索结果的列表
            datas = response.xpath('//ul[@id="iconList"]/li/h3/a')
            # 当前的页号
            page = response.meta['page']
            # 获取当前的url
            curr_url = response.url
            for data in datas:
                # 创建字典
                dd = dict()
                # APP名称
                app_name = data.xpath('./text()').extract_first()
                # APP 详情页链接
                app_url = urljoin(self.base_url, data.xpath('./@href').extract_first())
                # 向字典中更搜索的结果
                dd['cate_name'] = cate_name
                dd['category_name'] = category_name
                dd['app_name'] = app_name
                dd['app_url'] = app_url
                # 将搜索结果写入文件
                self.record(dd)
                # 请求详情页
                yield scrapy.Request(url=app_url, meta={'cate_name': cate_name, 'category_name': category_name,
                                                        'page': page, 'current_url': app_url},
                                     callback=self.parse_detail)
            # 判断是否有下一页
            if page <= 50:
                print("进入判断是否有下一页的请求中")
                # 将当前的url做分片
                url = curr_url.split("=")[0]
                # 将当前的页号自增
                page += 1
                # 请求下一页
                yield scrapy.Request(url=url+"="+str(page), meta={'cate_name': cate_name, 'category_name': category_name,
                                                                  'page': page, 'current_url': url+"="+str(page)},
                                     callback=self.parse)

    def parse_detail(self, response):
        """
        解析详情页的数据
        :param response:
        :return:
        """
        if response.status == 200:
            # 创建item对象
            item = SanLiuLing()
            # APP 名称
            app_name = response.xpath('//div[@id="app-info-panel"]//h2[@id="app-name"]/span/text()').extract_first()
            # APP 应用介绍
            app_desc = response.xpath('//div[@id="sdesc"]/div[@class="breif"]/text()').extract_first()
            # APP 基本信息
            app_info = response.xpath('//div[@id="sdesc"]/div[@class="breif"]/div[@class="base-info"]'
                                      '/table/tbody/tr/td/descendant-or-self::text()').extract()
            item['app_name'] = app_name
            item['app_desc'] = app_desc
            item['app_info'] = app_info
            item['cate_name'] = response.meta['cate_name']
            item['category_name'] = response.meta['category_name']
            yield item

    def record(self, data):
        """
        将二级分类的列表信息写入文件:字典转json
        :param data:
        :return:
        """
        with open(r'G:\工作\APP\wandoujia\SanLiuLing_info.json', 'a+', encoding="utf-8") as f:
            # 将字典的数据转为json
            result = json.dumps(data, ensure_ascii=False)
            # 将结果写入文件
            f.write(result + "\n")
