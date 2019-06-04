import json
import re
import scrapy
from wandoujia.items import XiaoMiItem


class XiaoMiSpider(scrapy.Spider):
    name = "xiaomi"
    # 加载动态数据的接口 page:初始为0
    load_url = "http://app.mi.com/categotyAllListApi?page={0}&categoryId={1}&pageSize=30"
    # 替换下一页的页号
    page_pattern = re.compile(r'page=(\d*)')
    # 详情页的链接
    detail_url = "http://app.mi.com/details?id={}"

    def start_requests(self):
        """
        读取文件获取初始请求
        :return:
        """
        with open(r"G:\工作\APP\wandoujia\xiaomi_process.json", 'r', encoding='utf-8') as f:
            data = json.loads(f.read(), encoding="utf-8")
        # 遍历数据列表
        for d in data:
            # 每一项都是一个字典：cate_name-->cate_url
            cate_name = d.get('cate_name')
            cate_url = d.get('cate_url')
            cateId = cate_url.split("category/")[1]
            # 判断是否存在
            yield scrapy.Request(
                url=self.load_url.format(str(0), cateId),
                meta={'cate_name': cate_name, 'page': 0})

    def parse(self, response):
        """
        获取的为json数据
        :param response:
        :return:
        """
        if response.status == 200:
            cate_name = response.meta['cate_name']
            page = response.meta['page']
            print("查看meta信息：", cate_name, page, type(page))
            # 获取当前的url
            url = response.url
            res = json.loads(response.text, encoding="utf-8")
            # 获取内容：为列表
            datas = res.get("data")
            if datas:
                for data in datas:
                    # 每一项为字典:获取详情页链接
                    packageName = data.get('packageName')
                    # 将列表信息写入文件
                    self.record(data)
                    # 请求详情页的链接
                    yield scrapy.Request(url=self.detail_url.format(packageName), meta={'cate_name': cate_name, 'page': page},
                                         callback=self.parse_detail)
                next_url = re.sub(self.page_pattern, 'page=%s' % (str(page + 1)), url)
                # 请求下一页
                yield scrapy.Request(url=next_url, meta={'cate_name': cate_name, 'page': page+1}, callback=self.parse)

    def parse_detail(self, response):
        """
        解析详情页获取数据
        :param response:
        :return:
        """
        default_value = "暂无"
        if response.status == 200:
            # APP名称
            app_name = response.xpath('//div[@class="app-info"]/div[@class="intro-titles"]/h3/text()').extract_first()
            # APP 描述
            app_desc = response.xpath('//div[@class="app-text"]/p[@class="pslide"]/text()').extract_first()
            # APP发布时间
            app_publishTime = response.xpath(
                '//div[@class="look-detail"]/div[@class="details preventDefault"]/ul[1]/li[6]/text()').extract_first()
            # APP开发者
            app_author = response.xpath(
                '//div[@class="app-info"]/div[@class="intro-titles"]/p[1]/text()').extract_first()
            # APP下载量无
            # APP图片链接
            app_img = response.xpath('//div[@class="app-info"]/img/@src').extract_first()
            # APP详情页链接
            detail_page = response.url
            # APP所属分类
            app_category = response.xpath(
                '//div[@class="app-info"]/div[@class="intro-titles"]/p[2]/text()[1]').extract_first()
            # APP大小
            app_fileSize = response.xpath(
                '//div[@class="look-detail"]/div[@class="details preventDefault"]/ul[1]/li[2]/text()').extract_first()
            # APP版本号,需要拼接一个 V
            app_version = response.xpath(
                '//div[@class="look-detail"]/div[@class="details preventDefault"]/ul[1]/li[4]/text()').extract_first()
            # APP评分,需要按 - 切分然后取最后一个
            app_comment = response.xpath(
                '//div[@class="app-info"]/div[@class="intro-titles"]/'
                'div[@class="star1-empty"]/div/@class').extract_first()
            # APP评论数
            app_commentNum = response.xpath(
                '//div[@class="app-info"]/div[@class="intro-titles"]/'
                'span[@class="app-intro-comment"]/text()').extract_first()
            # 创建item
            item = XiaoMiItem()
            # 判断是否为空，不为空添加，为空赋默认值，否则丢失数据
            item['app_name'] = app_name if app_name else default_value  # APP名称
            item['app_desc'] = app_desc.strip() if app_desc else default_value  # APP描述
            item['app_publishTime'] = app_publishTime if app_publishTime else default_value  # APP上线时间
            item['app_author'] = app_author if app_author else default_value  # APP开发者
            item['app_downloads'] = default_value  # APP下载量，无
            item['app_img'] = app_img if app_img else default_value  # APP图片
            item['detail_page'] = detail_page  # APP详情页
            item['app_category'] = app_category if app_category else default_value  # APP种类
            item['app_fileSize'] = app_fileSize if app_fileSize else default_value  # APP大小
            item['app_version'] = "V" + " " + app_version if app_version else default_value  # APP版本
            item['app_comment'] = app_comment.split('-')[-1] if app_comment else default_value  # APP评分
            item['app_commentNum'] = app_commentNum[2:-1] if app_commentNum else default_value  # APP评论数
            item['cate_name'] = response.meta['cate_name']
            yield item

    def record(self, data):
        """
        将二级分类的列表信息写入文件:字典转json
        :param data:
        :return:
        """
        with open(r'G:\工作\APP\wandoujia\cate_info.json', 'a+', encoding="utf-8") as f:
            # 将字典的数据转为json
            result = json.dumps(data, ensure_ascii=False)
            # 将结果写入文件
            f.write(result + "\n")
