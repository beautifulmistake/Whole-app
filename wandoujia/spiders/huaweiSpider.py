import json
from urllib.parse import urljoin

import scrapy

from wandoujia.items import HuaWei


class HuaWeiSpider(scrapy.Spider):
    name = "HuaWei"
    base_url = "http://app.hicloud.com"
    # 小分类：综合---->更新时间
    ranking_List = {
        "综合": '_2_{}',
        "总榜": '_1_{}',
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
        'Cookie': 'cs6k_langid=zh_cn; agreed-huawei-cookiepolicy=1'
    }

    def start_requests(self):
        """
        读取文件获取初始请求
        :return:
        """
        with open(r"G:\工作\APP\wandoujia\huawei_category_url.json", 'r', encoding='utf-8') as f:
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
                url = category_url + value.format(str(1))
                print("查看请求的url：", url)
                yield scrapy.Request(
                    url=url, headers=self.headers,
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
            datas = response.xpath('//div[@class="unit-main"]/div/div[2]')
            # 是否有下一页
            is_next = response.xpath('//div[@id="appListPage"]/script/text()').extract_first()
            for data in datas:
                # 创建字典
                dd = dict()
                # APP名称
                app_name = data.xpath('./h4/a/text()').extract_first()
                # APP 详情页链接 /h4/a/@href
                app_url = urljoin(self.base_url, data.xpath('./h4/a/@href').extract_first())
                # 向字典中更搜索的结果
                dd['cate_name'] = cate_name
                dd['category_name'] = category_name
                dd['app_name'] = app_name
                dd['app_url'] = app_url
                # 将搜索结果写入文件
                self.record(dd)
                # 请求详情页
                yield scrapy.Request(url=app_url, meta={'cate_name': cate_name, 'category_name': category_name,
                                                        'current_url': app_url}, headers=self.headers,
                                     callback=self.parse_detail)
            if is_next:
                # 将结果做切片处理
                result = is_next.split(",")[1:5]
                # 获取当前页号
                curr_page = int(result[0].strip())
                # 获取总数据数
                total = int(result[1].strip())
                # 每一页展示的条数
                num = int(result[2].strip())
                # 计算总页数
                page = total//num + 1 if total % num else total//num
                # 获取需要拼接的url
                url = result[-1].strip()[1:-3]
                print("查看要拼接的url:", url, type(url))
                if curr_page < page:
                    url = "http:" + url + str(curr_page + 1)
                    yield scrapy.Request(url=url, meta={'cate_name': cate_name,
                                                        'category_name': category_name, 'current_url': url},
                                         headers=self.headers, callback=self.parse)

    def parse_detail(self, response):
        """
        解析详情页的数据
        :param response:
        :return:
        """
        if response.status == 200:
            # 创建item对象
            item = HuaWei()
            # APP 名称
            app_name = response.xpath('//div[@class="app-info flt"]/ul[1]/li[2]/p[1]/'
                                      'span[@class="title"]/text()').extract_first()
            # APP 基本信息
            app_info = response.xpath('//div[@class="app-info flt"]/ul[2]/li/descendant-or-self::text()').extract()
            # APP 应用介绍
            app_desc = response.xpath('//div[@id="app_strdesc"]/descendant-or-self::text()').extract()
            # APP 下载量
            app_downloads = response.xpath('//div[@class="app-info flt"]/ul[1]/li[2]/p[1]/'
                                           'span[2]/text()').extract_first()
            item['app_name'] = app_name
            item['app_desc'] = app_desc
            item['app_info'] = app_info
            item['app_downloads'] = app_downloads
            item['cate_name'] = response.meta['cate_name']
            item['category_name'] = response.meta['category_name']
            yield item

    def record(self, data):
        """
        将二级分类的列表信息写入文件:字典转json
        :param data:
        :return:
        """
        with open(r'G:\工作\APP\wandoujia\huawei_info.json', 'a+', encoding="utf-8") as f:
            # 将字典的数据转为json
            result = json.dumps(data, ensure_ascii=False)
            # 将结果写入文件
            f.write(result + "\n")
