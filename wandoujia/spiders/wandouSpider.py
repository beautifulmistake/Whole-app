import json
import re
import scrapy
from wandoujia.items import WandoujiaItem


class WanDouSpider(scrapy.Spider):
    name = "wandou"
    # 加载动态数据的url
    load_url = 'https://www.wandoujia.com/wdjweb/api/category/' \
               'more?catId={0}&subCatId={1}&page={2}&ctoken=m_9FPY0s86YJwhUKEjhLpetz'
    # 正则匹配详情页的链接
    detail_pattern = re.compile(r'href="(.*?)"')
    # 替换下一页的页号
    page_pattern = re.compile(r'page=(\d*)')

    def start_requests(self):
        """
        读取文件生成初始urls
        :return:
        """
        with open(r"G:\工作\APP\wandoujia\process.json", 'r', encoding='utf-8') as f:
            data = json.loads(f.read(), encoding="utf-8")
        # 遍历数据列表
        for d in data:
            # 每一项都是一个字典：cate_name-->category_name-->sun_category_name-->url
            cate_name = d.get('cate_name')
            category_name = d.get('category_name')
            sun_category_name = d.get('sun_category_name')
            url = d.get('url').split("category/")
            catId = url[1].split("_")[0]
            subCatId = url[1].split("_")[1]
            # 判断是否存在
            yield scrapy.Request(
                url=self.load_url.format(catId, subCatId, str(1)),
                meta={'cate_name': cate_name, 'category_name': category_name, 'sun_category_name': sun_category_name})

    def parse(self, response):
        """
        获取三级目录的列表页
        :param response:
        :return:
        """
        set_ = set()
        res = json.loads(response.text, encoding="utf-8")
        # 获取内容
        data = res.get("data")
        # 获取当前的页号
        currPage = data.get("currPage")
        # 获取包含详情页链接的标签,获取的是字符串形式
        content = data.get("content")
        detail_urls = self.detail_pattern.findall(content)
        # print(detail_urls)
        for detail_url in detail_urls:
            # 暂时先使用判断语句，后期使用正则精准匹配
            if "apps" in detail_url:
                if detail_url not in set_:
                    set_.add(detail_url)
                    yield scrapy.Request(url=detail_url, meta=response.meta, callback=self.parse_detail)
        # 判断页号
        if currPage != -1:
            # 还有下一页的
            curr_url = response.url
            print("查看当前的url:", curr_url)
            next_url = re.sub(self.page_pattern, 'page=%s' % (str(currPage+1)), curr_url)
            print("查看下一页的链接", next_url)
            yield scrapy.Request(url=next_url, meta=response.meta, callback=self.parse)

    def parse_detail(self, response):
        default_value = "暂无"
        if response.status == 200:
            # 创建item对象
            item = WandoujiaItem()
            # APP名称
            app_name = response.xpath('//div[@class="app-info"]/p[@class="app-name"]/span/text()').extract_first()
            print("查看获取的APP名称：", app_name)
            # APP 描述
            app_desc = response.xpath('//div[@class="desc-info"]/div[@class="con"]/div[1]/text()').extract_first()
            # 发布时间
            publish_time = response.xpath(
                '//div[@class="num-list"]/span[@class="verified-info"]/span/text()').extract_first()
            print("查看获取的APP发布时间：", publish_time)
            # 开发者
            author = response.xpath('//div[@class="infos"]/dl/dd[5]/span/text()').extract_first()
            print("查看获取的APP作者：", author)
            # 下载次数
            userDownloads = response.xpath(
                '//div[@class="num-list"]/div[@class="app-info-data"]/span/i/text()').extract_first()
            print("查看获取的APP用户下载量：", userDownloads)
            # APP图片地址
            img_url = response.xpath('//div[@class="app-icon"]/img/@src').extract_first()
            print("查看获取的APP图片地址：", img_url)
            # APP详情页链接
            detail_page = response.url
            print("查看获取的APP详情页链接：", detail_page)
            # APP分类
            category = response.xpath('//div[@class="infos"]/dl/dd[2]/a/text()').extract()
            print("查看获取的APP种类：", category)
            # APP大小
            file_size = response.xpath('//div[@class="infos"]/dl/dd[1]/text()').extract_first()
            print("查看获取的APP大小：", file_size)
            # 版本号,需要去掉空格
            version = response.xpath('//div[@class="infos"]/dl/dd[3]/text()').extract_first()
            print("查看获取的APP版本号：", version)
            # 用户好评
            item_love = response.xpath(
                '//div[@class="num-list"]/div[@class="app-info-data"]/span[@class="item love"]/i/text()').extract_first()
            print("查看用户好评度：", item_love)
            # APP评论
            comment_num = response.xpath(
                '//div[@class="num-list"]/div[@class="app-info-data"]/a/i/text()').extract_first()
            print("查看APP评论数：", comment_num)
            # 判断是否为空，不为空则赋值
            item['app_name'] = app_name if app_name else default_value  # APP名称
            item['app_desc'] = "".join((app_desc.split())) if app_desc else default_value  # APP描述
            item['publish_time'] = '-'.join(
                (publish_time[-10:]).split("/")) if publish_time else default_value  # APP上线时间
            item['author'] = author if author else default_value  # APP开发者
            item['userDownloads'] = userDownloads if userDownloads else default_value  # APP下载量
            item['img_url'] = img_url if img_url else default_value  # APP图片
            item['detail_page'] = detail_page if detail_page else default_value  # APP详情页
            item['category'] = ' '.join(category) if category else default_value  # 两个种类时需要将列表项拼接在一起
            item['file_size'] = file_size if file_size else default_value  # APP大小
            item['version'] = version.strip() if version else default_value  # APP版本
            item['item_love'] = item_love if item_love else default_value  # APP评分
            item['comment_num'] = comment_num if comment_num else default_value  # APP评论数
            # APP 一级分类
            item['app_cate'] = response.meta['cate_name']
            # APP 二级分类
            item['app_category'] = response.meta['category_name']
            # APP 三级分类
            item['app_sub_category'] = response.meta['sun_category_name']
            yield item